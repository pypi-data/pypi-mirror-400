from importlib.metadata import version
import os
import typer

from .login import login, jwt
from .account import account_app
from .auxiliary import marmot, docs
from .service_principal import service_principal_app
from .feedback import feedback

__version__ = version("komodo")

app = typer.Typer(
    name="komodo",
    help="Komodo CLI - Build the evidentiary standard",
    add_completion=False,
    invoke_without_command=True,
)


@app.callback()
def callback(ctx: typer.Context, version: bool = typer.Option(False, "--version", "-v", help="Show the version and exit.")):
    """
    Komodo CLI - A command-line interface for managing Komodo workspaces and applications.

    Use this CLI to:
    • Login and manage authentication
    • Set and get account information
    • Build services using BuildKit
    • Manage Komodo applications
    """
    if version:
        typer.echo(f"Komodo CLI Version: {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


app.command()(login)
app.command()(jwt)
app.command()(marmot)
app.command()(docs)
app.command()(feedback)
app.add_typer(account_app, name="account")
app.add_typer(service_principal_app, name="service-principal")

if __name__ == "__main__":
    app()
