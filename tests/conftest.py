import asyncio
import copy

import pytest
import pytest_asyncio

from growbridge.config import Settings
from growbridge.protocol import encode
from growbridge.service import Bridge


class SimulatedTransport:
    """Synthetic device: never touches a radio or uses a captured device identity."""

    def __init__(self):
        self.connected = False
        self.commands = []
        self.ignore_writes = False
        self.delay_pump_ack = False
        self.fail_off = False
        self.on_event = asyncio.Event()
        self.config = {
            "alarm": {"enabled": True},
            "device": {
                name: {
                    "modeType": 0,
                    "mOnOff": 1,
                    "mLevel": level,
                    "timePeriod": [{"weekmask": 42, "startTime": 123}],
                }
                for name, level in [("light", 20), ("blower", 25), ("fan", 1)]
            },
            "outlet": {f"O{n}": {"modeType": 0, "mOnOff": int(n <= 3)} for n in range(1, 6)},
        }

    def status(self):
        return {
            "sensor": {"temp": 22.5, "humi": 55, "co2": 500},
            "outlet": {
                key: {"on": value["mOnOff"]} for key, value in self.config["outlet"].items()
            },
            **{
                key: {"on": value["mOnOff"], "level": value["mLevel"] if value["mOnOff"] else 0}
                for key, value in self.config["device"].items()
            },
        }

    def emit(self, message):
        for frame in encode(
            {
                "pid": "SYNTHETIC_DEVICE",
                "uid": "SYNTHETIC_USER",
                "pcode": 1002,
                "code": 200,
                **message,
            },
            chunk_size=80,
        ):
            self.callback(frame)

    async def connect(self, callback):
        self.callback = callback
        self.connected = True
        self.emit({"method": "getDevSta", "data": self.status()})

    async def send(self, command):
        self.commands.append(copy.deepcopy(command))
        method = command["method"]
        data = {}
        if method == "getDevSta":
            data = self.status()
        elif method == "getConfigFile":
            data = {"configFile": copy.deepcopy(self.config)}
        elif method == "setConfigField":
            section, key = command["params"]["keyPath"]
            block = command["params"][key]
            if self.fail_off and key == "O4" and block["mOnOff"] == 0:
                raise ConnectionError("Simulated OFF failure")
            if not self.ignore_writes:
                self.config[section][key] = copy.deepcopy(block)
            if key == "O4" and block["mOnOff"]:
                self.on_event.set()
                if self.delay_pump_ack:
                    await asyncio.sleep(10)
        self.emit({"method": method, "msgId": command["msgId"], "data": data})

    async def close(self):
        self.connected = False


@pytest.fixture
def settings(tmp_path):
    return Settings(
        device="SIMULATED",
        token="x" * 32,
        data_dir=tmp_path,
        controls_enabled=True,
        pump_cooldown_seconds=0,
    )


@pytest_asyncio.fixture
async def bridge(settings):
    simulator = SimulatedTransport()
    instance = Bridge(settings, lambda _: simulator)
    await instance.start()
    for _ in range(50):
        if instance.identity:
            break
        await asyncio.sleep(0.01)
    yield instance, simulator
    await instance.stop()
