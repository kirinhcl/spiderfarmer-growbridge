import asyncio
import csv
import hmac
import io
import math
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .dashboard import COOKIE, SESSION_SECONDS, BrowserSessions
from .service import Bridge, BridgeError


class Operation(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    request_id: str = Field(min_length=8, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")


class Level(Operation):
    level: StrictInt = Field(ge=0, le=100)


class Outlet(Operation):
    number: StrictInt = Field(ge=1, le=5)
    on: StrictBool


class Pump(Operation):
    seconds: float = Field(gt=0, le=60)


class BrowserCode(BaseModel):
    code: str = Field(min_length=20, max_length=100)


def create_app(settings, bridge=None):
    bridge = bridge or Bridge(settings)
    sessions = BrowserSessions()

    def check_origin(request: Request):
        allowed = {settings.url, f"http://localhost:{settings.port}"}
        if request.headers.get("origin") not in allowed:
            raise HTTPException(403, "Browser origin is not allowed")

    @asynccontextmanager
    async def lifespan(app):
        await bridge.start()
        yield
        await bridge.stop()

    async def bearer(authorization: Annotated[str | None, Header()] = None):
        expected = f"Bearer {settings.token}"
        if authorization is None or not hmac.compare_digest(authorization, expected):
            raise HTTPException(status_code=401, detail="Authentication required")

    async def authorize(request: Request, authorization: Annotated[str | None, Header()] = None):
        if authorization is not None:
            await bearer(authorization)
            return
        if not sessions.valid(request.cookies.get(COOKIE)):
            raise HTTPException(401, "Open the dashboard with growbridge dashboard to connect")
        if request.method not in {"GET", "HEAD"}:
            check_origin(request)
            if request.headers.get("x-growbridge-ui") != "1":
                raise HTTPException(403, "Browser control header is required")

    app = FastAPI(
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.bridge = bridge
    app.state.browser_sessions = sessions
    api = APIRouter(dependencies=[Depends(authorize)])
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"]
    )

    @app.middleware("http")
    async def browser_headers(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
            "base-uri 'none'; form-action 'self'"
        )
        return response

    web = Path(__file__).parent / "web"
    app.mount("/assets", StaticFiles(directory=web), name="assets")

    @app.get("/", include_in_schema=False)
    async def dashboard():
        return FileResponse(web / "index.html")

    @app.post("/ui/session", dependencies=[Depends(bearer)])
    async def browser_link():
        return {"code": sessions.issue(), "expires_in": 60}

    @app.post("/ui/session/redeem")
    async def redeem(request: Request, code: BrowserCode, response: Response):
        check_origin(request)
        session = sessions.redeem(code.code)
        response.set_cookie(
            COOKIE, session, max_age=SESSION_SECONDS, httponly=True, samesite="strict"
        )
        return {"connected": True}

    @api.post("/ui/logout")
    async def logout(request: Request, response: Response):
        sessions.revoke(request.cookies.get(COOKIE))
        response.delete_cookie(COOKIE)
        return {"connected": False}

    @api.get("/ui/settings")
    async def ui_settings():
        return {
            "stale_seconds": settings.stale_seconds,
            "max_pump_seconds": settings.max_pump_seconds,
            "pump_cooldown_seconds": settings.pump_cooldown_seconds,
            "pump_ready_at": bridge.store.last_pump() + settings.pump_cooldown_seconds,
            "retention_days": settings.retention_days,
        }

    @app.exception_handler(BridgeError)
    async def bridge_error(request, error):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=409, content={"detail": str(error)})

    @api.get("/health")
    async def health():
        return bridge.health()

    @api.get("/status")
    async def status(refresh: bool = False):
        return await bridge.status(refresh)

    @api.get("/history")
    async def history(
        hours: float = Query(default=24, gt=0, le=168),
        limit: int = Query(default=500, ge=1, le=2000),
    ):
        return {"samples": bridge.store.history(hours, limit)}

    @api.get("/history/series")
    async def history_series(
        hours: float = Query(default=24, gt=0, le=168),
        points: int = Query(default=600, ge=2, le=2000),
    ):
        return bridge.store.series(hours, points)

    @api.get("/activity")
    async def activity(limit: int = Query(default=20, ge=1, le=100)):
        return {"operations": bridge.store.activity(limit)}

    @api.get("/history/export.csv")
    async def export_csv(hours: float = Query(default=24, gt=0, le=168)):
        end = time.time()
        fields = [
            "timestamp_utc",
            "temperature_c",
            "humidity_percent",
            "vpd_kpa",
            "co2_ppm",
            "ppfd_umol_m2_s",
            "soil_temperature_c",
            "outlet_1_on",
            "outlet_2_on",
            "outlet_3_on",
            "outlet_4_on",
            "outlet_5_on",
            "light_level",
            "exhaust_level",
            "fan_level",
        ]

        def number(value):
            return value if isinstance(value, (int, float)) and math.isfinite(value) else ""

        def rows():
            stream = io.StringIO()
            writer = csv.writer(stream)
            writer.writerow(fields)
            yield stream.getvalue()
            for at, data in bridge.store.iter_samples(end - hours * 3600, end):
                stream.seek(0)
                stream.truncate()
                sensor = data.get("sensor", {})
                values = [datetime.fromtimestamp(at, UTC).isoformat()]
                values += [
                    number(sensor.get(key))
                    for key in ("temp", "humi", "vpd", "co2", "ppfd", "tempSoil")
                ]
                values += [
                    number(data.get("outlet", {}).get(f"O{i}", {}).get("on")) for i in range(1, 6)
                ]
                values += [
                    number(data.get(key, {}).get("level")) for key in ("light", "blower", "fan")
                ]
                writer.writerow(values)
                yield stream.getvalue()

        return StreamingResponse(
            rows(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="growbridge-history.csv"'},
        )

    @api.post("/control/{device}")
    async def level(device: str, operation: Level):
        if device not in {"light", "exhaust", "fan"}:
            raise HTTPException(404, "Unknown device")
        return await asyncio.shield(
            bridge.operate(operation.request_id, device, {"level": operation.level})
        )

    @api.post("/outlet")
    async def outlet(operation: Outlet):
        return await asyncio.shield(
            bridge.operate(
                operation.request_id, "outlet", {"number": operation.number, "on": operation.on}
            )
        )

    @api.post("/pump")
    async def pump(operation: Pump):
        return await asyncio.shield(
            bridge.operate(operation.request_id, "pump", {"seconds": operation.seconds})
        )

    app.include_router(api)
    return app
