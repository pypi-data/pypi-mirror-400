from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from komodo.iam.models.core.user_lookup_account import UserLookupAccount
from komodo.iam.models.core.user_lookup_group import UserLookupGroup
from typing import Optional, Set, Union
from typing_extensions import Self


class UserLookupOrganization(BaseModel):
    """
    UserLookupOrganization
    """  # noqa: E501

    accounts: Optional[List[UserLookupAccount]] = None
    groups: Optional[List[UserLookupGroup]] = None
    name: StrictStr = Field(description="Organization name")
    organization_id: StrictStr = Field(description="Organization ID")
    slug: StrictStr = Field(description="Organization slug")
    __properties: ClassVar[List[str]] = ["accounts", "groups", "name", "organization_id", "slug"]

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
        """Create an instance of UserLookupOrganization from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of each item in accounts (list)
        _items = []
        if self.accounts:
            for _item_accounts in self.accounts:
                if _item_accounts:
                    _items.append(_item_accounts.to_dict())
            _dict["accounts"] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in groups (list)
        _items = []
        if self.groups:
            for _item_groups in self.groups:
                if _item_groups:
                    _items.append(_item_groups.to_dict())
            _dict["groups"] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of UserLookupOrganization from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "accounts": [UserLookupAccount.from_dict(_item) for _item in obj["accounts"]] if obj.get("accounts") is not None else None,
                "groups": [UserLookupGroup.from_dict(_item) for _item in obj["groups"]] if obj.get("groups") is not None else None,
                "name": obj.get("name"),
                "organization_id": obj.get("organization_id"),
                "slug": obj.get("slug"),
            }
        )
        return _obj
