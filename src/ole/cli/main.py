from __future__ import annotations

import typer
from ole import __version__

app = typer.Typer(add_completion=False)

@app.command()
def version() -> None:
    """"Print version.""""
    typer.echo(__version__)

def main() -> None:
    app()

if __name__ == "__main__":
    main()
