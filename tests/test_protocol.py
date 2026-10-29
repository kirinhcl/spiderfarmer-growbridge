import json
import struct

import pytest

from growbridge.protocol import Decoder, ProtocolError, crc16, encode, public_data


def test_crc_known_answer():
    assert crc16(b"123456789") == 0x4B37


def test_interleaved_out_of_order_and_duplicate_fragments():
    a = {"method": "getDevSta", "data": {"sensor": {"temp": 22.5}, "text": "x" * 300}}
    b = {"method": "getSysSta", "data": {"sys": {"ver": "example"}}}
    first, second = encode(a, 40), encode(b, 20)
    decoder = Decoder()
    output = []
    assert decoder.feed(first[-1]) is None
    for packet in [first[-1], *second, *first[:-1]]:
        if message := decoder.feed(packet):
            output.append(message)
    assert output == [b, a]


def test_corrupt_crc_is_rejected():
    packet = bytearray(encode({"method": "test"})[0])
    packet[-3] ^= 1
    with pytest.raises(ProtocolError, match="CRC"):
        Decoder().feed(bytes(packet))


def test_valid_encrypted_version_is_rejected():
    packet = bytearray(encode({"method": "test"})[0])
    packet[6:8] = struct.pack(">H", 2)
    packet[-2:] = struct.pack(">H", crc16(packet[:-2]))
    decoder = Decoder()
    with pytest.raises(ProtocolError, match="v2"):
        decoder.feed(bytes(packet))
    assert decoder.version == 2


def test_raw_ack_and_private_fields():
    raw = {"method": "setConfigField", "code": 200, "uid": "synthetic", "pid": "synthetic"}
    assert Decoder().feed(json.dumps(raw).encode()) == raw
    assert public_data(raw) == {"method": "setConfigField", "code": 200}
