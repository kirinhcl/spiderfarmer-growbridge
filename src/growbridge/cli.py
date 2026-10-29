import argparse
import asyncio
import fcntl
import json
import logging
import os
from pathlib import Path

from . import __version__
from .config import default_config, initialize, load


def main():
    parser = argparse.ArgumentParser(description="Local Spider Farmer BLE service and MCP tools")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--config", type=Path, default=default_config())
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser(
        "init", help="Create private configuration without overwriting existing files"
    )
    init.add_argument(
        "--device", required=True, help="Address/UUID returned by scan on this machine"
    )
    init.add_argument("--enable-controls", action="store_true")
    sub.add_parser("scan", help="Scan nearby Spider Farmer devices")
    sub.add_parser("serve", help="Run the single-owner BLE service and loopback HTTP API")
    sub.add_parser("mcp", help="Run MCP over stdio; connects to the already-running daemon")
    sub.add_parser("status", help="Read current daemon state")
    args = parser.parse_args()
    os.umask(0o077)
    if args.command == "init":
        initialize(args.config, args.device, args.enable_controls)
        print(f"Configuration created: {args.config}")
        return
    if args.command == "scan":
        from .transport import scan_devices

        data_dir = Path.home() / ".local" / "share" / "spiderfarmer-growbridge"
        data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        print(json.dumps(asyncio.run(scan_devices(data_dir)), ensure_ascii=False, indent=2))
        return
    settings = load(args.config)
    if args.command == "mcp":
        from .mcp_server import create_mcp

        create_mcp(settings).run(transport="stdio")
    elif args.command == "status":
        from .client import Client

        print(
            json.dumps(
                asyncio.run(Client(settings).call("GET", "/status")), ensure_ascii=False, indent=2
            )
        )
    elif args.command == "serve":
        import uvicorn

        from .api import create_app

        settings.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (settings.data_dir / "daemon.lock").open("w") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                parser.error("A daemon already owns this data directory")
            logging.basicConfig(level=logging.INFO)
            uvicorn.run(
                create_app(settings), host="127.0.0.1", port=settings.port, log_level="info"
            )


if __name__ == "__main__":
    main()
