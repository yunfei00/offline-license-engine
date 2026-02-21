from __future__ import annotations

import json

from click.testing import CliRunner

from ole.cli.main import main
from ole.core.device_fingerprint import compute_fingerprint


def test_cli_imports() -> None:
    assert callable(main)


def test_device_export_writes_expected_fields(tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["device", "export", "--out-dir", str(tmp_path)])

    assert result.exit_code == 0

    files = list(tmp_path.glob("*.device.json"))
    assert len(files) == 1

    payload = json.loads(files[0].read_text(encoding="utf-8"))
    expected_keys = {
        "schema",
        "timestamp",
        "hostname",
        "platform",
        "fingerprint_inputs",
        "nonce",
        "fingerprint",
    }
    assert expected_keys.issubset(payload.keys())

    expected_fingerprint = compute_fingerprint(payload["fingerprint_inputs"], payload["nonce"])
    assert payload["fingerprint"] == expected_fingerprint


def test_fingerprint_is_deterministic_for_same_inputs_and_nonce() -> None:
    fingerprint_inputs = {
        "hostname": "example-host",
        "platform": {
            "system": "Linux",
            "release": "1",
            "version": "1.0",
            "machine": "x86_64",
        },
    }
    nonce = "0123456789abcdef"

    first = compute_fingerprint(fingerprint_inputs, nonce)
    second = compute_fingerprint(fingerprint_inputs, nonce)

    assert first == second


def test_device_export_help_shows_options() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["device", "export", "--help"])

    assert result.exit_code == 0
    assert "--out-dir" in result.output
