# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ApplicationCreateIdentityTokenParams"]


class ApplicationCreateIdentityTokenParams(TypedDict, total=False):
    callback_url: Required[Annotated[str, PropertyInfo(alias="callbackUrl")]]
    """The HTTPS URL where the user will be redirected after authentication.

    Must use HTTPS protocol.
    """
