import asyncio
import logging
import warnings

from komodo.client import Client
from komodo._vendored.komodo_connector.connector import connect
from komodo._vendored.komodo_connector.connection_creators.snowflake.cursor import KomodoSnowflakeCursor
from komodo._vendored.komodo_connector.connection import Connection
from snowflake.connector.cursor import SnowflakeCursor
from komodo.auth.Session import Session
from komodo._vendored.snowflake_query_tag.models import SnowflakeTag, VersionedProperties

logger = logging.getLogger(__name__)

# Suppress UserWarning from pandas when using komodo_connector's Connection object, since SQLAlchemy is
# technically the only DBAPI2.0 compliant connection supported by pandas.
warnings.simplefilter(action="ignore", category=UserWarning)


class UnsetAccountError(Exception):
    """Exception raised for errors in the snowflake connection"""


def get_snowflake_connection(account_id: str | None = None, jwt: str | None = None, client_id: str | None = None, client_secret: str | None = None, profile: str | None = None) -> Connection:
    if jwt is not None and (client_id is not None or client_secret is not None):
        raise ValueError("Cannot pass in both a JWT and client_id/client_secret.")
    
    if profile is not None and (jwt is not None or client_id is not None or client_secret is not None):
        raise ValueError("Cannot specify profile along with explicit credentials (jwt, client_id, or client_secret).")

    client_kwargs = {}

    if account_id is not None:
        client_kwargs["account_id"] = account_id

    if profile is not None:
        client_kwargs["auth_session"] = Session(profile=profile)
        if account_id is not None and client_kwargs["auth_session"].account_id is not None:
            raise ValueError(
             "The account_id parameter was provided, but the selected profile also contains an account_id. "
             "Please specify the account_id in only one location."
             )


    elif jwt is not None:
        client_kwargs["auth_session"] = Session(access_token=jwt)
    elif client_id is not None and client_secret is not None:
        client_kwargs["auth_session"] = Session(client_id=client_id, client_secret=client_secret)
    elif client_id is not None or client_secret is not None:
        raise ValueError("Invalid credentials provided. Please provide either a JWT or both client_id and client_secret.")

    client = Client(**client_kwargs)

    jwt = client.auth.access_token
    account_id = client.x_account_id

    if account_id is None:
        raise UnsetAccountError("An account_id was not passed and could not be read from the SDK client session. Please pass an account_id or set it in your credentials file.")

    me = client.iam.get_current_identity()
    identity_id = me.user.user_id if me.user else me.service_principal.service_principal_id

    environment = client.auth._settings.environment
    env = "prod" if environment == "production" else "dev"
    # TODO: We are in the process of getting final permission to remove the snowflake query tags
    app_id = "compute"
    client_type = "eng"
    nest = "mapkit"
    service = VersionedProperties(name="mapkit", version="1.0.0", properties={})
    client = VersionedProperties(name="python_sdk", version="1.0.0", properties={})
    snowflake_tag = SnowflakeTag(type=client_type, env=env, nest=nest, account_id=account_id, user_id=identity_id, service=service, client=client)
    query_tag = snowflake_tag.model_dump_json(exclude_none=True, exclude_unset=True, by_alias=True, indent=4)

    connection = connect(
        account_id=account_id,
        profile_id=identity_id,
        secret=f"Bearer {jwt}",
        app_id=app_id,
        protocol=None,
        environment=env,
        session_parameters={"QUERY_TAG": query_tag},
    )

    cursor = connection.cursor()
    cursor.close()

    return connection


class SnowflakeException(Exception):
    """Exception raised for errors in the Map database connection"""


def is_still_running(map_connection: Connection, query_id: str) -> bool:
    """Check if a Map query is still running."""
    try:
        return map_connection.is_still_running(map_connection.get_query_status_throw_if_error(query_id))
    except Exception as err:
        raise SnowflakeException(err) from err


async def execute_query_async(
    cursor: KomodoSnowflakeCursor,
    query: str,
    query_params: list[str] | dict[str, str] | None = None,
) -> KomodoSnowflakeCursor:
    """Wrapper around the KomodoSnowflakeCursor execute_async method to execute a query 'asynchronously' and poll for completion.

    Note that because the io is still blocking, this function is not truly asynchronous and will get thrown to a sync threadpool
    in FastAPI. If you are working outside of FastAPI, you should probably use `asyncio.to_thread` to run this function.

    Parameters
    ----------
    cursor: an existing KomodoSnowflakeCursor
    query: the query to execute
    query_params: the parameters to pass to the query (optional)

    Example usage:
        connection = get_snowflake_connection(account_id=account_id, jwt=user_jwt)
        cursor = connection.cursor()
        cursor.execute("USE ROLE CUSTOMER_ROLE")
        cursor.execute("USE DATABASE DATA")
        query = "SELECT column_name, table_name FROM INFORMATION_SCHEMA.COLUMNS;"
        cursor = await execute_query_async(cursor=cursor, query=query)
        rows = cursor.fetchall()
    """
    logger.info(f"Executing query:\n{query} with {query_params=}")
    cursor.execute_async(query, query_params)
    query_id = cursor.sfqid
    while is_still_running(cursor.connection, query_id):
        await asyncio.sleep(1)

    cursor.get_results_from_sfqid(query_id)
    return cursor
