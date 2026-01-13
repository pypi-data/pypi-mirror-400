import logging
import time
import webbrowser

from contextlib import nullcontext
from http import HTTPStatus
from typing import Any

import httpx
from auth0.authentication.token_verifier import AsymmetricSignatureVerifier, TokenVerifier
from komodo.APIResponseError import APIResponseError

from rich.console import Console
from rich.text import Text


class OAuthFlows:
    def __init__(self, *, domain, rbac_url, logger=None):
        """

        :param domain:
        :param rbac_url:
        :param logger:
        """
        self._idp_domain = domain
        self._rbac_url = rbac_url
        self._logger = logger if logger is not None else logging.getLogger(__name__)

    def client_credentials(self, client_id, client_secret) -> dict[str, Any]:
        """
        Get a service principal JWT using the client credentials flow.

        :param client_id: the service principal's client ID
        :param client_secret: the service principal's client secret
        :return: a dict containing the access token and its expiration time
        """

        payload = dict(client_id=client_id, client_secret=client_secret)
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        token_response = httpx.post(
            f"{self._rbac_url}/v1/iam/service-principals/token",
            headers=headers,
            json=payload,
            timeout=(10.0, 30.0),
        )
        if token_response.status_code == HTTPStatus.CREATED:
            token_data = token_response.json()

            self._logger.debug(f"access_token: {token_data['access_token'][:20]}...")
            self._logger.debug(f"access_token expires in: {token_data['expires_in']}s")

            expires_at = int(time.time()) + token_data["expires_in"]
            token_data["expires_at"] = expires_at
            del token_data["expires_in"]
            token_data["client_id"] = client_id
            token_data["client_secret"] = client_secret
            return token_data
        else:
            raise APIResponseError(
                message="Fail to get token",
                status_code=token_response.status_code,
                payload=token_response.text,
            )

    def device_authorization(self, client_id, audience, scope, timeout: int | None = None, **kwargs) -> dict[str, Any]:
        """
        Runs the OAuth 2 Device Authorization Grant flow
        (see https://www.rfc-editor.org/rfc/rfc8628)

        - Note: this flow is tailored for terminal/CLI and displays instructions on
          standard output.

        :param client_id:
        :param audience:
        :param scope:
        :param timeout: optional timeout for the user to complete the flow (in seconds).
        :param kwargs:
        :return: dictionary of tokens
        """
        console = kwargs.get("rich_console")
        if console is None:
            console = Console()

        device_code_payload = {
            "client_id": client_id,
            "audience": audience,
            "scope": scope,
        }

        device_code_response = httpx.post(
            f"https://{self._idp_domain}/oauth/device/code",
            data=device_code_payload,
            timeout=(10.0, 30.0),
        )

        if device_code_response.status_code != HTTPStatus.OK:
            term_display = "Error generating the device code"
            console.print(f"[bold red]{term_display}")
            self._logger.error(f"Fail to get device code [HTTP status code: {device_code_response.status_code}]")
            raise APIResponseError(
                message=term_display,
                status_code=device_code_response.status_code,
                payload=device_code_response.text,
            )

        self._logger.info("Device code successful")
        device_code_data = device_code_response.json()

        # Change to 'verification_uri' to not have user_code already part of the URL
        # and force user to enter it in UI
        link_text = Text(device_code_data["verification_uri_complete"], style="bold underline blue")
        term_display = Text("Authorize at ", style="bold")
        console.print(term_display.append(link_text))
        self._logger.info(f"Device code is: {device_code_data['user_code']}")

        try:
            webbrowser.open(device_code_data["verification_uri_complete"], new=2)
        except Exception as e:
            console.print(Text(f"Could not open the browser automatically: {e}", style="bold yellow"))

        token_payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code_data["device_code"],
            "client_id": client_id,
        }

        start_time = time.time()
        with console.status("Waiting for the user to complete the flow...", spinner="dots"):
            while True:
                if timeout is not None and (time.time() - start_time) > timeout:
                    term_display = "Timeout reached while waiting for user authorization."
                    console.print(f"[bold red]{term_display}")
                    raise TimeoutError(term_display)

                token_response = httpx.post(
                    f"https://{self._idp_domain}/oauth/token",
                    data=token_payload,
                    timeout=(10.0, 30),
                )
                token_data = token_response.json()

                if token_response.status_code == HTTPStatus.OK:
                    user_tokens = dict()
                    user_token_types = ["id_token", "access_token", "expires_in"]

                    # Validate (ID Token if found else Access Token)
                    if "id_token" in token_data:
                        self.validate_token(token_data["id_token"], client_id)
                    else:
                        self.validate_token(token_data["access_token"], audience)

                    for token_type in user_token_types:
                        if token_type in token_data:
                            if token_type == "expires_in":
                                expires_at = int(time.time()) + token_data["expires_in"]
                                user_tokens["expires_at"] = expires_at
                            else:
                                user_tokens[token_type] = token_data[token_type]

                    return user_tokens
                elif token_data["error"] not in ("authorization_pending", "slow_down"):
                    term_display = Text(token_data["error_description"], style="bold red")
                    console.print(term_display)
                    raise APIResponseError(
                        message=token_data["error_description"],
                        status_code=token_response.status_code,
                        payload=token_response.text,
                    )
                else:
                    time.sleep(device_code_data["interval"])

    def validate_token(self, token, audience):
        jwks_url = f"https://{self._idp_domain}/.well-known/jwks.json"
        issuer = f"https://{self._idp_domain}/"
        sv = AsymmetricSignatureVerifier(jwks_url)
        tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=audience)
        tv.verify(token)
