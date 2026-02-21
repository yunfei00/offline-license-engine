from __future__ import annotations

from ole.cli.main import main

def test_cli_imports() -> None:
    assert callable(main)