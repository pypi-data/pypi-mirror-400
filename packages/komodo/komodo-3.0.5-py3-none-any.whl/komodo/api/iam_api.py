import os
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from komodo.iam.models.identity.identity_response import IdentityResponse
from komodo.api_client import ApiClient, RequestSerialized


class IamApi:
    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client
        self.api_version = "2024-10-01"

    @validate_call
    def get_current_identity(
        self,
        expand: Annotated[
            Optional[List[StrictStr]],
            Field(
                description='Include expanded resources related to the user in the response:                - `organizations`: include a list of all organizations to which the user belongs                - `organizations.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user belongs within each organization_                - `organizations.groups`: a list of all organizations to which the user belongs _with a nested                     list of the groups to which the user belongs within each organization_                - `organizations.groups.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user has direct membership                     within each organization, and a nested list of the groups to which the                     user belongs within the organization. Each group contains a nested list of accounts to which                    the group (and therefore the user) has membership in the organization_               Note:                - If multiple elements with the same prefix but _different levels of nesting_ are specified                     only the longest element will be used. For example,                     if `"expand" = ["organizations", "organizations.accounts"]` the result                     will be the same as if `"expand" = ["organizations.accounts"]`.                - If both `organizations.accounts` and `organizations.groups.accounts` is                     specified, the behavior will match `organizations.groups.accounts`                - Elements must be unique             '
            ),
        ] = None,
        _request_timeout: Union[None, Annotated[StrictFloat, Field(gt=0)], Tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]]] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=2)] = 0,
    ) -> IdentityResponse:
        """Look up details on the User or Service Principal making the request.

        Look up details on the User or Service Principal making the request.  Look up details on the User or Service Principal making the request. The 'expand' parameter allows additional information to be returned for Users.  **Returns:** - IdentityResponse: Details of the User or Service Principal making the request.

        :param expand: Include expanded resources related to the user in the response:                - `organizations`: include a list of all organizations to which the user belongs                - `organizations.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user belongs within each organization_                - `organizations.groups`: a list of all organizations to which the user belongs _with a nested                     list of the groups to which the user belongs within each organization_                - `organizations.groups.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user has direct membership                     within each organization, and a nested list of the groups to which the                     user belongs within the organization. Each group contains a nested list of accounts to which                    the group (and therefore the user) has membership in the organization_               Note:                - If multiple elements with the same prefix but _different levels of nesting_ are specified                     only the longest element will be used. For example,                     if `\"expand\" = [\"organizations\", \"organizations.accounts\"]` the result                     will be the same as if `\"expand\" = [\"organizations.accounts\"]`.                - If both `organizations.accounts` and `organizations.groups.accounts` is                     specified, the behavior will match `organizations.groups.accounts`                - Elements must be unique
        :type expand: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """  # noqa: E501

        _param = self._get_current_identity_serialize(expand=expand, _request_auth=_request_auth, _content_type=_content_type, _headers=_headers, _host_index=_host_index)

        _response_types_map: Dict[str, Optional[str]] = {
            "200": "IdentityResponse",
            "404": "ErrorResponse",
            "422": "HTTPValidationError",
        }

        response_data = self.api_client.call_api(*_param, _request_timeout=_request_timeout)
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            subpackage="komodo.iam.models",
            response_types_map=_response_types_map,
        ).data

    @validate_call
    async def get_current_identity_async(
        self,
        expand: Annotated[
            Optional[List[StrictStr]],
            Field(
                description='Include expanded resources related to the user in the response:                - `organizations`: include a list of all organizations to which the user belongs                - `organizations.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user belongs within each organization_                - `organizations.groups`: a list of all organizations to which the user belongs _with a nested                     list of the groups to which the user belongs within each organization_                - `organizations.groups.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user has direct membership                     within each organization, and a nested list of the groups to which the                     user belongs within the organization. Each group contains a nested list of accounts to which                    the group (and therefore the user) has membership in the organization_               Note:                - If multiple elements with the same prefix but _different levels of nesting_ are specified                     only the longest element will be used. For example,                     if `"expand" = ["organizations", "organizations.accounts"]` the result                     will be the same as if `"expand" = ["organizations.accounts"]`.                - If both `organizations.accounts` and `organizations.groups.accounts` is                     specified, the behavior will match `organizations.groups.accounts`                - Elements must be unique             '
            ),
        ] = None,
        _request_timeout: Union[None, Annotated[StrictFloat, Field(gt=0)], Tuple[Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]]] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=2)] = 0,
    ) -> IdentityResponse:
        """Look up details on the User or Service Principal making the request.

        Look up details on the User or Service Principal making the request.  Look up details on the User or Service Principal making the request. The 'expand' parameter allows additional information to be returned for Users.  **Returns:** - IdentityResponse: Details of the User or Service Principal making the request.

        :param expand: Include expanded resources related to the user in the response:                - `organizations`: include a list of all organizations to which the user belongs                - `organizations.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user belongs within each organization_                - `organizations.groups`: a list of all organizations to which the user belongs _with a nested                     list of the groups to which the user belongs within each organization_                - `organizations.groups.accounts`: a list of all organizations to which the user belongs _with                     a nested list of the accounts to which the user has direct membership                     within each organization, and a nested list of the groups to which the                     user belongs within the organization. Each group contains a nested list of accounts to which                    the group (and therefore the user) has membership in the organization_               Note:                - If multiple elements with the same prefix but _different levels of nesting_ are specified                     only the longest element will be used. For example,                     if `\"expand\" = [\"organizations\", \"organizations.accounts\"]` the result                     will be the same as if `\"expand\" = [\"organizations.accounts\"]`.                - If both `organizations.accounts` and `organizations.groups.accounts` is                     specified, the behavior will match `organizations.groups.accounts`                - Elements must be unique
        :type expand: List[str]
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """  # noqa: E501

        _param = self._get_current_identity_serialize(expand=expand, _request_auth=_request_auth, _content_type=_content_type, _headers=_headers, _host_index=_host_index)

        _response_types_map: Dict[str, Optional[str]] = {
            "200": "IdentityResponse",
            "404": "ErrorResponse",
            "422": "HTTPValidationError",
        }
        response_data = await self.api_client.call_api_async(*_param, _request_timeout=_request_timeout)
        await response_data.read_async()
        return self.api_client.response_deserialize(
            response_data=response_data,
            subpackage="komodo.iam.models",
            response_types_map=_response_types_map,
        ).data

    def _get_current_identity_serialize(
        self,
        expand,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:
        _hosts = ["https://dev-api.khinternal.net", "https://api.komodohealth.com"]
        _host = _hosts[_host_index]

        environment = os.getenv("KOMODO_ENVIRONMENT", "production")
        if environment == "integration":
            _host = _hosts[0]
        else:
            _host = _hosts[1]

        _collection_formats: Dict[str, str] = {
            "expand": "multi",
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if expand is not None:
            _query_params.append(("expand", expand))

        # process the header parameters
        # process the form parameters
        # process the body parameter

        # set the HTTP header `Accept`
        if "Accept" not in _header_params:
            _header_params["Accept"] = self.api_client.select_header_accept(["application/json"])

        _header_params["X-API-Version"] = self.api_version
        # authentication setting
        _auth_settings: List[str] = ["HTTPBearer"]

        return self.api_client.param_serialize(
            method="GET",
            resource_path="/v1/iam/identity",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth,
        )
