import AppKit
import CoreBluetooth
import Foundation
import Darwin

// Local BLE diagnostics; explicit command-directory mode enables requested controls.
final class BLEExplorer: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    private var central: CBCentralManager!
    private var peripherals: [UUID: CBPeripheral] = [:]
    private var advertisements: [UUID: [String: Any]] = [:]
    private var selected: CBPeripheral?
    private var started = false
    private var finished = false
    private var notificationCount = 0
    private let log: FileHandle
    private let target: String?
    private let scanSeconds: Double
    private let listenSeconds: Double
    private let commandDirectory: String?
    private var commandTimer: Timer?
    private var writeCharacteristic: CBCharacteristic?
    private var queuedWrites: [(Data, String)] = []
    private var writing = false
    private var processedCommands = Set<String>()
    private var followUps: [String: [String: Any]] = [:]

    init(output: String, socketPath: String?, target: String?, scanSeconds: Double, listenSeconds: Double, commandDirectory: String?) throws {
        self.target = target
        self.scanSeconds = scanSeconds
        self.listenSeconds = listenSeconds
        self.commandDirectory = commandDirectory
        if let socketPath {
            var address = sockaddr_un()
            address.sun_family = sa_family_t(AF_UNIX)
            address.sun_len = UInt8(MemoryLayout<sockaddr_un>.size)
            let pathBytes = Array(socketPath.utf8) + [UInt8(0)]
            guard pathBytes.count <= MemoryLayout.size(ofValue: address.sun_path) else {
                throw NSError(domain: "GrowBridge", code: 1)
            }
            withUnsafeMutableBytes(of: &address.sun_path) { destination in
                destination.copyBytes(from: pathBytes)
            }
            let descriptor = Darwin.socket(AF_UNIX, SOCK_STREAM, 0)
            guard descriptor >= 0 else { throw NSError(domain: "GrowBridge", code: 2) }
            let connected = withUnsafePointer(to: &address) { pointer in
                pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                    Darwin.connect(descriptor, $0, socklen_t(MemoryLayout<sockaddr_un>.size))
                }
            }
            guard connected == 0 else { Darwin.close(descriptor); throw NSError(domain: "GrowBridge", code: 3) }
            self.log = FileHandle(fileDescriptor: descriptor, closeOnDealloc: true)
        } else {
            FileManager.default.createFile(atPath: output, contents: nil, attributes: [.posixPermissions: 0o600])
            self.log = try FileHandle(forWritingTo: URL(fileURLWithPath: output))
        }
        super.init()
    }

    func start() {
        // Never replay files left by an earlier physical-device test session.
        if let commandDirectory {
            let existing = (try? FileManager.default.contentsOfDirectory(atPath: commandDirectory)) ?? []
            processedCommands.formUnion(existing.filter { $0.hasSuffix(".json") })
        }
        emit("start", ["target": target ?? "scan only", "scan_seconds": scanSeconds, "process_id": ProcessInfo.processInfo.processIdentifier])
        central = CBCentralManager(delegate: self, queue: .main)
        DispatchQueue.main.asyncAfter(deadline: .now() + 90 + scanSeconds) {
            if self.selected?.state != .connected { self.finish("startup_timeout", code: 2) }
        }
    }

    private func emit(_ event: String, _ fields: [String: Any] = [:]) {
        var record = fields
        record["event"] = event
        record["time"] = ISO8601DateFormatter().string(from: Date())
        if let data = try? JSONSerialization.data(withJSONObject: record, options: [.sortedKeys]) {
            log.write(data)
            log.write(Data([10]))
            try? log.synchronize()
        }
    }

    private func finish(_ reason: String, code: Int32 = 0) {
        guard !finished else { return }
        finished = true
        commandTimer?.invalidate()
        central.stopScan()
        if let selected { central.cancelPeripheralConnection(selected) }
        emit("complete", ["reason": reason, "devices_seen": advertisements.count,
                           "notifications": notificationCount])
        try? log.close()
        exit(code)
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        let names: [CBManagerState: String] = [.unknown: "unknown", .resetting: "resetting",
            .unsupported: "unsupported", .unauthorized: "unauthorized", .poweredOff: "powered_off",
            .poweredOn: "powered_on"]
        emit("bluetooth_state", ["state": names[central.state] ?? "unknown",
                                 "authorization": CBManager.authorization.rawValue])
        switch central.state {
        case .poweredOn:
            guard !started else { return }
            started = true
            central.scanForPeripherals(withServices: nil,
                options: [CBCentralManagerScanOptionAllowDuplicatesKey: true])
            emit("scanning")
            DispatchQueue.main.asyncAfter(deadline: .now() + scanSeconds) {
                guard self.selected == nil else { return }
                self.central.stopScan()
                for record in self.advertisements.values.sorted(by: {
                    ($0["rssi"] as? Int ?? -999) > ($1["rssi"] as? Int ?? -999)
                }) { self.emit("device", record) }
                self.finish(self.target == nil ? "scan_complete" : "target_not_found",
                            code: self.target == nil ? 0 : 3)
            }
        case .unauthorized: finish("bluetooth_permission_required", code: 4)
        case .poweredOff: finish("bluetooth_powered_off", code: 5)
        case .unsupported: finish("bluetooth_unsupported", code: 6)
        default: break
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral,
                        advertisementData: [String: Any], rssi RSSI: NSNumber) {
        let id = peripheral.identifier
        peripherals[id] = peripheral
        let name = advertisementData[CBAdvertisementDataLocalNameKey] as? String ?? peripheral.name ?? ""
        var record: [String: Any] = ["id": id.uuidString, "name": name, "rssi": RSSI.intValue,
            "connectable": (advertisementData[CBAdvertisementDataIsConnectable] as? NSNumber)?.boolValue ?? false,
            "services": (advertisementData[CBAdvertisementDataServiceUUIDsKey] as? [CBUUID] ?? []).map(\.uuidString)]
        if let manufacturer = advertisementData[CBAdvertisementDataManufacturerDataKey] as? Data {
            record["manufacturer_hex"] = manufacturer.map { String(format: "%02x", $0) }.joined()
        }
        advertisements[id] = record
        guard let target, selected == nil,
              id.uuidString.caseInsensitiveCompare(target) == .orderedSame || name.caseInsensitiveCompare(target) == .orderedSame
        else { return }
        selected = peripheral
        peripheral.delegate = self
        central.stopScan()
        emit("connecting", record)
        central.connect(peripheral)
        DispatchQueue.main.asyncAfter(deadline: .now() + 20) {
            if peripheral.state != .connected { self.finish("connection_timeout", code: 7) }
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        emit("connected", ["id": peripheral.identifier.uuidString, "name": peripheral.name ?? ""])
        peripheral.discoverServices(nil)
        if listenSeconds > 0 {
            DispatchQueue.main.asyncAfter(deadline: .now() + listenSeconds) {
                self.finish("inspection_complete")
            }
        }
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        emit("error", ["detail": error?.localizedDescription ?? "connection failed"])
        finish("connection_failed", code: 8)
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        emit("disconnected", ["detail": error?.localizedDescription ?? "remote disconnect"])
        finish("disconnected", code: 9)
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        if let error { emit("error", ["detail": error.localizedDescription]); return }
        for service in peripheral.services ?? [] {
            emit("service", ["uuid": service.uuid.uuidString])
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        if let error { emit("error", ["detail": error.localizedDescription]); return }
        let flags: [(CBCharacteristicProperties, String)] = [(.read, "read"), (.write, "write"),
            (.writeWithoutResponse, "write_without_response"), (.notify, "notify"), (.indicate, "indicate")]
        for characteristic in service.characteristics ?? [] {
            emit("characteristic", ["service": service.uuid.uuidString, "uuid": characteristic.uuid.uuidString,
                "properties": flags.filter { characteristic.properties.contains($0.0) }.map { $0.1 }])
            if characteristic.uuid == CBUUID(string: "FF01"),
               characteristic.properties.contains(.notify) || characteristic.properties.contains(.indicate) {
                peripheral.setNotifyValue(true, for: characteristic)
            }
            if characteristic.uuid == CBUUID(string: "FF02"), characteristic.properties.contains(.write) {
                writeCharacteristic = characteristic
            }
            if ["2A26", "2A27", "2A28", "2A29"].contains(characteristic.uuid.uuidString),
               characteristic.properties.contains(.read) {
                peripheral.readValue(for: characteristic)
            }
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateNotificationStateFor characteristic: CBCharacteristic, error: Error?) {
        emit("subscription", ["uuid": characteristic.uuid.uuidString, "active": characteristic.isNotifying,
                              "error": error?.localizedDescription ?? ""])
        if characteristic.isNotifying, commandDirectory != nil, commandTimer == nil {
            commandTimer = Timer.scheduledTimer(withTimeInterval: 0.2, repeats: true) { _ in self.pollCommands() }
            emit("command_mode_ready")
        }
    }

    private func crc16(_ bytes: Data) -> UInt16 {
        var crc: UInt16 = 0xffff
        for byte in bytes {
            crc ^= UInt16(byte)
            for _ in 0..<8 { crc = crc & 1 == 1 ? (crc >> 1) ^ 0xa001 : crc >> 1 }
        }
        return crc
    }

    private func integer(_ value: Int, bytes: Int) -> Data {
        Data((0..<bytes).reversed().map { UInt8((value >> ($0 * 8)) & 0xff) })
    }

    private func enqueue(_ wrapper: [String: Any]) throws {
        guard let command = wrapper["command"] as? [String: Any],
              let method = command["method"] as? String,
              ["getDevSta", "getSysSta", "getConfigFile", "getConfigField", "setConfigField", "setLight", "setFan", "setBlower"].contains(method),
              let id = command["msgId"] as? String else {
            throw NSError(domain: "BLELab", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unsupported or incomplete command"])
        }
        let payload = try JSONSerialization.data(withJSONObject: command, options: [.sortedKeys, .withoutEscapingSlashes])
        let maxWrite = selected?.maximumWriteValueLength(for: .withResponse) ?? 0
        guard maxWrite > 22 else { throw NSError(domain: "BLELab", code: 2) }
        var frames: [Data] = []
        if wrapper["transport"] as? String == "raw", payload.count <= maxWrite {
            frames = [payload]
        } else {
            let checksum = Int(crc16(payload))
            let chunkSize = min(180, maxWrite - 22)
            for offset in stride(from: 0, to: payload.count, by: chunkSize) {
                let chunk = payload.subdata(in: offset..<min(offset + chunkSize, payload.count))
                let body = integer(1, bytes: 2) + integer(checksum, bytes: 2)
                    + integer(payload.count, bytes: 4) + integer(offset, bytes: 4)
                    + integer(chunk.count, bytes: 2) + chunk
                var frame = Data([0xaa, 0xaa, 0x00, 0x03]) + integer(body.count, bytes: 2) + body
                frame += integer(Int(crc16(frame)), bytes: 2)
                frames.append(frame)
            }
        }
        emit("command_queued", ["method": method, "msgId": id, "frames": frames.count,
                               "params": command["params"] ?? [:]])
        for (index, frame) in frames.enumerated() { queuedWrites.append((frame, index == frames.count - 1 ? id : "")) }
        if let seconds = wrapper["auto_off_seconds"] as? Double,
           (1...10).contains(seconds), let off = wrapper["auto_off_command"] as? [String: Any] {
            followUps[id] = ["delay": seconds, "command": off]
        }
        writeNext()
    }

    private func pollCommands() {
        guard let directory = commandDirectory, writeCharacteristic != nil else { return }
        if FileManager.default.fileExists(atPath: directory + "/STOP"), queuedWrites.isEmpty, !writing, followUps.isEmpty {
            finish("command_session_stopped")
            return
        }
        let files = (try? FileManager.default.contentsOfDirectory(atPath: directory)) ?? []
        for name in files.sorted() where name.hasSuffix(".json") && !processedCommands.contains(name) {
            processedCommands.insert(name)
            do {
                let data = try Data(contentsOf: URL(fileURLWithPath: directory + "/" + name))
                guard let wrapper = try JSONSerialization.jsonObject(with: data) as? [String: Any] else { continue }
                try enqueue(wrapper)
                do {
                    try FileManager.default.removeItem(atPath: directory + "/" + name)
                    processedCommands.remove(name)
                } catch { /* Retain the processed marker if removal failed. */ }
            } catch { emit("command_error", ["file": name, "error": error.localizedDescription]) }
        }
    }

    private func writeNext() {
        guard !writing, !queuedWrites.isEmpty, let selected, let characteristic = writeCharacteristic else { return }
        writing = true
        selected.writeValue(queuedWrites[0].0, for: characteristic, type: .withResponse)
    }

    func peripheral(_ peripheral: CBPeripheral, didWriteValueFor characteristic: CBCharacteristic, error: Error?) {
        guard characteristic.uuid == CBUUID(string: "FF02"), !queuedWrites.isEmpty else { return }
        let written = queuedWrites.removeFirst()
        writing = false
        if let error {
            emit("write_error", ["msgId": written.1, "error": error.localizedDescription])
            queuedWrites.removeAll()
        } else if !written.1.isEmpty {
            emit("command_written", ["msgId": written.1])
            if let followUp = followUps[written.1], let delay = followUp["delay"] as? Double,
               let off = followUp["command"] as? [String: Any] {
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                    self.followUps.removeValue(forKey: written.1)
                    do { try self.enqueue(["command": off, "transport": "framed"]) }
                    catch { self.emit("auto_off_error", ["error": error.localizedDescription]) }
                }
            }
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.04) { self.writeNext() }
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        if let error { emit("error", ["detail": error.localizedDescription]); return }
        guard let data = characteristic.value else { return }
        if characteristic.isNotifying { notificationCount += 1 }
        var record: [String: Any] = ["uuid": characteristic.uuid.uuidString, "bytes": data.count,
            "hex": data.map { String(format: "%02x", $0) }.joined()]
        if let text = String(data: data, encoding: .utf8) { record["text"] = text }
        emit("value", record)
    }
}

let args = CommandLine.arguments
func option(_ name: String) -> String? {
    guard let i = args.firstIndex(of: name), i + 1 < args.count else { return nil }
    return args[i + 1]
}
guard let output = option("--output") else {
    fputs("Usage: sf-ble --output /absolute/log.jsonl [--target exact-name-or-UUID] [--scan-seconds 20] [--listen-seconds 30]\n", stderr)
    exit(1)
}
let scan = Double(option("--scan-seconds") ?? "20") ?? 20
let listen = Double(option("--listen-seconds") ?? "30") ?? 30
guard (1...300).contains(scan), (0...86400).contains(listen) else { exit(1) }
let application = NSApplication.shared
application.setActivationPolicy(.accessory)
do {
    let explorer = try BLEExplorer(output: output, socketPath: option("--socket"), target: option("--target"), scanSeconds: scan, listenSeconds: listen, commandDirectory: option("--command-dir"))
    explorer.start()
    withExtendedLifetime(explorer) { application.run() }
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
