"""OIDC helpers: metadata, JWKS, and JWT verification."""

import base64
import hashlib
import logging

import httpx
from joserfc import jwk, jwt

# Simple cached OIDC metadata + JWKS loader
_OIDC_CACHE: dict[str, dict] = {}


logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Raised when token validation fails."""


async def _fetch_oidc_metadata(issuer: str) -> dict:
    key = f"metadata:{issuer}"
    if key in _OIDC_CACHE:
        return _OIDC_CACHE[key]
    url = issuer.rstrip("/") + "/.well-known/openid-configuration"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10)
        resp.raise_for_status()
        md = resp.json()
        _OIDC_CACHE[key] = md
        return md


async def _fetch_jwks(jwks_uri: str) -> dict:
    key = f"jwks:{jwks_uri}"
    if key in _OIDC_CACHE:
        return _OIDC_CACHE[key]
    async with httpx.AsyncClient() as client:
        resp = await client.get(jwks_uri, timeout=10)
        resp.raise_for_status()
        jwks = resp.json()
        _OIDC_CACHE[key] = jwks
        return jwks


async def issuer_endpoint(issuer_uri: str, service: str) -> str:
    """Fetch an endpoint URL (authorization/token/userinfo/etc) from OIDC metadata."""
    try:
        return (await _fetch_oidc_metadata(issuer_uri))[service]
    except KeyError:
        return ""


async def verify_jwt(
    token_json: str,
    issuer: str,
    audience: str | list[str] | None = None,
    nonce: str | None = None,
    at_hash: str | None = None,
) -> jwt.Token:
    """Verify a JWT using OIDC discovery and JWKS per Microsoft docs.

    Returns:
        The verified JWT token.
    """
    # Fetch metadata and keys from well-known endpoint.
    md = await _fetch_oidc_metadata(issuer)
    jwks_uri = md.get("jwks_uri")
    if not jwks_uri:
        raise RuntimeError("jwks_uri not found in oidc metadata")
    jwks = await _fetch_jwks(jwks_uri)

    # Build JsonWebKey set from HTTP response/cache.
    key_set = jwk.KeySet.import_key_set(jwks)  # pyright: ignore[reportArgumentType]

    # Decode and validate the JWT signature.
    token = jwt.decode(token_json, key_set)

    # Validate specific claims, if provided.
    iss_claim_request: jwt.ClaimsOption = {"essential": True, "value": issuer}
    aud_claim_request: jwt.ClaimsOption = {"essential": False}
    if audience is not None:
        aud_claim_request["essential"] = True
        if isinstance(audience, str):
            aud_claim_request["value"] = audience
        else:
            aud_claim_request["values"] = audience

    nonce_claim_request: jwt.ClaimsOption = {"essential": False}
    if nonce is not None:
        nonce_claim_request["essential"] = True
        nonce_claim_request["value"] = nonce

    at_hash_claim_request: jwt.ClaimsOption = {"essential": False}
    if at_hash:
        at_hash_claim_request["value"] = at_hash

    logger.debug(
        f"Verifying JWT claims: iss={iss_claim_request}, aud={aud_claim_request}, nonce={nonce_claim_request}, at_hash={at_hash_claim_request}"
    )

    claims_requests = jwt.JWTClaimsRegistry(
        iss=iss_claim_request,
        aud=aud_claim_request,
        nonce=nonce_claim_request,
        at_hash=at_hash_claim_request,
    )
    claims_requests.validate(token.claims)
    return token


def compute_at_hash(access_token: str, alg: str | None) -> str:
    """Compute at_hash value per OIDC spec for a given access token and alg."""
    if not alg:
        alg = "RS256"
    # map alg to hash
    if alg.endswith("256"):
        h = hashlib.sha256(access_token.encode("utf-8")).digest()
    elif alg.endswith("384"):
        h = hashlib.sha384(access_token.encode("utf-8")).digest()
    elif alg.endswith("512"):
        h = hashlib.sha512(access_token.encode("utf-8")).digest()
    else:
        h = hashlib.sha256(access_token.encode("utf-8")).digest()
    # left-most half
    half = h[: len(h) // 2]
    at_hash = base64.urlsafe_b64encode(half).decode("ascii").rstrip("=")
    return at_hash
