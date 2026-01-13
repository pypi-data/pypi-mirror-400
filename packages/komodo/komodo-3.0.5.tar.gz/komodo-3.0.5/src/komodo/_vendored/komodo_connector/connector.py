from typing import Any, Optional

from komodo._vendored.komodo_connector.connection import Connection
from komodo._vendored.komodo_connector.constants import (
    DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT,
    SNOWFLAKE_MAIN_ACCOUNTS,
    VENDOR_CONNECTION_STRING_MAP,
    Vendors,
)
from komodo._vendored.komodo_connector.models import (
    KomodoAuthenticationParams,
)
from komodo._vendored.komodo_connector.setup_driver import (
    load_driver,
    parse_komodo_url,
)


def connect(
    connection_string: Optional[str] = None,
    *,
    vendor: Vendors = Vendors.SNOWFLAKE,
    account_id: Optional[str] = None,
    profile_id: Optional[str] = None,
    secret: Optional[str] = None,
    port: Optional[str] = None,
    protocol: Optional[str] = None,
    environment: Optional[str] = None,
    komodo_host: Optional[str] = None,
    app_id: Optional[str] = None,
    **kwargs: Optional[Any],
) -> Connection:
    """
    Connects to a Komodo database using the provided connection parameters.

    Args:
        connection_string (Optional[str]): The connection string. Defaults to None.
        vendor (Vendors): The vendor of the Komodo database. Defaults to Vendors.SNOWFLAKE.
        account_id (Optional[str]): The account ID. Defaults to None.
        profile_id (Optional[str]): The profile ID. Defaults to None.
        secret (Optional[str]): The secret. Defaults to None.
        port (Optional[str]): The port number. Defaults to None.
        protocol (Optional[str]): The protocol. Defaults to None.
        environment (Optional[str]): The environment. Defaults to None.
        komodo_host (Optional[str]): The Komodo host. Defaults to None.
        app_id (Optional[str]): The application ID. Defaults to None.
        **kwargs (Optional[Any]): Additional keyword arguments.

    Returns:
        Connection: The connection object.

    Raises:
        AssertionError: Raised when required parameters are not provided.

    Example:
        ```python
        connection_string = "komodo://..."
        connection = connect(connection_string)
        connection.execute("SELECT * FROM table")
        ```
    """

    if connection_string is None:
        assert account_id is not None, "account_id cannot be None"
        assert profile_id is not None, "profile_id cannot be None"
        assert secret is not None, "secret cannot be None"
        connection_string = create_connection_string(
            vendor=vendor,
            account_id=account_id,
            profile_id=profile_id,
            secret=secret,
            port=port,
            protocol=protocol,
            environment=environment,
            komodo_host=komodo_host,
            app_id=app_id,
        )

    vendor = connection_string.split("://", 1)[1].split("+", 1)[0]
    if vendor not in Vendors.values():
        raise ValueError(f"Invalid vendor: {vendor}")

    komodo_account_id = connection_string.split("@")[1].split(":")[0]

    # Temporary override to native snowflake connector for legacy connections
    if vendor == Vendors.SNOWFLAKE and komodo_account_id in SNOWFLAKE_MAIN_ACCOUNTS:
        connection_string = connection_string.replace(vendor, Vendors.SNOWFLAKE_NATIVE.value, 1)
    driver_name, connection_config = parse_komodo_url(connection_string)
    connection_config_dict = dict(connection_config)
    connection_config_dict["query_params"] = {**connection_config_dict.get("query_params", {}), **kwargs}
    driver, connection_creator = load_driver(driver_name)
    return connection_creator(driver, connection_config_dict).create()


def create_connection_string(
    *,
    vendor: Vendors,
    account_id: str,
    profile_id: str,
    secret: str,
    port: Optional[str],
    protocol: Optional[str],
    environment: Optional[str],
    komodo_host: Optional[str],
    app_id: Optional[str],
) -> str:
    """
    Creates a connection string for a given vendor, account, profile, secret, and optional connection parameters.

    Returns:
        str: The generated connection string.

    """

    auth_params = KomodoAuthenticationParams(
        komodo_account=account_id,
        komodo_user=profile_id,
        komodo_token=secret,
    )
    port = port or DEV_KOMODO_PROXY_SERVICE_DEFAULT_PORT
    return build_connection_string(
        vendor,
        auth_params,
        port=port,
        protocol=protocol,
        environment=environment,
        komodo_host=komodo_host,
        app_id=app_id,
    )


def build_connection_string(
    vendor: Vendors,
    auth_params: KomodoAuthenticationParams,
    port: Optional[str] = None,
    protocol: Optional[str] = None,
    environment: Optional[str] = None,
    komodo_host: Optional[str] = None,
    app_id: Optional[str] = None,
) -> str:
    """
    Creates a connection string for a Komodo database based on the provided parameters.

    Args:
        vendor (Vendors): The vendor of the Komodo database.
        auth_params (KomodoAuthenticationParams): The authentication parameters.
        port (Optional[str]): The port number. Defaults to None.
        protocol (Optional[str]): The protocol. Defaults to None.
        environment (Optional[str]): The environment. Defaults to None.
        komodo_host (Optional[str]): The Komodo host. Defaults to None.

    Returns:
        str: The generated connection string.
    """

    connection_string = f"komodo://{VENDOR_CONNECTION_STRING_MAP[vendor]}+{auth_params.komodo_user}:{auth_params.komodo_token}@{auth_params.komodo_account}:{port}"

    query_params = []
    if protocol is not None:
        query_params.append(f"protocol={protocol}")
    if environment is not None:
        query_params.append(f"env={environment}")
    if komodo_host is not None:
        query_params.append(f"komodo_host={komodo_host}")
    if app_id is not None:
        query_params.append(f"app_id={app_id}")

    if query_params:
        connection_string += "?" + "&".join(query_params)
    return connection_string
