# Validation status — v0.2.0

Recorded on 2026-10-29.

## Verified on this Mac

- macOS 27.2, Apple Silicon, Python 3.14.4.
- AC5 advertising as SF-GGS-PS5; firmware reports 3.2, plaintext BLE protocol v1.
- The native transport scans, connects, subscribes and delivers live telemetry to the daemon.
- The per-user background service starts through launchd and stores local history.
- An actual MCP stdio client discovers all eight tools and reads live status/history.
- A light command retaining the current brightness is acknowledged and confirmed by device readback.
- Repeating that MCP request with the same request ID returns the stored receipt.
- Thirty-one automated tests pass using synthetic device data, including pump timing,
  missing acknowledgements, cancellation, durable recovery, idempotency and auth checks.
- Wheel and source distributions build successfully and include the native helper source.

Before packaging, the independent local prototype also physically verified outlets 1–4,
light levels 20/30%, exhaust levels 25/35%, fan gears 1/2, and a roughly five-second pump
pulse. Physical operation was confirmed by the operator. The new daemon's pump failure
cases are exercised with a simulator; packaging validation does not trigger another
physical watering pulse.

## Local dashboard validation

- Browser-session exchange, one-use link expiry, HttpOnly cookie, revocation, and same-origin control checks.
- History sampling covers the full selected window; CSV exports retain every raw sample and reject formula-like nonnumeric sensor fields.
- Browser checks with synthetic devices cover a brightness change, a finite pump pulse, Chinese/English switching and CSV download.
- Narrow-screen controls were inspected at 375 pixels with no horizontal page overflow.
- The live dashboard was connected to the real AC5. A browser brightness write retained the existing 20% value and passed controller readback. Physical pump pulses are not part of interface QA.

## Not yet verified

- Raspberry Pi radio, BlueZ permissions and user-service startup on an actual Pi.
- Encrypted protocol v2: intentionally unsupported; control is rejected.
- Power-loss behavior, unattended watering and long-duration reconnect endurance.
- Other controller models or firmware versions.

CI uses simulated hardware on Linux and macOS. A passing Linux CI run validates Python
behavior and packaging, not a Raspberry Pi BLE link.
