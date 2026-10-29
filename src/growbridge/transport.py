"""One BLE owner: a signed native helper on macOS, Bleak/BlueZ on Linux."""

import asyncio
import contextlib
import json
import os
import plistlib
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from .protocol import NOTIFY_UUID, WRITE_UUID, encode


def build_native(data_dir: Path) -> Path:
    source = Path(__file__).parent / "native" / "BLEHelper.swift"
    app = data_dir / "GrowBridge BLE.app"
    executable = app / "Contents" / "MacOS" / "sf-ble"
    if executable.exists() and executable.stat().st_mtime >= source.stat().st_mtime:
        return app
    executable.parent.mkdir(parents=True, exist_ok=True)
    info = {
        "CFBundleIdentifier": "local.growbridge.ble",
        "CFBundleName": "GrowBridge BLE",
        "CFBundleExecutable": "sf-ble",
        "CFBundlePackageType": "APPL",
        "CFBundleVersion": "1",
        "LSUIElement": True,
        "NSBluetoothAlwaysUsageDescription": "连接 Spider Farmer，读取数据并按你的指令控制设备。",
    }
    (app / "Contents" / "Info.plist").write_bytes(plistlib.dumps(info))
    subprocess.run(
        [
            "xcrun",
            "swiftc",
            str(source),
            "-o",
            str(executable),
            "-framework",
            "CoreBluetooth",
            "-framework",
            "AppKit",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["codesign", "--force", "--sign", "-", str(app)], check=True, capture_output=True
    )
    return app


async def scan_devices(data_dir: Path, seconds: int = 8) -> list[dict]:
    if sys.platform != "darwin":
        from bleak import BleakScanner

        devices = await BleakScanner.discover(timeout=seconds, return_adv=True)
        return [
            {"name": adv.local_name or device.name, "address": device.address, "rssi": adv.rssi}
            for device, adv in devices.values()
            if (adv.local_name or device.name or "").startswith("SF-")
        ]
    app = await asyncio.to_thread(build_native, data_dir)
    with tempfile.TemporaryDirectory(prefix="growbridge-scan-", dir="/tmp") as folder:
        output = Path(folder) / "scan.jsonl"
        process = await asyncio.create_subprocess_exec(
            "open",
            "-n",
            "-W",
            str(app),
            "--args",
            "--output",
            str(output),
            "--scan-seconds",
            str(seconds),
            "--listen-seconds",
            "0",
        )
        await asyncio.wait_for(process.wait(), timeout=110)
        events = [json.loads(line) for line in output.read_text().splitlines()]
        if events[-1].get("reason") != "scan_complete":
            raise RuntimeError(f"Bluetooth scan failed: {events[-1].get('reason')}")
        return [
            {"name": event["name"], "address": event["id"], "rssi": event["rssi"]}
            for event in events
            if event["event"] == "device" and event.get("name", "").startswith("SF-")
        ]


class NativeTransport:
    def __init__(self, device: str, data_dir: Path):
        self.device, self.data_dir = device, data_dir
        self.connected = False
        self.pending: dict[str, asyncio.Future] = {}
        self.ready = asyncio.Event()
        self.tasks: set[asyncio.Task] = set()
        self.process = None
        self.server = None
        self.folder = None
        self.failure = None
        self.native_pid = None

    async def connect(self, callback):
        self.callback = callback
        app = await asyncio.to_thread(build_native, self.data_dir)
        self.folder = Path(tempfile.mkdtemp(prefix="growbridge-", dir="/tmp"))
        self.commands = self.folder / "commands"
        self.commands.mkdir(mode=0o700)
        socket_path = self.folder / "events.sock"

        async def accepted(reader, writer):
            try:
                while line := await reader.readline():
                    event = json.loads(line)
                    kind = event["event"]
                    if kind == "start":
                        self.native_pid = event.get("process_id")
                    elif kind == "connected":
                        self.connected = True
                    elif kind == "command_mode_ready":
                        self.ready.set()
                    elif kind == "value":
                        callback(bytes.fromhex(event["hex"]))
                    elif kind == "command_written":
                        future = self.pending.get(event["msgId"])
                        if future is not None and not future.done():
                            future.set_result(None)
                    elif kind in {"complete", "write_error", "command_error"}:
                        self.failure = RuntimeError(f"BLE helper: {event.get('reason', kind)}")
                        self.connected = False
                        self.ready.set()
                        for future in self.pending.values():
                            if not future.done():
                                future.set_exception(self.failure)
            finally:
                self.connected = False
                self.ready.set()
                writer.close()
                await writer.wait_closed()

        def connection(reader, writer):
            task = asyncio.create_task(accepted(reader, writer))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)

        self.server = await asyncio.start_unix_server(connection, str(socket_path), limit=1048576)
        self.process = await asyncio.create_subprocess_exec(
            "open",
            "-n",
            "-W",
            str(app),
            "--args",
            "--output",
            str(self.folder / "unused.jsonl"),
            "--socket",
            str(socket_path),
            "--target",
            self.device,
            "--scan-seconds",
            "20",
            "--listen-seconds",
            "0",
            "--command-dir",
            str(self.commands),
        )
        await asyncio.wait_for(self.ready.wait(), 100)
        if self.failure or not self.connected:
            raise self.failure or RuntimeError("Bluetooth connection unavailable")

    async def send(self, command: dict):
        if not self.connected:
            raise ConnectionError("BLE disconnected")
        message_id = command["msgId"]
        future = asyncio.get_running_loop().create_future()
        self.pending[message_id] = future
        path = self.commands / f"{message_id}.json"
        temporary = path.with_suffix(".pending")
        temporary.write_text(json.dumps({"command": command, "transport": "framed"}))
        temporary.chmod(0o600)
        temporary.replace(path)
        try:
            await asyncio.wait_for(future, 10)
        finally:
            self.pending.pop(message_id, None)

    async def close(self):
        if self.folder and self.folder.exists():
            (self.commands / "STOP").touch()
        if self.process:
            try:
                await asyncio.wait_for(self.process.wait(), 10)
            except TimeoutError:
                if self.native_pid:
                    with contextlib.suppress(ProcessLookupError):
                        os.kill(self.native_pid, signal.SIGTERM)
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        for task in list(self.tasks):
            task.cancel()
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        if self.folder:
            shutil.rmtree(self.folder, ignore_errors=True)
        self.connected = False


class BleakTransport:
    def __init__(self, device: str, data_dir: Path):
        self.device = device
        self.client = None

    @property
    def connected(self):
        return self.client is not None and self.client.is_connected

    async def connect(self, callback):
        from bleak import BleakClient, BleakScanner

        device = await BleakScanner.find_device_by_address(self.device, timeout=20)
        if device is None:
            raise ConnectionError("Configured BLE address was not found; run growbridge scan")
        self.client = BleakClient(device, timeout=20)
        await self.client.connect()
        await self.client.start_notify(NOTIFY_UUID, lambda _, data: callback(bytes(data)))

    async def send(self, command: dict):
        for packet in encode(command, chunk_size=80):
            await self.client.write_gatt_char(WRITE_UUID, packet, response=True)
            await asyncio.sleep(0.04)

    async def close(self):
        if self.client:
            await self.client.disconnect()


def make_transport(settings):
    backend = NativeTransport if sys.platform == "darwin" else BleakTransport
    return backend(settings.device, settings.data_dir)
