import asyncio
import copy
import json
import logging
import math
import time
import uuid

from .protocol import Decoder, ProtocolError, public_data
from .store import Store
from .transport import make_transport

log = logging.getLogger(__name__)


class BridgeError(RuntimeError):
    pass


class PumpOffUnconfirmed(BridgeError):
    pass


class Bridge:
    def __init__(self, settings, transport_factory=make_transport):
        self.settings = settings
        self.store = Store(settings.data_dir / "growbridge.sqlite3")
        self.transport_factory = transport_factory
        self.transport = None
        self.decoder = Decoder()
        self.identity = {}
        self.data = {}
        self.system = {}
        self.received_at = 0.0
        self.received_monotonic = 0.0
        self.pending = {}
        self.query_lock = asyncio.Lock()
        self.operation_lock = asyncio.Lock()
        self.registration_lock = asyncio.Lock()
        self.jobs = {}
        self.task = None
        self.last_error = None
        self.interlock = any(kind == "pump" for _, kind in self.store.pending())
        self.last_prune = 0.0

    @property
    def connected(self):
        return self.transport is not None and self.transport.connected

    def packet(self, packet):
        try:
            message = self.decoder.feed(packet)
        except (ProtocolError, ValueError) as error:
            self.last_error = str(error)
            return
        if message is None:
            return
        if message.get("pid") and message.get("uid"):
            self.identity = {key: message[key] for key in ("pid", "uid", "pcode") if key in message}
        method = message.get("method")
        if message.get("code") == 200 and isinstance(message.get("data"), dict):
            if method == "getDevSta":
                self.data = public_data(message["data"])
                self.received_at = time.time()
                self.received_monotonic = time.monotonic()
                self.store.sample(self.data)
                if time.monotonic() - self.last_prune > 3600:
                    self.store.prune(self.settings.retention_days)
                    self.last_prune = time.monotonic()
            elif method == "getSysSta":
                self.system = public_data(message["data"].get("sys", {}))
        future = self.pending.get((str(message.get("msgId")), method))
        if future is not None and not future.done():
            if message.get("code") == 200:
                future.set_result(message)
            else:
                future.set_exception(
                    BridgeError(f"Device rejected {method}: code {message.get('code')}")
                )

    async def start(self):
        self.task = asyncio.create_task(self.run())

    async def run(self):
        delay = 1
        while True:
            self.transport = self.transport_factory(self.settings)
            self.decoder = Decoder()
            self.identity = {}
            self.received_monotonic = 0
            try:
                await self.transport.connect(self.packet)
                log.info("BLE connected")
                for _ in range(150):
                    if self.identity and self.decoder.version == 1:
                        break
                    await asyncio.sleep(0.1)
                if self.decoder.version != 1 or not self.identity:
                    raise BridgeError("No supported v1 telemetry received")
                await self.recover()
                self.last_error = None
                delay = 1
                while self.connected:
                    await asyncio.sleep(1)
                    if self.interlock:
                        await self.recover()
                raise ConnectionError("BLE disconnected")
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.last_error = f"{type(error).__name__}: {error}"
                log.warning("BLE unavailable; reconnecting in %s seconds", delay)
            finally:
                for future in self.pending.values():
                    if not future.done():
                        future.set_exception(BridgeError("BLE connection ended"))
                try:
                    await self.transport.close()
                except Exception:
                    log.warning("BLE close did not complete cleanly")
            await asyncio.sleep(delay)
            delay = min(delay * 2, 30)

    async def stop(self):
        for task in list(self.jobs.values()):
            if not task.done():
                task.cancel()
        if self.jobs:
            await asyncio.gather(*list(self.jobs.values()), return_exceptions=True)
        if self.task:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
        self.store.close()

    async def request(self, method, params=None):
        async with self.query_lock:
            if not self.connected or not self.identity or self.decoder.version != 1:
                raise BridgeError("Supported live BLE connection required")
            message_id = str(time.time_ns() // 1000000) + uuid.uuid4().hex[:6]
            command = {
                "method": method,
                **self.identity,
                "params": params or {},
                "msgId": message_id,
            }
            future = asyncio.get_running_loop().create_future()
            key = message_id, method
            self.pending[key] = future
            try:
                await self.transport.send(command)
                return await asyncio.wait_for(future, timeout=8)
            except TimeoutError as error:
                raise BridgeError(f"No matched device reply for {method}") from error
            finally:
                self.pending.pop(key, None)
                if not future.done():
                    future.cancel()

    def health(self):
        age = time.monotonic() - self.received_monotonic if self.received_monotonic else None
        return {
            "connected": self.connected,
            "protocol_version": self.decoder.version,
            "controls_enabled": self.settings.controls_enabled,
            "pump_off_unconfirmed": self.interlock,
            "last_sample_at": self.received_at or None,
            "age_seconds": round(age, 2) if age is not None else None,
            "stale": age is None or age > self.settings.stale_seconds or not self.connected,
            "last_error": self.last_error,
            "outlet_mapping": {
                "light": self.settings.light_outlet,
                "exhaust": self.settings.exhaust_outlet,
                "fan": self.settings.fan_outlet,
                "pump": self.settings.pump_outlet,
            },
        }

    async def status(self, refresh=False):
        if refresh:
            await self.request("getDevSta")
        return {"health": self.health(), "data": self.data, "system": self.system}

    def check_write(self):
        health = self.health()
        if not self.settings.controls_enabled:
            raise BridgeError("Controls disabled in local configuration")
        if self.interlock:
            raise BridgeError("Pump off is unconfirmed; resolve before further controls")
        if health["stale"] or self.decoder.version != 1:
            raise BridgeError("Fresh v1 telemetry is required before control")

    async def configuration(self):
        response = await self.request("getConfigFile")
        config = response.get("data", {}).get("configFile")
        if not isinstance(config, dict) or not isinstance(config.get("device"), dict):
            raise BridgeError("Incomplete configuration; refusing to overwrite settings")
        return config

    async def verify(self, section, key, predicate):
        for _ in range(3):
            response = await self.request("getDevSta")
            data = response["data"]
            state = data.get(section, {}).get(key) if section == "outlet" else data.get(key)
            if isinstance(state, dict) and predicate(state):
                return state
            await asyncio.sleep(0.5)
        raise BridgeError("Device state did not confirm the requested setting")

    def outlet_params(self, config, number, on):
        key = f"O{number}"
        block = config.get("outlet", {}).get(key)
        if not isinstance(block, dict):
            raise BridgeError(f"Outlet {number} is absent from the live configuration")
        block = copy.deepcopy(block)
        block.update(modeType=0, mOnOff=int(on))
        return {"keyPath": ["outlet", key], key: block}

    async def set_outlet(self, number, on):
        config = await self.configuration()
        await self.request("setConfigField", self.outlet_params(config, number, on))
        return await self.verify("outlet", f"O{number}", lambda state: state.get("on") == int(on))

    async def set_module(self, module, level):
        config = await self.configuration()
        block = config["device"].get(module)
        if not isinstance(block, dict):
            raise BridgeError(f"{module} is absent from the live configuration")
        before = copy.deepcopy(block)
        block = copy.deepcopy(block)
        block.update(modeType=0, mOnOff=int(level > 0), mLevel=level)
        if module == "blower" and "maxSpeed" in block:
            block["maxSpeed"] = level
        await self.request("setConfigField", {"keyPath": ["device", module], module: block})
        state = await self.verify(
            "device",
            module,
            lambda value: (
                value.get("level") == level and value.get("on", int(level > 0)) == int(level > 0)
            ),
        )
        return {"before": before, "confirmed_state": state}

    async def pump(self, seconds):
        config = await self.configuration()
        number = self.settings.pump_outlet
        on = self.outlet_params(config, number, True)
        off = self.outlet_params(config, number, False)
        began = time.monotonic()
        confirmed_off = None
        confirmed_on = False
        try:
            try:
                async with asyncio.timeout(seconds):
                    await self.request("setConfigField", on)
                    await self.verify("outlet", f"O{number}", lambda state: state.get("on") == 1)
                    confirmed_on = True
                    await asyncio.sleep(seconds)
            except TimeoutError:
                pass
        finally:
            for _ in range(2):
                try:
                    await self.request("setConfigField", off)
                    confirmed_off = await self.verify(
                        "outlet", f"O{number}", lambda state: state.get("on") == 0
                    )
                    break
                except Exception:
                    await asyncio.sleep(0.2)
            if confirmed_off is None:
                self.interlock = True
                self.last_error = "Pump off unconfirmed; check the pump physically"
                raise PumpOffUnconfirmed(self.last_error)
        if not confirmed_on:
            raise BridgeError("Pump was turned off but its startup could not be verified")
        return {
            "requested_seconds": seconds,
            "elapsed_seconds": round(time.monotonic() - began, 2),
            "confirmed_state": confirmed_off,
        }

    async def recover(self):
        for key, kind in self.store.pending():
            if kind == "pump":
                self.interlock = True
                await self.set_outlet(self.settings.pump_outlet, False)
            self.store.complete(
                key,
                {
                    "error": "Interrupted operation; not replayed",
                    "pump_off_confirmed": kind == "pump",
                },
                state="failed",
            )
        self.interlock = False

    def validate_action(self, kind, params):
        if kind in {"light", "exhaust", "fan"}:
            maximum = 10 if kind == "fan" else 100
            if type(params.get("level")) is not int or not 0 <= params["level"] <= maximum:
                raise BridgeError(f"Level must be an integer from 0 to {maximum}")
        elif kind == "outlet":
            if (
                type(params.get("number")) is not int
                or not 1 <= params["number"] <= 5
                or type(params.get("on")) is not bool
            ):
                raise BridgeError("Invalid outlet request")
            if params["number"] == self.settings.pump_outlet and params["on"]:
                raise BridgeError("Use run_pump with a finite duration for the pump outlet")
        elif kind == "pump":
            seconds = params.get("seconds")
            if (
                isinstance(seconds, bool)
                or not isinstance(seconds, (int, float))
                or not math.isfinite(seconds)
                or not 0 < seconds <= self.settings.max_pump_seconds
            ):
                raise BridgeError(
                    f"Pump duration must be within {self.settings.max_pump_seconds} seconds"
                )
            if time.time() - self.store.last_pump() < self.settings.pump_cooldown_seconds:
                raise BridgeError("Pump cooldown has not elapsed")
        else:
            raise BridgeError("Unknown action")

    async def operate(self, key, kind, params):
        async with self.registration_lock:
            previous = self.store.operation(key)
            if previous:
                if previous["kind"] != kind or previous["params"] != json.dumps(
                    params, sort_keys=True
                ):
                    raise BridgeError("Request ID already used for different arguments")
                if key in self.jobs:
                    task = self.jobs[key]
                elif previous["state"] == "complete":
                    return json.loads(previous["result"])
                else:
                    raise BridgeError(
                        "Previous operation interrupted or failed; "
                        "inspect state before retrying with a new request ID"
                    )
            else:
                self.check_write()
                self.validate_action(kind, params)
                self.store.begin(key, kind, params)
                task = asyncio.create_task(self.execute(key, kind, params))
                self.jobs[key] = task
                task.add_done_callback(lambda done: self.jobs.pop(key, None))
                task.add_done_callback(
                    lambda done: done.exception() if not done.cancelled() else None
                )
        return await asyncio.shield(task)

    async def execute(self, key, kind, params):
        try:
            async with self.operation_lock:
                self.check_write()
                if kind == "pump":
                    result = await self.pump(params["seconds"])
                elif kind == "outlet":
                    result = {
                        "confirmed_state": await self.set_outlet(params["number"], params["on"])
                    }
                else:
                    module = {"light": "light", "exhaust": "blower", "fan": "fan"}[kind]
                    result = await self.set_module(module, params["level"])
                receipt = {
                    "request_id": key,
                    "action": kind,
                    "completed_at": time.time(),
                    **public_data(result),
                }
                self.store.complete(key, receipt)
                return receipt
        except PumpOffUnconfirmed:
            # Leave the durable operation pending so the next BLE connection turns it off.
            raise
        except BaseException as error:
            self.store.complete(key, {"error": type(error).__name__}, state="failed")
            raise
