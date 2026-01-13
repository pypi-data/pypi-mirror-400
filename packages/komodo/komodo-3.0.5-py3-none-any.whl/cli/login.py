import pyperclip
from datetime import datetime, timezone
import typer
from rich.console import Console
from rich.text import Text

from cli.account import fetch_accounts
from cli.util import resolve_environment, ENVIRONMENT_OPTION


@resolve_environment
def login(environment: str = ENVIRONMENT_OPTION):
    """Authenticate and save credentials."""
    from komodo.auth.Session import CredentialsFileDefaultProvider, Session
    from komodo.auth.constants import KOMODO_IDP_API_SCOPE
    import komodo.auth.OAuthFlows as oauthflows
    from komodo.config import SDKSettings
    console = Console()

    settings = SDKSettings(environment=environment)
    oauth = oauthflows.OAuthFlows(domain=settings.komodo_idp_domain, rbac_url=settings.komodo_external)
    try:
        tokens = oauth.device_authorization(settings.komodo_client_id, settings.komodo_idp_audience, KOMODO_IDP_API_SCOPE, rich_console=console)

        provider = CredentialsFileDefaultProvider(settings)
        file_path = provider.set_credentials(environment, tokens)

        session = Session(environment=environment)
        credentials = session.load_credentials()
        formatted_expires_at = datetime.fromtimestamp(int(tokens['expires_at']), tz=timezone.utc).strftime('%H:%M UTC on %d %B %Y')
        message = f"✏️ Success! Credentials written to: {file_path}\n Credentials valid until {formatted_expires_at}"
        if credentials.access_token:
            accounts = fetch_accounts(credentials.access_token, settings.komodo_external)
            if len(accounts) == 1:
                account_id = list(accounts.values())[0]
                account_slug = list(accounts.keys())[0]
                provider = CredentialsFileDefaultProvider(settings)
                provider.set_credentials(environment, {"account_id": account_id, "account_slug": account_slug})
                message += f"\n Using account: {account_slug} ({account_id})"
        console.print(Text(message, style="bold green"))
    except Exception as e:
        console.print(Text(f"Device authorization failed: {e}", style="bold red"))


@resolve_environment
def jwt(environment: str = ENVIRONMENT_OPTION):
    """Display access token and copy to clipboard."""
    from komodo.auth.Session import Session
    session = Session(environment=environment)
    console = Console()
    token = session.access_token
    if not token:
        console.print(Text("No access token found. Please `komodo login` first.", style="bold red"))
        raise typer.Exit(code=1)
    console.print(Text(token))
    try:
        pyperclip.copy(token)
        console.print(Text("📎 JWT copied to clipboard", style="bold green"))
    except Exception:
        console.print(Text("Could not copy to clipboard. Please copy manually.", style="bold red"))
