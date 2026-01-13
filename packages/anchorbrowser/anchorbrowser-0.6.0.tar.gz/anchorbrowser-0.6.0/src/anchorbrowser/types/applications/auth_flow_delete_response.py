# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["AuthFlowDeleteResponse"]


class AuthFlowDeleteResponse(BaseModel):
    success: Optional[bool] = None
    """Whether the deletion was successful"""
