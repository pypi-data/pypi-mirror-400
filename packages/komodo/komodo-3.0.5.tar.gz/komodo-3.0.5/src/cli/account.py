from typing import Any

import httpx
import pyperclip
import typer
from questionary import Choice, Style, select
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from cli.util import ENVIRONMENT_OPTION, get_headers,print_table, resolve_environment


def fetch_accounts(token: str, base_url: str) -> dict[str, str]:
    url = f"{base_url}/v1/iam/users/me?expand=organizations.accounts"
    headers = get_headers(token)
    with httpx.Client() as client:
        resp = client.get(url, headers=headers)
        data = resp.json()

    accounts = {}
    for org in data.get("organizations", []):
        for acct in org.get("accounts", []):
            accounts[acct["slug"]] = acct["account_id"]
    return accounts


def fetch_accounts_detailed(token: str, base_url: str) -> list[dict[str, Any]]:
    """Fetch all accounts with complete metadata."""
    url = f"{base_url}/v1/iam/users/me?expand=organizations.accounts"
    headers = get_headers(token)

    with httpx.Client() as client:
        resp = client.get(url, headers=headers)
        data = resp.json()

    accounts = []
    for org in data.get("organizations", []):
        org_name = org.get("name", "")
        for acct in org.get("accounts", []):
            # Add organization name to account metadata
            acct_data = {**acct, "organization_name": org_name}
            accounts.append(acct_data)
    return accounts


account_app = typer.Typer(short_help="Get and set the Komodo Account.", no_args_is_help=True)


@account_app.command("set")
@resolve_environment
def account_set(environment: str = ENVIRONMENT_OPTION):
    """Set the Komodo Account."""
    from komodo.config import SDKSettings
    from komodo.auth.Session import Session, CredentialsFileDefaultProvider
    env = environment.lower()

    settings = SDKSettings(environment=env)
    console = Console()
    session = Session(environment=env)
    credentials = session.load_credentials()
    if not credentials.access_token:
        console.print(Text("No access token found. Please login first.", style="bold red"))
        raise typer.Exit(code=1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("Fetching accounts...", start=True)
        try:
            accounts = fetch_accounts(session.access_token, settings.komodo_external)
        except Exception as e:
            progress.stop()

            if "nodename nor servname provided, or not known" in str(e):
                console.print(Text("You are not connected to Twingate. Please connect to Twingate and try again.", style="bold red"))
            else:
                console.print(Text(f"Failed to fetch accounts: {e}", style="bold red"))

            raise typer.Exit(code=1)
        progress.update(task, description="Accounts fetched!")

    if not accounts:
        console.print(Text(f"No accounts found for this user in {env}.", style="bold red"))
        raise typer.Exit(code=1)
    max_slug_len = max(len(slug) for slug in accounts)
    choices = []
    for slug, account_id in accounts.items():
        label = f"{slug.ljust(max_slug_len)}  |  {account_id}"
        value = f"{slug}|{account_id}"
        choices.append(Choice(title=label, value=value))
    custom_style = Style(
        [
            ("qmark", "fg:#00b7c2 bold"),
            ("question", "bold"),
            ("answer", "fg:#f44336 bold"),
            ("pointer", "fg:#00b7c2 bold"),
            ("highlighted", "fg:#00b7c2 bold"),
            ("selected", "fg:#00b7c2 bold"),
            ("separator", "fg:#cc5454"),
            ("instruction", ""),
            ("text", ""),
            ("disabled", "fg:#858585 italic"),
        ]
    )
    selected = select("Select an account:", choices=choices, use_shortcuts=False, style=custom_style).ask()
    if not selected:
        console.print(Text("No account selected. Exiting.", style="bold red"))
        raise typer.Exit(code=1)
    selected_slug, selected_account_id = selected.split("|", 1)
    selected_slug = selected_slug.strip()
    selected_account_id = selected_account_id.strip()
    selected_account_id = str(selected_account_id)

    provider = CredentialsFileDefaultProvider(settings)
    file_path = provider.set_credentials(env, {"account_id": selected_account_id, "account_slug": selected_slug})

    console.print(Text(f"✏️ Account set to: {selected_slug} ({selected_account_id}) in {file_path}", style="bold green"))


@account_app.command("get")
@resolve_environment
def account_get(environment: str = ENVIRONMENT_OPTION):
    """Copy the set komodo account id to clipboard."""
    from komodo.config import SDKSettings
    from komodo.auth.Session import CredentialsFileDefaultProvider
    console = Console()
    env = environment.lower()
    settings = SDKSettings(environment=env)
    provider = CredentialsFileDefaultProvider(settings)
    creds = provider.get_credentials()
    account_id = getattr(creds, "account_id", None)
    account_slug = getattr(creds, "account_slug", None)
    if not account_id or not account_slug:
        console.print(Text("KOMODO_ACCOUNT_ID or KOMODO_ACCOUNT_SLUG not set. Please run 'komodo account set' first.", style="bold red"))
        raise typer.Exit(code=1)
    try:
        pyperclip.copy(str(account_id))
        console.print(Text(f"📎 Copied account id for {account_slug} ({account_id}) into clipboard ", style="bold green"))
    except Exception:
        console.print(Text("📎Could not copy to clipboard. Please copy manually.", style="bold red"))
        console.print(Text(f"Account id for {account_slug}: {account_id}", style="bold yellow"))


@account_app.command("list")
@resolve_environment
def account_list(environment: str = ENVIRONMENT_OPTION):
    """List the komodo accounts"""
    from komodo.config import SDKSettings
    import komodo.auth.Session as session
    env = environment.lower()

    settings = SDKSettings(environment=env)
    console = Console()
    session = session.Session(environment=env)
    credentials = session.load_credentials()
    if not credentials.access_token:
        console.print(Text("No access token found. Please login first.", style="bold red"))
        raise typer.Exit(code=1)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("Fetching accounts...", start=True)
        try:
            accounts = fetch_accounts_detailed(session.access_token, settings.komodo_external)
        except Exception as e:
            progress.stop()

            if "nodename nor servname provided, or not known" in str(e):
                console.print(Text("You are not connected to Twingate. Please connect to Twingate and try again.", style="bold red"))
            else:
                console.print(Text(f"Failed to fetch accounts: {e}", style="bold red"))

            raise typer.Exit(code=1)
        progress.update(task, description="Accounts fetched!")

    print_table(accounts, "Komodo Accounts", priority_keys=["slug", "account_id", "name", "organization_name"], console=console)

