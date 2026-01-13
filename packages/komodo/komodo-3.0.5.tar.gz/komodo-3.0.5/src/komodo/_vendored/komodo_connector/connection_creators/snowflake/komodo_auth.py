from __future__ import annotations

import logging
from enum import Enum, unique
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import requests

from komodo._vendored.komodo_connector.connection_creators.snowflake.utils import (
    SNOWFLAKE_VERSION_3_0_0,
    sf_connector_version_greater_than,
)
from komodo._vendored.komodo_connector.setup_driver import Environment, get_proxy_host_port

if sf_connector_version_greater_than(SNOWFLAKE_VERSION_3_0_0):
    from snowflake.connector.auth import AuthByPlugin
else:
    from snowflake.connector.auth_by_plugin import AuthByPlugin

if TYPE_CHECKING:
    from snowflake.connector.network import SnowflakeRestful

KEY_PAIR_AUTHENTICATOR = "SNOWFLAKE_JWT"
logger = logging.getLogger(__name__)


@unique
class KomodoAuthType(Enum):
    KOMODO_PROXY = "KOMODO_PROXY"


class AuthByKomodoProxy(AuthByPlugin):
    """OAuth Based Authentication.

    Works by accepting an OAuth token and using that to authenticate.
    """

    @property
    def type_(self) -> KomodoAuthType:
        return KomodoAuthType.KOMODO_PROXY

    @property
    def assertion_content(self) -> Union[str, None]:
        """Returns the token."""
        return self._token

    def __init__(
        self, kh_token: str, kh_account: str, kh_user: str, komodo_env: str, komodo_host: Optional[str] = None
    ) -> None:
        """Initializes an instance with an OAuth Token."""
        super().__init__()
        self._token: Optional[str] = kh_token
        self._account_id: Optional[str] = kh_account
        self._kh_user: Optional[str] = kh_user
        self._komodo_env: Optional[Environment] = komodo_env
        self._komodo_host: Optional[str] = komodo_host
        self._session = requests.Session()

    def reset_secrets(self) -> None:
        self._token = None
        self._account_id = None
        self._kh_user = None

    def _send_request(self, url: str, params: Dict[str, str], headers: Dict[str, str]) -> requests.Response:
        """Send a GET request and return the response."""
        response = self._session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    def authenticate(self, *args, **kwargs) -> None:  # type: ignore
        """We do not use this method."""
        pass

    def prepare(self, conn: "SnowflakeRestful", **kwargs: Any) -> None:
        """
        Prepare for the authentication process.
        Update the host of the connection with the received host value.
        """
        try:
            conn._rest._host, conn._rest._port = get_proxy_host_port(self._komodo_env, self._komodo_host)
            conn._rest.kh_account = self._account_id
            conn._rest.kh_token = self._token
            conn._rest.kh_user = self._kh_user
            if not sf_connector_version_greater_than(SNOWFLAKE_VERSION_3_0_0):
                conn._rest._token = self._token
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def reauthenticate(self, **kwargs: Any) -> dict[str, bool]:
        return {"success": False}

    def update_body(self, body: dict[Any, Any]) -> None:
        body["data"]["AUTHENTICATOR"] = KEY_PAIR_AUTHENTICATOR
