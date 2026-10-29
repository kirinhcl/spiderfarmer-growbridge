import asyncio
import copy
import time

import pytest

from growbridge.service import BridgeError, PumpOffUnconfirmed


async def test_light_readback_and_configuration_preservation(bridge):
    core, device = bridge
    before = copy.deepcopy(device.config)
    result = await core.operate("light-001", "light", {"level": 30})
    assert result["confirmed_state"] == {"on": 1, "level": 30}
    assert device.config["device"]["light"]["timePeriod"] == before["device"]["light"]["timePeriod"]
    assert device.config["alarm"] == before["alarm"]
    assert device.config["device"]["fan"] == before["device"]["fan"]


@pytest.mark.parametrize(
    "kind,params",
    [
        ("fan", {"level": 11}),
        ("light", {"level": True}),
        ("pump", {"seconds": float("nan")}),
        ("pump", {"seconds": 6}),
        ("outlet", {"number": 4, "on": True}),
    ],
)
async def test_invalid_controls_never_reach_radio(bridge, kind, params):
    core, device = bridge
    with pytest.raises(BridgeError):
        await core.operate("invalid-001", kind, params)
    assert not device.commands


async def test_stale_or_disabled_controls_are_blocked(bridge):
    core, device = bridge
    core.received_monotonic = time.monotonic() - 100
    with pytest.raises(BridgeError, match="Fresh"):
        await core.operate("stale-001", "light", {"level": 20})
    assert not device.commands
    core.received_monotonic = time.monotonic()
    core.settings.controls_enabled = False
    with pytest.raises(BridgeError, match="disabled"):
        await core.operate("disabled-001", "light", {"level": 20})


async def test_ack_without_state_change_is_failure(bridge):
    core, device = bridge
    device.ignore_writes = True
    with pytest.raises(BridgeError, match="state did not confirm"):
        await core.operate("ignored-001", "light", {"level": 30})
    assert core.store.operation("ignored-001")["state"] == "failed"


async def test_same_request_id_executes_once_and_conflicting_args_fail(bridge):
    core, device = bridge
    a, b = await asyncio.gather(
        core.operate("same-001", "fan", {"level": 2}), core.operate("same-001", "fan", {"level": 2})
    )
    assert a == b
    assert sum(command["method"] == "setConfigField" for command in device.commands) == 1
    assert await core.operate("same-001", "fan", {"level": 2}) == a
    with pytest.raises(BridgeError, match="different arguments"):
        await core.operate("same-001", "fan", {"level": 3})


async def test_pump_duplicate_does_not_water_twice(bridge):
    core, device = bridge
    a, b = await asyncio.gather(
        core.operate("pump-001", "pump", {"seconds": 0.05}),
        core.operate("pump-001", "pump", {"seconds": 0.05}),
    )
    assert a == b
    assert device.config["outlet"]["O4"]["mOnOff"] == 0
    assert sum(command["method"] == "setConfigField" for command in device.commands) == 2


async def test_client_cancellation_does_not_cancel_pump_off(bridge):
    core, device = bridge
    caller = asyncio.create_task(core.operate("cancel-001", "pump", {"seconds": 0.08}))
    await device.on_event.wait()
    caller.cancel()
    with pytest.raises(asyncio.CancelledError):
        await caller
    await asyncio.sleep(0.15)
    assert device.config["outlet"]["O4"]["mOnOff"] == 0
    assert core.store.operation("cancel-001")["state"] == "complete"


async def test_missing_on_ack_does_not_delay_off_until_request_timeout(bridge):
    core, device = bridge
    device.delay_pump_ack = True
    began = time.monotonic()
    with pytest.raises(BridgeError, match="startup could not be verified"):
        await core.operate("missing-ack-001", "pump", {"seconds": 0.06})
    assert time.monotonic() - began < 1
    assert device.config["outlet"]["O4"]["mOnOff"] == 0


async def test_failed_off_keeps_durable_pending_and_blocks_controls(bridge):
    core, device = bridge
    device.fail_off = True
    with pytest.raises(PumpOffUnconfirmed):
        await core.operate("failed-off-001", "pump", {"seconds": 0.04})
    assert core.interlock
    assert core.store.operation("failed-off-001")["state"] == "pending"
    with pytest.raises(BridgeError, match="Pump off"):
        await core.operate("blocked-001", "light", {"level": 20})
    device.fail_off = False
    await core.recover()
    assert not core.interlock
    assert device.config["outlet"]["O4"]["mOnOff"] == 0


async def test_interrupted_pump_is_turned_off_without_replaying_on(bridge):
    core, device = bridge
    core.store.begin("interrupted-001", "pump", {"seconds": 5})
    device.config["outlet"]["O4"]["mOnOff"] = 1
    await core.recover()
    assert device.config["outlet"]["O4"]["mOnOff"] == 0
    writes = [command for command in device.commands if command["method"] == "setConfigField"]
    assert len(writes) == 1 and writes[0]["params"]["O4"]["mOnOff"] == 0
