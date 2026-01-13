import asyncio
import os
import threading
from typing import Any, Dict, Tuple

import httpx
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from komodo._vendored.komodo_connector.connection import Connection

HTTP_TOTAL_TIMEOUT = 120
HTTP_CONNECTION_TIMEOUT = 60

timeout = httpx.Timeout(HTTP_TOTAL_TIMEOUT, connect=HTTP_CONNECTION_TIMEOUT)


class SnowflakeRotateKeysCreator:
    """
    Initializes a SnowflakeRotateKeysCreator instance.

    Args:
        driver: The driver used to connect to Snowflake.
        connection_config: The configuration parameters for the Snowflake connection.

    Raises:
        AssertionError: If `komodo_user` is not a string.

    """

    def __init__(self, driver: Any, connection_config: Dict[str, Any]) -> None:
        self.driver = driver
        if not isinstance(connection_config["komodo_user"], str):
            raise AssertionError("komodo_user must be a string")
        self.user = connection_config["komodo_user"].split("+")[1]
        self.connection_config = connection_config

    def fetch_credentials(self) -> Dict[str, str]:
        """
        Fetches the credentials for the Snowflake connection.

        Returns:
            The fetched credentials.

        Raises:
            Exception: If the credentials cannot be fetched.

        """
        url, headers = self.build_connection_url()

        response = httpx.get(
            url,
            params={
                "kh_user": self.user,
            },
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

        if response.status_code != 200:
            raise httpx.HTTPError(
                f"Failed to fetch credentials for user {self.user} with status code {response.status_code}"
            )

        return response.json()  # type: ignore

    def create(self) -> Connection:
        """
        Creates a Snowflake connection using the fetched credentials.

        Returns:
            The Snowflake connection.

        """
        credentials = self.fetch_credentials()
        self.connection_config.update(credentials)

        private_key_str = self.connection_config["USER_PRIVATE_KEY"]

        private_key_obj = serialization.load_pem_private_key(
            private_key_str.encode(), password=None, backend=default_backend()
        )

        private_key_der_bytes = private_key_obj.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        driver = self.driver(
            user=self.user,
            account=self.connection_config["komodo_account"],
            private_key=private_key_der_bytes,
        )

        if driver.session_id:
            # Reset credentials upon a successful session creation
            self.trigger_reset_credentials()

        return Connection(driver)

    def trigger_reset_credentials(self) -> None:
        """
        Triggers the reset of credentials in a separate thread.

        """

        def run_event_loop(loop: Any) -> None:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.reset_credentials())

        # Launch the event loop in a new thread so that it doesn't block, but still runs in the background before the process exits
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=run_event_loop, args=(loop,))
        thread.start()

    async def reset_credentials(self) -> None:
        """
        Resets the credentials for the Snowflake connection.

        """
        url, headers = self.build_connection_url()
        refresh_credentials_url = f"{url}/refresh"
        async with httpx.AsyncClient(verify=os.getenv("environment") == "prod", timeout=timeout) as client:
            _ = await client.post(
                refresh_credentials_url,
                params={
                    "kh_user": self.user,
                },
                headers=headers,
            )

    def build_connection_url(self) -> Tuple[str, Dict[str, str]]:
        """
        Builds the connection URL and headers for the Snowflake connection.

        Returns:
            The connection URL and headers.

        """
        from komodo._vendored.komodo_connector.setup_driver import get_proxy_host_port

        protocol = self.connection_config.get("query_params", {}).get("protocol", "https")
        host, port = get_proxy_host_port()
        url = f"{protocol}://{host}:{port}/driver/credentials"

        headers = {
            "Authorization": f'Bearer {self.connection_config["komodo_token"]}',
            "Content-Type": "application/json",
            "X-Account-Id": self.connection_config["komodo_account"],
        }
        return url, headers
