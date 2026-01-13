# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ApplicationCreateParams"]


class ApplicationCreateParams(TypedDict, total=False):
    source: Required[str]
    """The source URL of the application"""

    description: str
    """Description of the application"""

    name: str
    """Name of the application"""
