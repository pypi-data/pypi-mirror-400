# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, TypeAlias, TypedDict

__all__ = [
    "IdentityUpdateParams",
    "Credential",
    "CredentialUsernamePasswordCredentialSchema",
    "CredentialAuthenticatorCredentialSchema",
    "CredentialCustomCredentialSchema",
    "CredentialCustomCredentialSchemaField",
]


class IdentityUpdateParams(TypedDict, total=False):
    credentials: Iterable[Credential]
    """Array of credentials for authentication"""

    metadata: Dict[str, object]
    """Metadata for the identity"""

    name: str
    """Name of the identity"""


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
