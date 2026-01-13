import configparser
import logging
import threading
import time
import os

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from komodo.auth.constants import KOMODO_IDP_API_SCOPE
from komodo.auth.OAuthFlows import OAuthFlows
from komodo.config import SDKSettings
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExpiredCredentialsError(Exception):
    def __init__(self, message: str = "Credentials are expired and need to be refreshed."):
        super().__init__(message)
        self.message = message


class AuthenticationType(Enum):
    PASS_THROUGH = "PassThrough"
    BROWSER = "Browser"
    MACHINE_TO_MACHINE = "MachineToMachine"


class Credentials(BaseModel):
    access_token: str | None = None
    expires_at: int | None = None
    client_id: str | None = None
    client_secret: str | None = None
    account_id: str | None = None
    account_slug: str | None = None
    credential_type: AuthenticationType | None = None

    def __init__(self, **data):
        logging.debug(f"Credentials initialized with keys: {list(data.keys())}")
        super().__init__(**data)

    def refresh_needed(self) -> bool:
        """
        Check if the access token needs to be refreshed within the next 15 minutes.
        :return: True if refresh is needed, False otherwise
        """
        if self.expires_at is None:
            return None
        else:
            current_epoch_ts = time.time()
            if current_epoch_ts > (self.expires_at - 900):
                logger.debug("Access token has expired or will expire within the next 15 minutes. Refresh is needed.")
                return True
            else:
                logger.debug(f"Access token is still valid. Expires at: {self.expires_at}, Current time: {current_epoch_ts}")
                return False


class AuthProvider(ABC):
    @abstractmethod
    def get_credentials(self) -> Credentials | None:
        """
        Get credentials from their source and return them as a Credentials object.

        If no credentials are found, return None.

        Subclasses must implement this method to be used by the AuthResolver.
        :return: Credentials object or None if no credentials are found
        """


class AuthResolver:
    def __init__(self, providers: list[AuthProvider]):
        self.providers = providers

    def get_credentials(self) -> Credentials:
        logger.debug("Attempting to resolve credentials from providers.")
        for provider in self.providers:
            auth = provider.get_credentials()
            if auth:
                return auth
        return Credentials(credential_type=AuthenticationType.BROWSER)


class JwtEnvProvider(AuthProvider):
    def __init__(self, settings: SDKSettings):
        self._settings = settings

    def get_credentials(self):
        access_token = self._settings.access_token
        token_expiration = self._settings.token_expiration
        account_id = self._settings.account_id

        token_data = {}
        if access_token:
            token_data["access_token"] = access_token.get_secret_value()

        if token_expiration:
            token_data["expires_at"] = int(token_expiration)

        if account_id:
            token_data["account_id"] = str(account_id)

        if not token_data:
            return None

        token_data["credential_type"] = AuthenticationType.PASS_THROUGH
        return Credentials(**token_data)


class ClientCredentialsEnvProvider(AuthProvider):
    def __init__(self, settings: SDKSettings):
        self._settings = settings

    def get_credentials(self):
        client_id = self._settings.client_id
        client_secret = self._settings.client_secret
        account_id = self._settings.account_id

        if client_id and client_secret:
            return Credentials(
                client_id=client_id.get_secret_value(),
                client_secret=client_secret.get_secret_value(),
                account_id=account_id,
                credential_type=AuthenticationType.MACHINE_TO_MACHINE,
            )
        return None


class CredentialsFileProfileProvider(AuthProvider):
    """
    Reads credentials from a named profile section in ~/.komodo/credentials.
    Only supports service principal credentials (client_id/client_secret).
    Expects an INI file with sections like:
    [profile-name]
    client_id=...
    client_secret=...
    account_id=...
    account_slug=...
    """

    def __init__(self, settings: SDKSettings, profile_name: str):
        self._settings = settings
        self._profile_name = profile_name

    def get_credentials(self):
        credentials_path = os.path.expanduser("~/.komodo/credentials")
        if not os.path.exists(credentials_path):
            logging.warning(f"Credentials file not found at {credentials_path}. Please run `komodo login` to create it.")
            return None

        config = configparser.ConfigParser()
        try:
            config.read(credentials_path)
        except configparser.DuplicateSectionError as e:
            raise ValueError(f"Duplicate section found in credentials file at {credentials_path}. Please ensure each section header appears only once. Error: {e}") from e
        except Exception as e:
            logging.warning(f"Could not read credentials file: {e}")
            return None

        if self._profile_name not in config:
            logging.warning(f"Profile section [{self._profile_name}] not found in credentials file.")
            return None

        section = config[self._profile_name]
        client_id = section.get("client_id")
        client_secret = section.get("client_secret")
        account_id = section.get("account_id")
        account_slug = section.get("account_slug")

        if client_id and client_secret:
            creds_kwargs = {
                "client_id": client_id,
                "client_secret": client_secret,
                "credential_type": AuthenticationType.MACHINE_TO_MACHINE,
            }
            if account_id:
                creds_kwargs["account_id"] = account_id
            if account_slug:
                creds_kwargs["account_slug"] = account_slug
            return Credentials(**creds_kwargs)
        
        return None


class CredentialsFileDefaultProvider(AuthProvider):
    """
    Reads credentials from the [default] section in ~/.komodo/credentials.
    Supports JWT token credentials.
    Expects an INI file with sections like:
    [default]
    token=...
    token_expiration=...
    account_id=...
    account_slug=...
    """

    def __init__(self, settings: SDKSettings):
        self._settings = settings

    def get_credentials(self):
        credentials_path = os.path.expanduser("~/.komodo/credentials")
        if not os.path.exists(credentials_path):
            return None

        config = configparser.ConfigParser()
        try:
            config.read(credentials_path)
        except configparser.DuplicateSectionError as e:
            raise ValueError(f"Duplicate section found in credentials file at {credentials_path}. Please ensure each section header (e.g., [default]) appears only once. Error: {e}") from e
        except Exception as e:
            logging.warning(f"Could not read credentials file: {e}")
            return None

        section_name = "default"
        if section_name not in config:
            logging.warning(f"Default section [{section_name}] not found in credentials file.")
            return None

        section = config[section_name]
        token = section.get("token")
        expires_at_str = section.get("token_expiration")
        account_id = section.get("account_id")
        account_slug = section.get("account_slug")

        if token and expires_at_str:
            try:
                expires_at = int(expires_at_str)
            except ValueError:
                logging.warning(f"Invalid expiration timestamp in [{section_name}]: {expires_at_str}")
                return None
            
            creds_kwargs = {
                "access_token": token,
                "expires_at": expires_at,
            }
            if account_id:
                creds_kwargs["account_id"] = account_id
            if account_slug:
                creds_kwargs["account_slug"] = account_slug
            return Credentials(**creds_kwargs)
        
        return None

    def set_credentials(self, env: str, tokens: dict, file_path: str = None):
        """
        Write the provided tokens to the credentials file under the [default] section.
        Only update the fields provided in tokens, preserving any existing fields in the section.
        Also update/create a [session] section with komodo_environment set to the last written environment.
        """
        credentials_path = file_path or os.path.expanduser("~/.komodo/credentials")
        config = configparser.ConfigParser()
        if os.path.exists(credentials_path):
            try:
                config.read(credentials_path)
            except configparser.DuplicateSectionError as e:
                raise ValueError(f"Duplicate section found in credentials file at {credentials_path}. Please ensure each section header appears only once. Error: {e}") from e
        else:
            os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

        section_name = "default"
        if section_name not in config:
            config.add_section(section_name)
        # Update with new tokens
        for key, value in tokens.items():
            if key == "access_token":
                config.set(section_name, "token", value)
            elif key == "expires_at":
                config.set(section_name, "token_expiration", str(value))
            elif key == "account_id":
                config.set(section_name, "account_id", str(value))
            elif key == "account_slug":
                config.set(section_name, "account_slug", str(value))

        # Add/update session section with environment
        if "session" not in config:
            config.add_section("session")
        config.set("session", "komodo_environment", env)

        with open(credentials_path, "w") as f:
            config.write(f)
        return credentials_path


class Session:
    def __init__(self, access_token=None, client_id=None, client_secret=None, environment: str | None = None, profile: str | None = None):
        """
        Initialize a Session object with authentication credentials.

        Credential resolution inspired by https://github.com/boto/botocore/blob/develop/botocore/credentials.py

        :param access_token: JWT token
        :param client_id: Client ID for machine-to-machine authentication
        :param client_secret: Client secret for machine-to-machine authentication
        :param environment: Environment name (integration or production)
        :param profile: Named profile to use from credentials file (e.g., "profile-1", "default")
        """

        self._logger = logging.getLogger(__name__)

        if (client_id is not None and client_secret is not None) and (access_token is not None):
            raise ValueError("Cannot pass in both access_token and client_id/client_secret")
        
        if profile is not None and (access_token is not None or client_id is not None or client_secret is not None):
            raise ValueError("Cannot specify profile along with explicit credentials (access_token, client_id, or client_secret)")

        self._access_token = access_token
        self._client_id = client_id
        self._client_secret = client_secret
        self._profile = profile
        self._refresh_lock = threading.Lock()

        if environment:
            self._settings = SDKSettings(environment=environment)
        else:
            self._settings = SDKSettings()

        self._token_data = self.load_credentials()
        
        # Update instance attributes from loaded credentials (for profile-based credentials)
        if self._token_data and not self._access_token and not (self._client_id and self._client_secret):
            if self._token_data.client_id:
                self._client_id = self._token_data.client_id
            if self._token_data.client_secret:
                self._client_secret = self._token_data.client_secret

    def load_credentials(self) -> Credentials:
        """
        Check each of the providers in order and return the first set of credentials found.

        If the access token or client credentials were provided during initialization, then use those and
        only retrieve the stored account ID if there is one.
        """
        if self._access_token or (self._client_id and self._client_secret):
            if self._access_token:
                credential_type = AuthenticationType.PASS_THROUGH
            else:
                credential_type = AuthenticationType.MACHINE_TO_MACHINE
            return Credentials(
                access_token=self._access_token,
                client_id=self._client_id,
                client_secret=self._client_secret,
                credential_type=credential_type,
            )

        providers = [
            JwtEnvProvider(self._settings),
            ClientCredentialsEnvProvider(self._settings),
        ]
        
        # If profile is specified, use profile provider first; otherwise use default profile provider
        # If profile is 'default', use CredentialsFileDefaultProvider instead of CredentialsFileProfileProvider
        if self._profile is not None:
            if self._profile == "default":
                providers.insert(0, CredentialsFileDefaultProvider(self._settings))
            else:
                providers.insert(0, CredentialsFileProfileProvider(self._settings, self._profile))
        else:
            providers.append(CredentialsFileDefaultProvider(self._settings))
        
        resolver = AuthResolver(providers)
        creds = resolver.get_credentials()
        return creds

    @property
    def access_token(self) -> str | None:
        """
        Get the access token for the AuthSession. Represents a JWT used as the Authorization Bearer header in SDK HTTP
            requests.

        :return: JWT token
        """

        if self._token_data.refresh_needed():
            # Put a threading lock on the _token_data object to prevent multiple threads from trying to refresh the token at once
            # If the lock can't be acquired, block until it is released and the acquire it
            if self._refresh_lock.acquire(False):
                try:
                    if not self._token_data.refresh_needed():
                        return self._token_data.access_token
                    self.connect()
                    return self._token_data.access_token
                finally:
                    self._refresh_lock.release()
            else:
                with self._refresh_lock:
                    if not self._token_data.refresh_needed():
                        return self._token_data.access_token
                    self.connect()
        return self._token_data.access_token

    @property
    def expires_at(self) -> int | None:
        """
        The epoch timestamp when the access token expires

        :return: Epoch timestamp when the access token expires or None
        """
        return self._token_data.expires_at

    @property
    def account_id(self) -> str | None:
        return self._token_data.account_id if self._token_data else None

    def connect(self):
        # The integration /token endpoint is only available behind the rbac proxy url, aka /platform-rbac-stage/
        rbac_url = self._settings.komodo_external if self._settings.environment == "production" else f"{self._settings.komodo_external}/platform-rbac-stage"
        oauth = OAuthFlows(domain=self._settings.komodo_idp_domain, rbac_url=rbac_url, logger=self._logger)

        tokens = None
        match self._token_data.credential_type:
            case AuthenticationType.BROWSER:
                if self._token_data.refresh_needed():
                    self._logger.warning("Access token will expire soon. Please re-authenticate.")
                else:
                    tokens = oauth.device_authorization(
                        self._settings.komodo_client_id,
                        self._settings.komodo_idp_audience,
                        KOMODO_IDP_API_SCOPE,
                    )
            case AuthenticationType.MACHINE_TO_MACHINE:
                if self._token_data.access_token is not None:
                    if self._token_data.refresh_needed():
                        tokens = oauth.client_credentials(
                            self._client_id,
                            self._client_secret,
                        )
                else:
                    tokens = oauth.client_credentials(
                        self._client_id,
                        self._client_secret,
                    )

        if tokens is not None:
            # Preserve account_id and account_slug from original credentials when updating tokens
            creds_kwargs = {**tokens, "credential_type": self._token_data.credential_type}
            if self._token_data.account_id:
                creds_kwargs["account_id"] = self._token_data.account_id
            if self._token_data.account_slug:
                creds_kwargs["account_slug"] = self._token_data.account_slug
            self._token_data = Credentials(**creds_kwargs)
