from typing import Any, Dict, Union

from komodo._vendored.komodo_connector.connection_creators.snowflake.utils import (
    SQLALCHEMY_VERSION_1_4_0,
    sql_alchemy_version_greater_than,
)

if sql_alchemy_version_greater_than(SQLALCHEMY_VERSION_1_4_0):
    from sqlalchemy.engine import URL
else:
    from sqlalchemy.engine.url import URL

from komodo._vendored.komodo_connector.connection import Connection


class SnowflakeCreator:
    def __init__(self, driver: Any, connection_config: Dict[str, Union[str, Dict[str, str]]]) -> None:
        """
        Initializes a SnowflakeCreator instance.

        Args:
            driver: The driver used to connect to Snowflake.
            connection_config: The configuration parameters for the Komodo connection.

        """
        self.driver = driver
        self.connection_config = connection_config

    def create(self) -> Connection:
        """
        Creates a Snowflake connection.

        Returns:
            The Snowflake connection.

        """
        if (query_params := self.connection_config.get("query_params", {})) and isinstance(query_params, dict):
            environment = query_params.pop("env", None)
            komodo_host = query_params.pop("komodo_host", None)
        else:
            environment, komodo_host = None, None

        snowflake_connection = self.driver(
            user=self.connection_config["komodo_user"],
            account=self.connection_config["komodo_account"],
            komodo_credentials={
                "kh_token": self.connection_config["komodo_token"],
                "kh_account": self.connection_config["komodo_account"],
                "kh_user": self.connection_config["komodo_user"],
            },
            environment=environment,
            komodo_host=komodo_host,
            **self.connection_config["query_params"],
        )
        return Connection(snowflake_connection)

    def build_connection_url(self) -> Union[str, URL, None]:
        return None
