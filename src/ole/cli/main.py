from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

import click
from ole import __version__
from ole.core.device_fingerprint import compute_fingerprint, gather_fingerprint_inputs


@click.group(help="Offline License Engine (OLE) CLI.")
def main() -> None:
    pass


@main.command("version", help="Print version.")
def version_cmd() -> None:
    click.echo(__version__)


@main.group("device", help="Device utilities.")
def device_group() -> None:
    pass


@device_group.command("export", help="Export device information as JSON.")
@click.option("--out-dir", type=click.Path(file_okay=False, dir_okay=True, path_type=Path), required=True)
def device_export_cmd(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    fingerprint_inputs = gather_fingerprint_inputs()
    hostname = str(fingerprint_inputs.get("hostname", "unknown"))
    platform_info = fingerprint_inputs.get("platform", {})
    nonce = secrets.token_hex(16)
    fingerprint = compute_fingerprint(fingerprint_inputs, nonce)

    document = {
        "schema": "ole.device.v1",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "hostname": hostname,
        "platform": platform_info,
        "fingerprint_inputs": fingerprint_inputs,
        "nonce": nonce,
        "fingerprint": fingerprint,
    }

    output_path = out_dir / f"{hostname}.device.json"
    output_path.write_text(json.dumps(document, indent=2, sort_keys=True), encoding="utf-8")
    click.echo(str(output_path))


if __name__ == "__main__":
    main()
