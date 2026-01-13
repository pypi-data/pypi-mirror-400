# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["ApplicationListResponse", "Application"]


class Application(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the application"""

    allowed_domains: Optional[List[str]] = None
    """List of allowed domains for this application"""

    auth_methods: Optional[List[str]] = None
    """Authentication methods available for this application"""

    created_at: Optional[datetime] = None
    """Timestamp when the application was created"""

    description: Optional[str] = None
    """Description of the application"""

    identity_count: Optional[int] = None
    """Number of identities associated with this application"""

    name: Optional[str] = None
    """Name of the application"""

    updated_at: Optional[datetime] = None
    """Timestamp when the application was last updated"""

    url: Optional[str] = None
    """URL of the application"""


class ApplicationListResponse(BaseModel):
    applications: Optional[List[Application]] = None
