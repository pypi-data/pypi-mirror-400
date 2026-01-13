import os
import typer

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from cli.util import ENVIRONMENT_OPTION, get_headers, make_api_request, print_table, resolve_environment

service_principal_app = typer.Typer(short_help="Manage Service Principals", no_args_is_help=True)


def get_proxy_url(environment: str) -> str:
    if environment.lower() == "integration":
        return "https://connector-gateway.staging.onkomodo.com/internal/service-principals"
    else:
        return "https://connector-gateway.onkomodo.com/internal/service-principals"


@service_principal_app.command("create")
@resolve_environment
def create_service_principal(
    environment: str = ENVIRONMENT_OPTION,
    name: str = typer.Option(..., "--name", "-n", help="The name of the service principal"),
    description: str = typer.Option(..., "--description", "-d", help="The description of the service principal"),
):
    """Create a new service principal."""
    from komodo.auth.Session import Session

    session = Session(environment=environment)
    credentials = session.load_credentials()
    console = Console()
    if not credentials.access_token:
        console.print(Text("No access token found. Please login first.", style="bold red"))
        raise typer.Exit(code=1)
    if not credentials.account_id:
        console.print(Text("No account ID found. Please run 'komodo account set' first.", style="bold red"))
        raise typer.Exit(code=1)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("Creating service principal...", start=True)
        try:
            url = get_proxy_url(environment)
            headers = get_headers(credentials.access_token, credentials.account_id)
            response = make_api_request(
                "POST",
                url,
                headers=headers,
                json_data={"name": name, "description": description},
                console=console,
                custom_error_messages={403: "Access denied. Only account admins can create service principals."},
            )
        except Exception as e:
            progress.stop()
            console.print(Text(f"Failed to create service principal: {e}", style="bold red"))
            raise typer.Exit(code=1)
        progress.update(task, description="Service principal created!")
    console.print(
        Text(
            f"Service principal {name} created successfully. Client ID and Client Secret are sensitive credentials and should be stored in a secure location. Client ID: {response.get('client_id')} Client Secret: {response.get('client_secret')}"
        )
    )


@service_principal_app.command("list")
@resolve_environment
def list_service_principals(environment: str = ENVIRONMENT_OPTION):
    """List all service principals."""
    from komodo.auth.Session import Session

    session = Session(environment=environment)
    credentials = session.load_credentials()
    console = Console()
    if not credentials.access_token:
        console.print(Text("No access token found. Please login first.", style="bold red"))
        raise typer.Exit(code=1)
    if not credentials.account_id:
        console.print(Text("No account ID found. Please run 'komodo account set' first.", style="bold red"))
        raise typer.Exit(code=1)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("Fetching service principals...", start=True)
        try:
            url = get_proxy_url(environment)
            headers = get_headers(credentials.access_token, credentials.account_id)
            response = make_api_request("GET", url, headers=headers, console=console)
            service_principals = response.get("service_principals", [])
        except Exception as e:
            progress.stop()
            console.print(Text(f"Failed to fetch service principals: {e}", style="bold red"))
            raise typer.Exit(code=1)
        progress.update(task, description="Service principals fetched!")
    print_table(service_principals, "Komodo Service Principals", ["service_principal_id", "name", "description", "created_at"], console=console)


@service_principal_app.command("delete")
@resolve_environment
def delete_service_principal(environment: str = ENVIRONMENT_OPTION, service_principal_id: str = typer.Option(..., "--service-principal-id", "-s", help="The ID of the service principal to delete")):
    """Delete a service principal."""
    from komodo.auth.Session import Session

    session = Session(environment=environment)
    credentials = session.load_credentials()
    console = Console()
    if not credentials.access_token:
        console.print(Text("No access token found. Please login first.", style="bold red"))
        raise typer.Exit(code=1)
    if not credentials.account_id:
        console.print(Text("No account ID found. Please run 'komodo account set' first.", style="bold red"))
        raise typer.Exit(code=1)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("Deleting service principal...", start=True)
        try:
            url = get_proxy_url(environment) + f"/{service_principal_id}"
            headers = get_headers(credentials.access_token, credentials.account_id)
            make_api_request("DELETE", url, headers=headers, console=console, custom_error_messages={403: "Access denied. Only account admins can delete service principals."})
        except Exception as e:
            progress.stop()
            console.print(Text(f"Failed to delete service principal: {e}", style="bold red"))
            raise typer.Exit(code=1)
        progress.update(task, description="Service principal deleted!")
    console.print(Text(f"Service principal {service_principal_id} deleted successfully.", style="bold green"))
