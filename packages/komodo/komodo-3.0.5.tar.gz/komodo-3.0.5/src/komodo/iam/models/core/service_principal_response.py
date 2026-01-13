from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, SecretStr, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from komodo.iam.models.core.membership_type import MembershipType
from komodo.iam.models.core.role_response import RoleResponse
from typing import Optional, Set, Union
from typing_extensions import Self


class ServicePrincipalResponse(BaseModel):
    """
    ServicePrincipalResponse
    """  # noqa: E501

    account_id: Optional[StrictStr] = Field(default=None, description="Account ID")
    application_id: Optional[StrictStr] = Field(default=None, description="Application ID")
    client_id: StrictStr = Field(description="Client ID")
    client_secret: Optional[SecretStr] = Field(default=None, description="Client secret")
    created_at: datetime = Field(description="Time of creation")
    created_by: Optional[StrictStr] = Field(default=None, description="Created By")
    description: StrictStr = Field(description="ServicePrincipal description")
    membership_type: Optional[Union[MembershipType, str]] = Field(default=None, description="The service principal's level of access within platform-rbac")
    name: StrictStr = Field(description="ServicePrincipal name")
    roles: Optional[List[RoleResponse]] = None
    service_principal_id: StrictStr = Field(description="Service Principal ID")
    updated_at: datetime = Field(description="Time of last update")
    updated_by: Optional[StrictStr] = Field(default=None, description="Updated By")
    __properties: ClassVar[List[str]] = [
        "account_id",
        "application_id",
        "client_id",
        "client_secret",
        "created_at",
        "created_by",
        "description",
        "membership_type",
        "name",
        "roles",
        "service_principal_id",
        "updated_at",
        "updated_by",
    ]

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
        """Create an instance of ServicePrincipalResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in roles (list)
        _items = []
        if self.roles:
            for _item_roles in self.roles:
                if _item_roles:
                    _items.append(_item_roles.to_dict())
            _dict["roles"] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ServicePrincipalResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "account_id": obj.get("account_id"),
                "application_id": obj.get("application_id"),
                "client_id": obj.get("client_id"),
                "client_secret": obj.get("client_secret"),
                "created_at": obj.get("created_at"),
                "created_by": obj.get("created_by"),
                "description": obj.get("description"),
                "membership_type": obj.get("membership_type"),
                "name": obj.get("name"),
                "roles": [RoleResponse.from_dict(_item) for _item in obj["roles"]] if obj.get("roles") is not None else None,
                "service_principal_id": obj.get("service_principal_id"),
                "updated_at": obj.get("updated_at"),
                "updated_by": obj.get("updated_by"),
            }
        )
        return _obj
