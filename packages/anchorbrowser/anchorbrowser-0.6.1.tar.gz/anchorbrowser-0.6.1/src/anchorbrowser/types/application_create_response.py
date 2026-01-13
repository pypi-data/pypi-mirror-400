# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["ApplicationCreateResponse"]


class ApplicationCreateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the application"""

    created_at: Optional[datetime] = None
    """Timestamp when the application was created"""

    description: Optional[str] = None
    """Description of the application"""

    name: Optional[str] = None
    """Name of the application"""

    url: Optional[str] = None
    """URL of the application"""
