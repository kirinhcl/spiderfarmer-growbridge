"""Observed GGS v1 framing. Encrypted firmware is rejected before any control write."""

import json
import struct
import time

MAGIC = b"\xaa\xaa\x00\x03"
NOTIFY_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"


class ProtocolError(ValueError):
    pass


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def encode(message: dict, chunk_size: int = 180) -> list[bytes]:
    if not 1 <= chunk_size <= 480:
        raise ValueError("Invalid chunk size")
    payload = json.dumps(message, separators=(",", ":"), ensure_ascii=False).encode()
    checksum = crc16(payload)
    result = []
    for offset in range(0, len(payload), chunk_size):
        chunk = payload[offset : offset + chunk_size]
        body = struct.pack(">HHIIH", 1, checksum, len(payload), offset, len(chunk)) + chunk
        frame = MAGIC + struct.pack(">H", len(body)) + body
        result.append(frame + struct.pack(">H", crc16(frame)))
    return result


class Decoder:
    def __init__(self) -> None:
        self.groups: dict[tuple, tuple[float, dict]] = {}
        self.version: int | None = None

    def feed(self, packet: bytes) -> dict | None:
        if packet.lstrip().startswith(b"{"):
            message = json.loads(packet)
            if not isinstance(message, dict):
                raise ProtocolError("Response must be a JSON object")
            return message
        if len(packet) < 22 or packet[:4] != MAGIC:
            raise ProtocolError("Unrecognized BLE frame")
        length, version, checksum, total, offset, count = struct.unpack(">HHHIIH", packet[4:20])
        if length != len(packet) - 8 or len(packet) != count + 22:
            raise ProtocolError("Frame length mismatch")
        if crc16(packet[:-2]) != int.from_bytes(packet[-2:], "big"):
            raise ProtocolError("Frame CRC mismatch")
        self.version = version
        if version != 1:
            raise ProtocolError(f"Unsupported protocol v{version}; controls disabled")
        if not 0 < total <= 1048576 or not count or offset + count > total:
            raise ProtocolError("Invalid fragment bounds")
        now = time.monotonic()
        self.groups = {key: value for key, value in self.groups.items() if now - value[0] < 30}
        key = checksum, total
        if key not in self.groups and len(self.groups) >= 32:
            raise ProtocolError("Too many incomplete messages")
        _, chunks = self.groups.setdefault(key, (now, {}))
        chunk = packet[20:-2]
        for previous, previous_chunk in chunks.items():
            if previous == offset and previous_chunk == chunk:
                continue
            if offset < previous + len(previous_chunk) and previous < offset + count:
                raise ProtocolError("Overlapping fragments")
        chunks[offset] = chunk
        position, assembled = 0, bytearray()
        for chunk_offset, fragment in sorted(chunks.items()):
            if chunk_offset != position:
                return None
            assembled.extend(fragment)
            position += len(fragment)
        if position != total:
            return None
        del self.groups[key]
        if crc16(assembled) != checksum:
            raise ProtocolError("Message CRC mismatch")
        message = json.loads(assembled)
        if not isinstance(message, dict):
            raise ProtocolError("Response must be a JSON object")
        return message


def public_data(value):
    if isinstance(value, dict):
        return {
            key: public_data(item)
            for key, item in value.items()
            if key not in {"uid", "pid", "id", "ssid", "password", "TZ"}
        }
    if isinstance(value, list):
        return [public_data(item) for item in value]
    return value
