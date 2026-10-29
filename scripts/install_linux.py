#!/usr/bin/env python3
"""Install a Linux systemd user service; physical Raspberry Pi validation is pending."""

import argparse
import subprocess
import sys
from pathlib import Path

from growbridge.config import default_config, load

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--uninstall", action="store_true")
parser.add_argument("--config", type=Path, default=default_config())
args = parser.parse_args()
if not sys.platform.startswith("linux"):
    parser.error("Linux only")
target = Path.home() / ".config" / "systemd" / "user" / "growbridge.service"
if args.uninstall:
    subprocess.run(["systemctl", "--user", "disable", "--now", "growbridge"], check=True)
    target.unlink(missing_ok=True)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
else:
    load(args.config)
    target.parent.mkdir(parents=True, exist_ok=True)
    executable = Path(sys.executable).parent / "growbridge"

    # systemd quoted arguments use C-style escaping, not shell quoting.
    def quote(path):
        return '"' + str(path).replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") + '"'

    target.write_text(
        "[Unit]\nDescription=Spider Farmer GrowBridge\n\n"
        f"[Service]\nType=simple\nExecStart={quote(executable)} "
        f"--config {quote(args.config.resolve())} serve\n"
        "Restart=on-failure\nRestartSec=5\nTimeoutStopSec=30\nUMask=0077\n\n"
        "[Install]\nWantedBy=default.target\n"
    )
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", "growbridge"], check=True)
    print(f"Installed: {target}. Enable user linger separately if boot-time operation is needed.")
