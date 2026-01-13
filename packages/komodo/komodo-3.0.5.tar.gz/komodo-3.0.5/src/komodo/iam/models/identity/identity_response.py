from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict
from typing import Any, ClassVar, Dict, List, Optional
from komodo.iam.models.core.service_principal_response import ServicePrincipalResponse
from komodo.iam.models.core.user_lookup_response import UserLookupResponse
from komodo.iam.models.identity.jwt_type import JWTType
from typing import Optional, Set, Union
from typing_extensions import Self


class IdentityResponse(BaseModel):
    """
    Details of the User or Service Principal making the request.
    """  # noqa: E501

    jwt_type: JWTType
    service_principal: Optional[ServicePrincipalResponse] = None
    user: Optional[UserLookupResponse] = None
    __properties: ClassVar[List[str]] = ["jwt_type", "service_principal", "user"]

    model_config = ConfigDict(populate_by_name=True, validate_assignment=True, protected_namespaces=(), extra="allow")

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of IdentityResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of service_principal
        if self.service_principal:
            _dict["service_principal"] = self.service_principal.to_dict()
        # override the default output from pydantic by calling `to_dict()` of user
        if self.user:
            _dict["user"] = self.user.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of IdentityResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "jwt_type": obj.get("jwt_type"),
                "service_principal": ServicePrincipalResponse.from_dict(obj["service_principal"]) if obj.get("service_principal") is not None else None,
                "user": UserLookupResponse.from_dict(obj["user"]) if obj.get("user") is not None else None,
            }
        )
        return _obj
