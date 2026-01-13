# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["IdentityCreateResponse"]


class IdentityCreateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the identity"""

    created_at: Optional[datetime] = None
    """Timestamp when the identity was created"""

    metadata: Optional[Dict[str, object]] = None
    """Metadata associated with the identity"""

    name: Optional[str] = None
    """Name of the identity"""

    status: Optional[Literal["pending", "validated", "failed"]] = None
    """Status of the identity"""
