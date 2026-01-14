"""Type definitions for OIDC authentication in Reflex Enterprise."""

from typing import TypedDict


class OIDCUserInfo(TypedDict, total=False):
    """Type describing user info obtained from an OIDC provider.

    Attributes:
        sub: The unique identifier for the user.
    """

    sub: str
