# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["ApplicationCreateIdentityTokenResponse", "Data"]


class Data(BaseModel):
    token: Optional[str] = None
    """The generated identity token for authentication"""

    expires_at: Optional[datetime] = None
    """The timestamp when the token expires"""

    token_hash: Optional[str] = None
    """A hash of the token for verification purposes"""


class ApplicationCreateIdentityTokenResponse(BaseModel):
    data: Optional[Data] = None
