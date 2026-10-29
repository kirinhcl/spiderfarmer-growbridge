#!/usr/bin/env python3
"""Install the daemon as a per-user LaunchAgent using this Python environment."""

import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path

from growbridge.config import default_config, load
from growbridge.transport import build_native

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--uninstall", action="store_true")
parser.add_argument("--config", type=Path, default=default_config())
args = parser.parse_args()
if sys.platform != "darwin":
    parser.error("macOS only")
label = "local.growbridge.daemon"
domain = f"gui/{os.getuid()}"
target = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"
if args.uninstall:
    subprocess.run(["launchctl", "bootout", f"{domain}/{label}"], check=False)
    target.unlink(missing_ok=True)
    print("GrowBridge LaunchAgent removed")
else:
    settings = load(args.config)
    settings.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    build_native(settings.data_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    executable = Path(sys.executable).parent / "growbridge"
    info = {
        "Label": label,
        "ProgramArguments": [str(executable), "--config", str(args.config.resolve()), "serve"],
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 10,
        "ProcessType": "Interactive",
        "StandardOutPath": str(settings.data_dir / "daemon.stdout.log"),
        "StandardErrorPath": str(settings.data_dir / "daemon.stderr.log"),
    }
    target.write_bytes(plistlib.dumps(info))
    target.chmod(0o600)
    subprocess.run(["launchctl", "bootout", f"{domain}/{label}"], capture_output=True, check=False)
    subprocess.run(["launchctl", "bootstrap", domain, str(target)], check=True)
    print(f"GrowBridge installed and started: {target}")
