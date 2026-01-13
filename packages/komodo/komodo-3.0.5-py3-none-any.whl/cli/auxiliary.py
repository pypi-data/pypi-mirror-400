import webbrowser

import typer
from rich.console import Console
from rich.text import Text


def _open_url_in_browser(url: str, message: str):
    """Helper to open a URL in the browser and print a message."""
    console = Console()
    try:
        success = webbrowser.open(url)
        if success:
            console.print(Text(message, style="bold green"))
        else:
            console.print(Text("Failed to open browser: Unable to launch browser", style="bold red"))
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(Text(f"Failed to open browser: {e}", style="bold red"))
        raise typer.Exit(code=1) from e

def marmot():
    """Open Marmot website in default browser."""
    url = "https://marmot.komodohealth.com"
    message = f"🌐 Opening Marmot: {url}"
    _open_url_in_browser(url, message)

def docs():
    """Open documentation website in default browser."""
    url = "https://docs.komodohealth.com"
    message = f"📚 Opening Documentation: {url}"
    _open_url_in_browser(url, message)
