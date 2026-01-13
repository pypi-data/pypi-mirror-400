# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ApplicationListIdentitiesParams"]


class ApplicationListIdentitiesParams(TypedDict, total=False):
    search: str
    """Search query to filter identities by name"""
