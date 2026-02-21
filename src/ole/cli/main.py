from __future__ import annotations

import click
from ole import __version__


@click.group(help="Offline License Engine (OLE) CLI.")
def main() -> None:
    pass


@main.command("version", help="Print version.")
def version_cmd() -> None:
    click.echo(__version__)


if __name__ == "__main__":
    main()