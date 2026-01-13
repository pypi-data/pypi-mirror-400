import io
import re

import httpx
from httpx_retries import RetryTransport, Retry
from komodo.exceptions import ApiException, ApiValueError

SUPPORTED_SOCKS_PROXIES = {"socks5", "socks5h", "socks4", "socks4a"}
RESTResponseType = httpx.Response

ALLOW_RETRY_METHODS = frozenset({"DELETE", "GET", "HEAD", "OPTIONS", "PUT", "TRACE"})


def is_socks_proxy_url(url):
    if url is None:
        return False
    split_section = url.split("://")
    if len(split_section) < 2:
        return False
    else:
        return split_section[0].lower() in SUPPORTED_SOCKS_PROXIES


class RESTResponse(io.IOBase):
    def __init__(self, resp) -> None:
        self.response = resp
        self.status = resp.status_code
        self.reason = resp.reason_phrase
        self.data = None

    def read(self):
        if self.data is None:
            self.data = self.response.content
        return self.data

    async def read_async(self):
        if self.data is None:
            self.data = await self.response.aread()
        return self.data

    def getheaders(self):
        """Returns a dictionary of the response headers."""
        return self.response.headers

    def getheader(self, name, default=None):
        """Returns a given response header."""
        return self.response.headers.get(name, default)


class RESTClientObject:
    def __init__(self, configuration) -> None:
        retry = Retry(total=configuration.retries)
        transport = RetryTransport(retry=retry)
        self.client = httpx.Client(
            transport=transport,
            verify=configuration.verify_ssl,
            timeout=None,
        )

    def request(self, method, url, headers=None, body=None, post_params=None, _request_timeout=None):
        """Perform requests.

        :param method: http request method
        :param url: http request url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencoded`
                            and `multipart/form-data`
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        """
        method = method.upper()
        assert method in ["GET", "HEAD", "DELETE", "POST", "PUT", "PATCH", "OPTIONS"]

        if post_params and body:
            raise ApiValueError("body parameter cannot be used with post_params parameter.")

        post_params = post_params or {}
        headers = headers or {}

        timeout = _request_timeout or 5 * 60

        try:
            # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`
            if method in ["POST", "PUT", "PATCH", "OPTIONS", "DELETE"]:
                # no content type provided or payload is json
                content_type = headers.get("Content-Type", "application/json")
                if re.search("json", content_type, re.IGNORECASE):
                    response = self.client.request(method, url, json=body, headers=headers, timeout=timeout)
                elif content_type == "application/x-www-form-urlencoded":
                    response = self.client.request(method, url, data=post_params, headers=headers, timeout=timeout)
                elif content_type == "multipart/form-data":
                    headers.pop("Content-Type", None)
                    response = self.client.request(method, url, files=post_params, headers=headers, timeout=timeout)
                else:
                    response = self.client.request(method, url, content=body, headers=headers, timeout=timeout)
            else:
                response = self.client.request(method, url, headers=headers, timeout=timeout)
        except httpx.RequestError as e:
            raise ApiException(status=0, reason=str(e))

        return RESTResponse(response)


class RESTClientObjectAsync:
    def __init__(self, configuration) -> None:
        retry = Retry(total=configuration.retries)
        transport = RetryTransport(retry=retry)

        self.client = httpx.AsyncClient(
            transport=transport,
            verify=configuration.verify_ssl,
            timeout=None,
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def request(self, method, url, headers=None, body=None, post_params=None, _request_timeout=None):
        """Execute request

        :param method: http request method
        :param url: http request url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencoded`
                            and `multipart/form-data`
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        """
        method = method.upper()
        assert method in ["GET", "HEAD", "DELETE", "POST", "PUT", "PATCH", "OPTIONS"]

        if post_params and body:
            raise ApiValueError("body parameter cannot be used with post_params parameter.")

        post_params = post_params or {}
        headers = headers or {}
        # url already contains the URL query string
        timeout = _request_timeout or 5 * 60

        # Set default Content-Type if not provided
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        try:
            # Handle different content types for request body
            if method in ["POST", "PUT", "PATCH", "OPTIONS", "DELETE"]:
                content_type = headers.get("Content-Type", "application/json")
                if re.search("json", content_type, re.IGNORECASE):
                    response = await self.client.request(method, url, json=body, headers=headers, timeout=timeout)
                elif content_type == "application/x-www-form-urlencoded":
                    response = await self.client.request(method, url, data=post_params, headers=headers, timeout=timeout)
                elif content_type == "multipart/form-data":
                    headers.pop("Content-Type", None)
                    response = await self.client.request(method, url, files=post_params, headers=headers, timeout=timeout)
                else:
                    response = await self.client.request(method, url, content=body, headers=headers, timeout=timeout)
            else:
                # Handle GET-like methods with query parameters
                response = await self.client.request(method, url, headers=headers, timeout=timeout)
        except httpx.RequestError as e:
            raise ApiException(status=0, reason=str(e))

        return RESTResponse(response)
