"""Strict token verification; RBAC comes from local grants, not untrusted headers."""

from pathlib import Path
from uuid import UUID

import jwt
from fastapi import HTTPException
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Device
from app.security.identity import Principal
from app.security.models import DeviceRegistration, Identity
from app.seed import DEMO_USER_ID


def deny(code="UNAUTHENTICATED", status=401):
    raise HTTPException(status, {"code": code, "message": "Authentication or permission required."})


def secret():
    if not settings.auth_key_file:
        raise ValueError("AUTH_KEY_FILE is required for local token mode")
    value = Path(settings.auth_key_file).read_text().strip()
    if len(value) < 64:
        raise ValueError("Local signing key must contain at least 64 characters")
    return value


def authenticate(headers):
    if settings.auth_mode == "demo":
        return Principal(DEMO_USER_ID, frozenset({"owner", "approver", "operator"}))
    token = headers.get("authorization", "")
    if not token.startswith("Bearer ") or len(token) > 12000:
        deny()
    try:
        if settings.auth_mode == "local":
            key, algorithms, issuer = secret(), ["HS256"], "nova-local"
        else:
            # Operator-provided public JWKS snapshot; no token-controlled URL/network discovery.
            keys = oidc_keys()
            kid = jwt.get_unverified_header(token[7:]).get("kid")
            candidates = [k for k in keys.keys if k.key_id == kid and k.algorithm_name == "RS256"]
            if len(candidates) != 1:
                deny()
            key, algorithms, issuer = candidates[0].key, ["RS256"], settings.oidc_issuer
        claims = jwt.decode(
            token[7:],
            key,
            algorithms=algorithms,
            issuer=issuer,
            audience=settings.auth_audience,
            options={
                "require": ["exp", "iat", "iss", "aud", "sub"]
                + (["nbf"] if settings.auth_mode == "local" else [])
            },
        )
        if claims["exp"] - claims["iat"] > 3600:
            deny()
        device_id = UUID(claims["device_id"])
        with SessionLocal() as session:
            identity = session.scalar(
                select(Identity).where(
                    Identity.issuer == issuer, Identity.subject == claims["sub"], Identity.enabled
                )
            )
            if identity is None or (
                settings.auth_mode == "local" and claims.get("version") != identity.version
            ):
                deny()
            if not session.scalar(
                select(Device.id).where(Device.id == device_id, Device.user_id == identity.user_id)
            ):
                deny("DEVICE_IDENTITY_INVALID")
            device = session.get(DeviceRegistration, device_id)
            if device and (
                not device.enabled
                or (
                    settings.auth_mode == "local"
                    and claims.get("device_version", 0) != device.version
                )
                or (
                    settings.auth_mode == "oidc"
                    and int(claims["iat"]) <= int(device.updated_at.timestamp())
                )
            ):
                deny("DEVICE_REVOKED")
            return Principal(
                identity.user_id,
                frozenset(identity.roles),
                device_id,
                settings.auth_mode,
                identity.id,
            )
    except (jwt.PyJWTError, ValueError, KeyError, TypeError, OSError):
        deny()


def authorize(value, method, path):
    needed = "owner"
    if path.startswith(("/api/v1/evaluation", "/api/v1/experiments", "/api/v1/operations")):
        needed = "operator"
    elif method != "GET" and (path.endswith("/approve") or path.endswith("/execute")):
        needed = "approver"
    if needed not in value.roles and not (
        needed == "owner" and "viewer" in value.roles and method == "GET"
    ):
        deny("FORBIDDEN", 403)


_jwks_cache = {}


def oidc_keys():
    if settings.oidc_jwks_file:
        return jwt.PyJWKSet.from_json(Path(settings.oidc_jwks_file).read_text())
    import time
    from urllib.parse import urlsplit

    import httpx

    url = settings.oidc_jwks_url
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"keycloak", "localhost", "127.0.0.1"}
        or parsed.username
        or parsed.query
        or parsed.fragment
    ):
        deny()
    cached = _jwks_cache.get(url)
    if cached and time.monotonic() < cached[0]:
        return cached[1]
    try:
        with httpx.Client(timeout=3, trust_env=False, follow_redirects=False) as client:
            with client.stream("GET", url) as response:
                response.raise_for_status()
                body = b""
                for chunk in response.iter_bytes():
                    body += chunk
                    if len(body) > 64000:
                        deny()
        keys = jwt.PyJWKSet.from_json(body)
        if len(keys.keys) > 20:
            deny()
        _jwks_cache.clear()
        _jwks_cache[url] = (time.monotonic() + 60, keys)
        return keys
    except (httpx.HTTPError, ValueError):
        deny()
