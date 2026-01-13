# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["AuthFlowCreateParams", "CustomField"]


class AuthFlowCreateParams(TypedDict, total=False):
    methods: Required[List[Literal["username_password", "authenticator", "custom"]]]
    """Authentication methods in this flow"""

    name: Required[str]
    """Name of the authentication flow"""

    custom_fields: Iterable[CustomField]
    """Custom fields for this authentication flow"""

    description: str
    """Description of the authentication flow"""

    is_recommended: bool
    """Whether this is the recommended authentication flow"""


class CustomField(TypedDict, total=False):
    name: Required[str]
    """Name of the custom field"""
