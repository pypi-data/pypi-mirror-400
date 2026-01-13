from typing import TYPE_CHECKING, Any, Dict, Union

import httpx

from komodo._vendored.komodo_connector.connection import Connection

HTTP_TOTAL_TIMEOUT = 120
HTTP_CONNECTION_TIMEOUT = 60

timeout = httpx.Timeout(HTTP_TOTAL_TIMEOUT, connect=HTTP_CONNECTION_TIMEOUT)
if TYPE_CHECKING:
    from sqlalchemy.engine import URL


class SnowflakeNativeCreator:
    def __init__(self, driver: Any, connection_config: Dict[str, Any]) -> None:
        """
        Initializes a SnowflakeNativeCreator instance.

        Args:
            driver: The driver used to connect to Snowflake.
            connection_config: The configuration parameters for the Snowflake connection.

        """
        self.driver = driver
        self.connection_config = {
            "user": connection_config["komodo_user"],
            "password": connection_config["komodo_token"],
            "account": connection_config["komodo_account"],
            "session_parameters": connection_config.get("query_params", {}).get("session_parameters", {}),
        }

    def create(self) -> Connection:
        """
        Creates a Snowflake connection using the provided configuration parameters.

        Returns:
            The Snowflake connection.

        """
        return Connection(self.driver(**self.connection_config))

    def build_connection_url(self) -> Union[str, "URL", None]: ...
