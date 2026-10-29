import os
import secrets
import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


def default_config() -> Path:
    return Path.home() / ".config" / "spiderfarmer-growbridge" / "config.toml"


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device: str
    token: str = Field(min_length=24)
    data_dir: Path
    port: int = Field(default=8766, ge=1024, le=65535)
    controls_enabled: bool = False
    stale_seconds: float = Field(default=20, ge=5, le=120)
    max_pump_seconds: float = Field(default=5, gt=0, le=60)
    pump_cooldown_seconds: float = Field(default=60, ge=0)
    pump_outlet: int = Field(default=4, ge=1, le=5)
    light_outlet: int = Field(default=1, ge=1, le=5)
    exhaust_outlet: int = Field(default=2, ge=1, le=5)
    fan_outlet: int = Field(default=3, ge=1, le=5)
    retention_days: int = Field(default=30, ge=1, le=365)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


def load(path: Path | None = None) -> Settings:
    selected = (path or default_config()).expanduser().resolve()
    values = tomllib.loads(selected.read_text())
    values["data_dir"] = Path(values["data_dir"]).expanduser()
    settings = Settings(**values)
    mapping = [
        settings.pump_outlet,
        settings.light_outlet,
        settings.exhaust_outlet,
        settings.fan_outlet,
    ]
    if len(set(mapping)) != len(mapping):
        raise ValueError("Each device must have a separate outlet")
    return settings


def initialize(path: Path, device: str, enable_controls: bool = False) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    data = Path.home() / ".local" / "share" / "spiderfarmer-growbridge"
    # repr-independent TOML strings; JSON basic strings are valid TOML strings here.
    import json

    content = (
        f"device = {json.dumps(device)}\n"
        f"token = {json.dumps(secrets.token_urlsafe(32))}\n"
        f"data_dir = {json.dumps(str(data))}\n"
        f"controls_enabled = {str(enable_controls).lower()}\n"
        "port = 8766\nmax_pump_seconds = 5\npump_cooldown_seconds = 60\n"
        "light_outlet = 1\nexhaust_outlet = 2\nfan_outlet = 3\npump_outlet = 4\n"
    )
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(content)
