from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from komodo.iam.models.core.membership_type import MembershipType
from komodo.iam.models.core.user_lookup_organization import UserLookupOrganization
from komodo.iam.models.core.user_status import UserStatus
from komodo.iam.models.core.user_type import UserType
from typing import Optional, Set, Union
from typing_extensions import Self


class UserLookupResponse(BaseModel):
    """
    Details of User that may contain expanded information about Organizations, Groups, and Accounts the User is a member of.
    """  # noqa: E501

    auth_tenant_id: Optional[StrictStr] = Field(default=None, description="the id of the user that is issued by the auth tenant")
    created_at: datetime = Field(description="Time of creation")
    created_by: Optional[StrictStr] = Field(default=None, description="Created By")
    display_name: Optional[StrictStr] = Field(default=None, description="Display name (SCIM)")
    email: StrictStr = Field(description="User email")
    family_name: Optional[StrictStr] = Field(default=None, description="Family name (SCIM)")
    formatted: Optional[StrictStr] = Field(default=None, description="Formatted name (SCIM)")
    given_name: Optional[StrictStr] = Field(default=None, description="Given name (SCIM)")
    honorific_prefix: Optional[StrictStr] = Field(default=None, description="Honorific prefix (SCIM)")
    honorific_suffix: Optional[StrictStr] = Field(default=None, description="Honorific suffix (SCIM)")
    last_account_used: Optional[StrictStr] = Field(default=None, description="Account id")
    locale: Optional[StrictStr] = Field(default=None, description="Locale (SCIM)")
    membership_type: Optional[Union[MembershipType, str]] = Field(default=None, description="The user's level of access across the entire platform-rbac system")
    middle_name: Optional[StrictStr] = Field(default=None, description="Middle name (SCIM)")
    nick_name: Optional[StrictStr] = Field(default=None, description="Nick name (SCIM)")
    organizations: Optional[List[UserLookupOrganization]] = None
    preferred_language: Optional[StrictStr] = Field(default=None, description="Preferred language (SCIM)")
    profile_url: Optional[StrictStr] = Field(default=None, description="Profile URL (SCIM)")
    status: Union[UserStatus, str] = Field(description="Status (active or inactive)")
    timezone: Optional[StrictStr] = Field(default=None, description="Timezone (SCIM)")
    title: Optional[StrictStr] = Field(default=None, description="Title (SCIM)")
    updated_at: datetime = Field(description="Time of last update")
    updated_by: Optional[StrictStr] = Field(default=None, description="Updated By")
    user_id: StrictStr = Field(description="User ID")
    user_type: Union[UserType, str] = Field(description="User type")
    __properties: ClassVar[List[str]] = [
        "auth_tenant_id",
        "created_at",
        "created_by",
        "display_name",
        "email",
        "family_name",
        "formatted",
        "given_name",
        "honorific_prefix",
        "honorific_suffix",
        "last_account_used",
        "locale",
        "membership_type",
        "middle_name",
        "nick_name",
        "organizations",
        "preferred_language",
        "profile_url",
        "status",
        "timezone",
        "title",
        "updated_at",
        "updated_by",
        "user_id",
        "user_type",
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
        """Create an instance of UserLookupResponse from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in organizations (list)
        _items = []
        if self.organizations:
            for _item_organizations in self.organizations:
                if _item_organizations:
                    _items.append(_item_organizations.to_dict())
            _dict["organizations"] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of UserLookupResponse from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "auth_tenant_id": obj.get("auth_tenant_id"),
                "created_at": obj.get("created_at"),
                "created_by": obj.get("created_by"),
                "display_name": obj.get("display_name"),
                "email": obj.get("email"),
                "family_name": obj.get("family_name"),
                "formatted": obj.get("formatted"),
                "given_name": obj.get("given_name"),
                "honorific_prefix": obj.get("honorific_prefix"),
                "honorific_suffix": obj.get("honorific_suffix"),
                "last_account_used": obj.get("last_account_used"),
                "locale": obj.get("locale"),
                "membership_type": obj.get("membership_type"),
                "middle_name": obj.get("middle_name"),
                "nick_name": obj.get("nick_name"),
                "organizations": [UserLookupOrganization.from_dict(_item) for _item in obj["organizations"]] if obj.get("organizations") is not None else None,
                "preferred_language": obj.get("preferred_language"),
                "profile_url": obj.get("profile_url"),
                "status": obj.get("status"),
                "timezone": obj.get("timezone"),
                "title": obj.get("title"),
                "updated_at": obj.get("updated_at"),
                "updated_by": obj.get("updated_by"),
                "user_id": obj.get("user_id"),
                "user_type": obj.get("user_type"),
            }
        )
        return _obj
