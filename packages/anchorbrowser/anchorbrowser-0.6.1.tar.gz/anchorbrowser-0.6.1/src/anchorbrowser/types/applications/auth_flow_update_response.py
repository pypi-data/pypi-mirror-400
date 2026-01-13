# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["AuthFlowUpdateResponse", "CustomField"]


class CustomField(BaseModel):
    name: str
    """Name of the custom field"""


class AuthFlowUpdateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the authentication flow"""

    created_at: Optional[datetime] = None
    """Timestamp when the authentication flow was created"""

    custom_fields: Optional[List[CustomField]] = None
    """Custom fields for this authentication flow"""

    description: Optional[str] = None
    """Description of the authentication flow"""

    is_recommended: Optional[bool] = None
    """Whether this is the recommended authentication flow"""

    methods: Optional[List[str]] = None
    """Authentication methods in this flow"""

    name: Optional[str] = None
    """Name of the authentication flow"""

    updated_at: Optional[datetime] = None
    """Timestamp when the authentication flow was last updated"""
