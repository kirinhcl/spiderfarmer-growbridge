import asyncio
import hmac
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt
from starlette.middleware.trustedhost import TrustedHostMiddleware

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


def create_app(settings, bridge=None):
    bridge = bridge or Bridge(settings)

    @asynccontextmanager
    async def lifespan(app):
        await bridge.start()
        yield
        await bridge.stop()

    async def authorize(authorization: Annotated[str | None, Header()] = None):
        expected = f"Bearer {settings.token}"
        if authorization is None or not hmac.compare_digest(authorization, expected):
            raise HTTPException(status_code=401, detail="Authentication required")

    app = FastAPI(
        lifespan=lifespan,
        dependencies=[Depends(authorize)],
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.bridge = bridge
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"]
    )

    @app.exception_handler(BridgeError)
    async def bridge_error(request, error):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.get("/health")
    async def health():
        return bridge.health()

    @app.get("/status")
    async def status(refresh: bool = False):
        return await bridge.status(refresh)

    @app.get("/history")
    async def history(
        hours: float = Query(default=24, gt=0, le=168),
        limit: int = Query(default=500, ge=1, le=2000),
    ):
        return {"samples": bridge.store.history(hours, limit)}

    @app.post("/control/{device}")
    async def level(device: str, operation: Level):
        if device not in {"light", "exhaust", "fan"}:
            raise HTTPException(404, "Unknown device")
        return await asyncio.shield(
            bridge.operate(operation.request_id, device, {"level": operation.level})
        )

    @app.post("/outlet")
    async def outlet(operation: Outlet):
        return await asyncio.shield(
            bridge.operate(
                operation.request_id, "outlet", {"number": operation.number, "on": operation.on}
            )
        )

    @app.post("/pump")
    async def pump(operation: Pump):
        return await asyncio.shield(
            bridge.operate(operation.request_id, "pump", {"seconds": operation.seconds})
        )

    return app
