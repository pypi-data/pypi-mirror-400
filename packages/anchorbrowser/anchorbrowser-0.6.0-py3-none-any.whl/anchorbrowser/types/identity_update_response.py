# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["IdentityUpdateResponse"]


class IdentityUpdateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the identity"""

    metadata: Optional[Dict[str, object]] = None
    """Metadata associated with the identity"""

    name: Optional[str] = None
    """Name of the identity"""

    updated_at: Optional[datetime] = None
    """Timestamp when the identity was last updated"""
