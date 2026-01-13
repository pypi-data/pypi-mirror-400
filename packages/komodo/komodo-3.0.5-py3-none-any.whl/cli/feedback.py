import logging

import httpx
import questionary
import typer
from rich.console import Console
from rich.text import Text

from komodo.config import SDKSettings
from komodo.auth.Session import Session
from cli.util import resolve_environment, ENVIRONMENT_OPTION

logger = logging.getLogger(__name__)

@resolve_environment
def feedback(environment: str = ENVIRONMENT_OPTION):
    """Submit feedback about the Komodo Connector."""
    console = Console()

    # Get JWT token
    settings = SDKSettings(environment=environment)
    session = Session(environment=settings.environment)
    credentials = session.load_credentials()
    
    if not credentials or not credentials.access_token:
        console.print(Text("No access token found. Please run 'komodo login' first.", style="bold red"))
        raise typer.Exit(code=1)
    
    jwt_token = credentials.access_token

    try:
        headers = {"Authorization": f"Bearer {jwt_token}", "accept": "application/json"}
        
        with httpx.Client() as client:
            response = client.get(settings.komodo_rbac_me, headers=headers, timeout=30.0)
            response.raise_for_status()
            user_data = response.json()
            email = user_data.get("email")
            
            if not email:
                console.print(Text("Can't retrieve email of authenticated user", style="bold red"))
                raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as e:
        logger.debug(f"Failed to get email from RBAC API: {e}", exc_info=True)
        console.print(Text("Can't retrieve email of authenticated user", style="bold red"))
        raise typer.Exit(code=1) from e

    # Prompt for feedback
    feedback_text = questionary.text("Enter your feedback or bug report:", multiline=True).ask()
    if not feedback_text:
        console.print(Text("Feedback is required. Exiting.", style="bold red"))
        raise typer.Exit(code=1)

    url = f"{settings.proxy_domain}/feedback"
    payload = {"email": email, "body": feedback_text}
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

    # Send POST request
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            console.print(Text("Your feedback has been sent!", style="bold green"))
    except httpx.HTTPStatusError as e:
        console.print(Text("Failed to send feedback. Please try again later.", style="bold red"))
        logger.debug(f"Server response: {e.response.status_code} - {e.response.text}")
        raise typer.Exit(code=1) from e
    except httpx.RequestError as e:
        console.print(Text("Failed to send feedback. Please check your connection and try again.", style="bold red"))
        logger.debug(f"Request error: {e}")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(Text("An unexpected error occurred while sending feedback.", style="bold red"))
        logger.debug(f"Unexpected error: {e}")
        raise typer.Exit(code=1) from e

