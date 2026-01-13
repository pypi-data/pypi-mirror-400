from __future__ import annotations
import json
from enum import Enum
from typing_extensions import Self


class UserStatus(str, Enum):
    """
    UserStatus
    """

    """
    allowed enum values
    """
    INACTIVE = "inactive"
    ACTIVE = "active"

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of UserStatus from a JSON string"""
        return cls(json.loads(json_str))
