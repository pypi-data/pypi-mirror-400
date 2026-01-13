# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ApplicationListIdentitiesResponse", "Identity"]


class Identity(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the identity"""

    auth_flow: Optional[str] = None
    """Authentication flow associated with this identity"""

    created_at: Optional[datetime] = None
    """Timestamp when the identity was created"""

    name: Optional[str] = None
    """Name of the identity"""

    status: Optional[Literal["pending", "validated", "failed"]] = None
    """Status of the identity"""

    updated_at: Optional[datetime] = None
    """Timestamp when the identity was last updated"""


class ApplicationListIdentitiesResponse(BaseModel):
    identities: Optional[List[Identity]] = None
