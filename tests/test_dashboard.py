import csv
import io
import json
import time
from contextlib import aclosing

import httpx
import pytest

from growbridge.api import create_app
from growbridge.dashboard import COOKIE


async def browser_client(bridge, settings):
    core, _ = bridge
    app = create_app(settings, core)
    client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=settings.url)
    link = await client.post("/ui/session", headers={"Authorization": f"Bearer {settings.token}"})
    code = link.json()["code"]
    response = await client.post(
        "/ui/session/redeem", json={"code": code}, headers={"Origin": settings.url}
    )
    assert response.status_code == 200
    return client, app, code, response


async def test_dashboard_assets_are_public_but_data_is_private(bridge, settings):
    app = create_app(settings, bridge[0])
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url=settings.url
    ) as client:
        root = await client.get("/")
        assert root.status_code == 200
        assert settings.token not in root.text
        assert "frame-ancestors 'none'" in root.headers["content-security-policy"]
        assert (await client.get("/assets/app.js")).status_code == 200
        for path in (
            "/status",
            "/activity",
            "/ui/settings",
            "/history/series",
            "/history/export.csv",
        ):
            assert (await client.get(path)).status_code == 401
        assert (await client.post("/ui/session")).status_code == 401


async def test_browser_link_is_single_use_and_session_cookie_is_private(bridge, settings):
    client, app, code, response = await browser_client(bridge, settings)
    async with aclosing(client):
        cookie = response.headers["set-cookie"].lower()
        assert "httponly" in cookie and "samesite=strict" in cookie
        assert settings.token not in response.text
        assert (await client.get("/status")).status_code == 200
        assert (await client.post("/ui/session")).status_code == 401
        again = await client.post(
            "/ui/session/redeem", json={"code": code}, headers={"Origin": settings.url}
        )
        assert again.status_code == 401


async def test_cookie_controls_require_same_origin_and_control_header(bridge, settings):
    client, _, _, _ = await browser_client(bridge, settings)
    async with aclosing(client):
        body = {"request_id": "browser-control-001", "level": 20}
        assert (await client.post("/control/light", json=body)).status_code == 403
        response = await client.post(
            "/control/light",
            json=body,
            headers={"Origin": "https://unrelated.example", "X-GrowBridge-UI": "1"},
        )
        assert response.status_code == 403
        assert not bridge[1].commands
        response = await client.post(
            "/control/light",
            json=body,
            headers={"Origin": settings.url, "X-GrowBridge-UI": "1"},
        )
        assert response.status_code == 200
        assert response.json()["confirmed_state"]["level"] == 20
        operations = (await client.get("/activity")).json()["operations"]
        assert operations[0]["request_id"] == "browser-control-001"


async def test_logout_revokes_old_cookie(bridge, settings):
    client, _, _, _ = await browser_client(bridge, settings)
    async with aclosing(client):
        old = client.cookies.get(COOKIE)
        assert (
            await client.post(
                "/ui/logout", headers={"Origin": settings.url, "X-GrowBridge-UI": "1"}
            )
        ).status_code == 200
        client.cookies.set(COOKIE, old)
        assert (await client.get("/status")).status_code == 401


async def test_expired_link_cannot_create_session(bridge, settings):
    app = create_app(settings, bridge[0])
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url=settings.url
    ) as client:
        link = await client.post(
            "/ui/session", headers={"Authorization": f"Bearer {settings.token}"}
        )
        app.state.browser_sessions.codes = {key: 0 for key in app.state.browser_sessions.codes}
        response = await client.post(
            "/ui/session/redeem",
            json={"code": link.json()["code"]},
            headers={"Origin": settings.url},
        )
        assert response.status_code == 401


async def test_history_sampling_covers_the_whole_window_and_export_keeps_raw_rows(bridge, settings):
    core, _ = bridge
    core.store.db.execute("DELETE FROM samples")
    now = time.time()
    points = [(now - 3500 + i * 34, {"sensor": {"temp": i, "humi": 50}}) for i in range(100)]
    core.store.db.executemany(
        "INSERT INTO samples VALUES(?,?)", [(at, json.dumps(data)) for at, data in points]
    )
    core.store.db.commit()
    app = create_app(settings, core)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=settings.url,
        headers={"Authorization": f"Bearer {settings.token}"},
    ) as client:
        series = (await client.get("/history/series?hours=1&points=10")).json()
        assert series["total_samples"] == 100
        assert series["downsampled"]
        assert 2 <= len(series["samples"]) <= 11
        assert series["samples"][0]["timestamp"] < now - 3000
        assert series["samples"][-1]["data"]["sensor"]["temp"] == 99
        result = await client.get("/history/export.csv?hours=1")
        rows = list(csv.DictReader(io.StringIO(result.text)))
        assert len(rows) == 100
        assert rows[0]["temperature_c"] == "0" and rows[-1]["temperature_c"] == "99"
        assert rows[0]["co2_ppm"] == ""
        assert rows[0]["timestamp_utc"].endswith("+00:00")


async def test_csv_does_not_export_spreadsheet_formulas_from_device_fields(bridge, settings):
    core, _ = bridge
    core.store.sample({"sensor": {"temp": '=HYPERLINK("example")', "humi": 0}})
    app = create_app(settings, core)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=settings.url,
        headers={"Authorization": f"Bearer {settings.token}"},
    ) as client:
        response = await client.get("/history/export.csv?hours=1")
        assert "HYPERLINK" not in response.text
        rows = list(csv.DictReader(io.StringIO(response.text)))
        assert rows[-1]["temperature_c"] == ""
        assert rows[-1]["humidity_percent"] == "0"


@pytest.mark.parametrize(
    "path", ["/history/series?hours=0", "/history/series?points=99999", "/activity?limit=1000"]
)
async def test_dashboard_query_bounds(bridge, settings, path):
    app = create_app(settings, bridge[0])
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=settings.url,
        headers={"Authorization": f"Bearer {settings.token}"},
    ) as client:
        assert (await client.get(path)).status_code == 422
