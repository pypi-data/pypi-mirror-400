import os
from functools import wraps

import httpx
import typer

from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.text import Text


ENVIRONMENT_OPTION = typer.Option(
    None,
    "--environment",
    "-E",
    help="Specify the environment (e.g., production or integration). Defaults to production.",
)

def resolve_environment(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "environment" in kwargs:
            kwargs["environment"] = get_environment(kwargs["environment"])
        return func(*args, **kwargs)

    return wrapper


def get_environment(environment_flag: str, default: str = "production") -> str:
    """
    Get the environment setting.
    Priority: environment_flag > KOMODO_ENVIRONMENT env var > 'production' default
    """

    return environment_flag or os.getenv("KOMODO_ENVIRONMENT") or default


def get_session_and_settings(environment: str) -> tuple:
    """Get authenticated session, settings, and console for API calls"""
    from komodo.config import SDKSettings
    from komodo.auth.Session import Session
    env = environment.lower()
    settings = SDKSettings(environment=env)
    console = Console()
    session = Session(environment=env)

    credentials = session.load_credentials()
    if not credentials:
        console.print(Text("No access token found. Please login first.", style="bold red"))
        raise typer.Exit(code=1)

    return session, settings, console, credentials


def handle_api_error(response: httpx.Response, console: Console, operation: str, custom_error_messages: Optional[Dict[int, str]] = None) -> None:
    """Handle API errors with proper error messages"""
    if custom_error_messages and response.status_code in custom_error_messages:
        console.print(Text(custom_error_messages[response.status_code], style="bold red"))
        raise typer.Exit(code=1)

    if response.status_code == 401:
        console.print(Text("Authentication failed. Please run 'komodo login' first.", style="bold red"))
        raise typer.Exit(code=1)
    elif response.status_code == 403:
        console.print(Text("Access denied. You don't have permission to perform this operation.", style="bold red"))
        raise typer.Exit(code=1)
    elif response.status_code == 404:
        console.print(Text("Resource not found.", style="bold red"))
        raise typer.Exit(code=1)
    elif response.status_code == 422:
        try:
            error_data = response.json()
            console.print(Text(f"Validation error: {error_data}", style="bold red"))
        except:
            console.print(Text("Validation error occurred.", style="bold red"))
        raise typer.Exit(code=1)
    else:
        console.print(Text(f"API error during {operation}: {response.status_code} - {response.text}", style="bold red"))
        raise typer.Exit(code=1)


def get_log_content(url: str, console: Console) -> str:
    """Fetch a presigned URL from a given URL"""
    with httpx.Client() as client:
        try:
            return client.get(url).text
        except httpx.RequestError as e:
            console.print(Text(f"Network error during fetch_presigned_url: {e}", style="bold red"))
            raise typer.Exit(code=1)


def make_api_request(method: str, url: str, headers: Dict[str, str], json_data: Optional[Dict[str, Any]] = None, console: Console = None, operation: str = "API call", custom_error_messages: Optional[Dict[int, str]] = None) -> Dict[str, Any]:
    """Make an API request with proper error handling"""
    if console is None:
        console = Console()
    with httpx.Client() as client:
        try:
            if method.upper() == "GET":
                response = client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = client.post(url, headers=headers, json=json_data)
            elif method.upper() == "PUT":
                response = client.put(url, headers=headers, json=json_data)
            elif method.upper() == "DELETE":
                response = client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code == 200:
                return response.json()
            else:
                handle_api_error(response, console, operation, custom_error_messages)

        except httpx.RequestError as e:
            console.print(Text(f"Network error during {operation}: {e}, {url}", style="bold red"))
            raise typer.Exit(code=1)


def get_apps_api_url(environment: str) -> str:
    """
    Get the API URL for the given environment.

    Priority: KOMODO_ENVIRONMENT env var > command flag > 'production' default
    """

    if environment == "integration":
        return "https://developer-platform-apps.internal.staging.onkomodo.com/apps-integration/v1/"
    else:
        return "https://api.khinternal.net/apps-production/v1/"


def get_platform_infrastructure_api_url(environment: str) -> str:
    """Get the API URL for the given environment"""
    if environment == "integration":
        return "https://developer-platform-infra.internal.dev.onkomodo.com/v1"
    else:
        return "https://developer-platform-infra.internal.onkomodo.com/v1"


def print_table(data: List[Dict[str, Any]], title: str, priority_keys: List[str] = [], console: Console = None) -> None:
    if console is None:
        console = Console()
    if not data:
        console.print(Text(f"No {title} found.", style="bold yellow"))
        return

    table = Table(title=title, show_header=True, header_style="bold cyan")

    # Dynamically add columns based on the keys in the first account
    # Sort keys to have a consistent column order
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())

    # Order columns: priority keys first, then remaining keys alphabetically
    ordered_keys = [k for k in priority_keys if k in all_keys]
    remaining_keys = sorted([k for k in all_keys if k not in priority_keys])
    column_keys = ordered_keys + remaining_keys

    # Add columns to table
    for key in column_keys:
        # Format column names nicely
        column_name = key.replace("_", " ").title()
        table.add_column(column_name, style="green")

    # Add rows
    for item in data:
        row_values = [str(item.get(key, "")) for key in column_keys]
        table.add_row(*row_values)

    console.print(table)

def get_headers(access_token: str, account_id: str | None = None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    if account_id:
        headers["x-account-id"] = account_id
    if "KOMODO_SESSION_ID" in os.environ:
        headers["x-session-id"] = os.environ["KOMODO_SESSION_ID"]
    if "KOMODO_USER_ID" in os.environ:
        headers["x-user-id"] = os.environ["KOMODO_USER_ID"]
    if "KOMODO_USER_TYPE" in os.environ:
        headers["x-user-type"] = os.environ["KOMODO_USER_TYPE"]
    if "KOMODO_ORGANIZATION_ID" in os.environ:
        headers["x-organization-id"] = os.environ["KOMODO_ORGANIZATION_ID"]
    if "KOMODO_DEVICE_ID" in os.environ:
        headers["x-device-id"] = os.environ["KOMODO_DEVICE_ID"]
    return headers
