import httpx

from growbridge.api import create_app
from growbridge.mcp_server import create_mcp


async def test_api_authentication_and_bounds(bridge, settings):
    core, device = bridge
    app = create_app(settings, core)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        assert (await client.get("/status")).status_code == 401
        client.headers["Authorization"] = f"Bearer {settings.token}"
        assert (await client.get("/status")).json()["data"]["sensor"]["temp"] == 22.5
        assert (
            await client.post("/control/light", json={"request_id": "bounds-001", "level": 101})
        ).status_code == 422
        assert (
            await client.post("/pump", json={"request_id": "pump-001", "seconds": 6})
        ).status_code == 409
        assert not device.commands


async def test_mcp_tool_inventory_and_annotations(settings):
    tools = await create_mcp(settings).list_tools()
    assert len(tools) == 8
    by_name = {tool.name: tool for tool in tools}
    assert by_name["get_status"].annotations.readOnlyHint
    assert by_name["run_pump"].annotations.destructiveHint
    assert "request_id" in by_name["run_pump"].inputSchema["required"]
