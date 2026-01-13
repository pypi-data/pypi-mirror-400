from __future__ import annotations
import json
from enum import Enum
from typing_extensions import Self


class PrivateRole(str, Enum):
    """
    PrivateRole
    """

    """
    allowed enum values
    """
    OWNER = "owner"

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of PrivateRole from a JSON string"""
        return cls(json.loads(json_str))
