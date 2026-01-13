from functools import singledispatch
from importlib import import_module
from typing import Dict, Optional, Tuple, Union
from urllib.parse import parse_qsl, urlparse

from sqlalchemy.engine.url import URL

from komodo._vendored.komodo_connector.connection_creators.snowflake.creator import SnowflakeCreator
from komodo._vendored.komodo_connector.connection_creators.snowflake_native.creator import (
    SnowflakeNativeCreator,
)
from komodo._vendored.komodo_connector.connection_creators.snowflake_rotate_keys.creator import (
    SnowflakeRotateKeysCreator,
)
from komodo._vendored.komodo_connector.constants import DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT, KOMODO_PROXY_HOST, Environment
from komodo._vendored.komodo_connector.creator import ConnectionCreator
from komodo._vendored.komodo_connector.models import (
    DriverConfig,
    KomodoConnectionConfig,
)

# Do not import the driver classes in this module here to avoid the memory overhead of loading all the drivers
# We will dynamically load the required driver classes in the load_driver function


DRIVERS_MAP: Dict[str, DriverConfig] = {
    # SnowflakeCreator - routes all connections through the proxy
    "snowflake": DriverConfig(
        driver_module_path="komodo._vendored.komodo_connector.connection_creators.snowflake.connect.KomodoSnowflakeConnection",
        driver_creator_class=SnowflakeCreator,
    ),
    # SnowflakeRotateKeysCreator - routes all connections directly to snowflake,
    # but fetches temporary snowflake credentials from the proxy and rotates them
    "snowflake-keys": DriverConfig(
        driver_module_path="snowflake.connector.connect",
        driver_creator_class=SnowflakeRotateKeysCreator,
    ),
    # SnowflakeNativeCreator - routes all connections directly to snowflake
    "snowflake-native": DriverConfig(
        driver_module_path="snowflake.connector.connect",
        driver_creator_class=SnowflakeNativeCreator,
    ),
}


@singledispatch
def parse_komodo_url(url: str) -> Tuple[str, KomodoConnectionConfig]:
    """
    The `parse_url` function takes a URL as input and returns a tuple containing the vendor name and a
    dictionary of parsed components from the URL.

    :param url: The `url` parameter is a string that represents a URL
    :return: The function `parse_url` returns a tuple containing two elements. The first element is a
    string representing the vendor, and the second element is a dictionary containing the
    connection parameters
    """
    parsed_url = urlparse(url)
    vendor = parsed_url.netloc.split("+", 1)[0]

    user_auth, account_config = parsed_url.netloc.split("@", 1)
    komodo_user_string, komodo_token = user_auth.split(":")[:2]
    komodo_user = komodo_user_string.split("+", 1)[1]
    komodo_account, komododb_port = (
        account_config.split(":", 1)
        if ":" in account_config
        else (account_config, DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT)
    )

    query_param_dict: Dict[str, Union[str, Dict[str, str]]] = dict(parse_qsl(parsed_url.query))

    return (
        vendor,
        KomodoConnectionConfig(
            komodo_account=komodo_account,
            komododb_port=int(komododb_port),
            komodo_user=komodo_user,
            komodo_token=komodo_token,
            query_params=query_param_dict,
        ),
    )


@parse_komodo_url.register
def parse_url_sqlalchemy_URL(url: URL) -> Tuple[str, KomodoConnectionConfig]:
    """
    The function `parse_url_sqlalchemy_URL` takes a URL object and returns a tuple containing the host,
    database, username, password, and port extracted from the URL.
    """
    vendor, komodo_user_string = url.username.split("+", 1)
    komodo_user = komodo_user_string.split("+", 1)[1]
    komodo_port = url.port or DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT
    return (
        vendor,
        KomodoConnectionConfig(
            komodo_account=url.host,
            komododb_port=int(komodo_port),
            komodo_user=komodo_user,
            komodo_token=url.password,
            query_params=url.query,
        ),
    )


def load_driver(driver_name: str) -> Tuple[object, ConnectionCreator]:
    driver_config = DRIVERS_MAP[driver_name]
    module_path, driver_name = driver_config.driver_module_path.rsplit(".", 1)

    driver_module = import_module(module_path)
    # TODO: Support multiple driver versions by reloading the driver module with the specified version
    # importlib.reload(driver_module)

    driver = getattr(driver_module, driver_name)
    return driver, driver_config.driver_creator_class


def get_proxy_host_port(
    komodo_env: Environment = Environment.PROD, komodo_host: Optional[str] = None
) -> Tuple[str, str]:
    host = komodo_host if (komodo_env != Environment.PROD and komodo_host) else KOMODO_PROXY_HOST[komodo_env]
    port = DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT
    return host, port
