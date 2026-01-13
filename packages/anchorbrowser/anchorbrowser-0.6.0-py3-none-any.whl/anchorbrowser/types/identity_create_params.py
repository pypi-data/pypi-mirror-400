# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "IdentityCreateParams",
    "Credential",
    "CredentialUsernamePasswordCredentialSchema",
    "CredentialAuthenticatorCredentialSchema",
    "CredentialCustomCredentialSchema",
    "CredentialCustomCredentialSchemaField",
]


class IdentityCreateParams(TypedDict, total=False):
    credentials: Required[Iterable[Credential]]
    """Array of credentials for authentication"""

    source: Required[str]
    """The source URL for the identity (e.g., login page URL)"""

    validate_async: Annotated[bool, PropertyInfo(alias="validateAsync")]
    """Whether to validate the identity asynchronously. Defaults to true."""

    application_description: Annotated[str, PropertyInfo(alias="applicationDescription")]
    """Optional application description"""

    application_name: Annotated[str, PropertyInfo(alias="applicationName")]
    """Optional application name to associate with the identity"""

    metadata: Dict[str, object]
    """Optional metadata for the identity"""

    name: str
    """Name of the identity. Defaults to "Unnamed Identity" if not provided."""


class CredentialUsernamePasswordCredentialSchema(TypedDict, total=False):
    password: str
    """The password of the credential"""

    type: Literal["username_password"]
    """The type of credential"""

    username: str
    """The username of the credential"""


class CredentialAuthenticatorCredentialSchema(TypedDict, total=False):
    otp: str
    """The OTP of the credential"""

    secret: str
    """The secret of the credential"""

    type: Literal["authenticator"]
    """The type of credential"""


class CredentialCustomCredentialSchemaField(TypedDict, total=False):
    name: str
    """The name of the field"""

    value: str
    """The value of the field"""


class CredentialCustomCredentialSchema(TypedDict, total=False):
    fields: Iterable[CredentialCustomCredentialSchemaField]

    type: Literal["custom"]
    """The type of credential"""


Credential: TypeAlias = Union[
    CredentialUsernamePasswordCredentialSchema,
    CredentialAuthenticatorCredentialSchema,
    CredentialCustomCredentialSchema,
]
