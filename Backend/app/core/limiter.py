from jose import jwt as _jwt
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def _get_uid(request) -> str:
    """
    Rate-limit key for authenticated endpoints.

    Extracts the Firebase UID from the JWT without re-verifying the signature —
    full verification is already done by get_current_user downstream. Falls back
    to the remote IP when no Bearer token is present.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            claims = _jwt.get_unverified_claims(auth_header[7:])
            uid = claims.get("sub") or claims.get("user_id")
            if uid:
                return uid
        except Exception:
            pass
    return get_remote_address(request)


_storage = settings.REDIS_URL or "memory://"

# Per-user limiter (authenticated endpoints)
limiter = Limiter(key_func=_get_uid, storage_uri=_storage)

# Per-IP limiter (public endpoints and registration)
ip_limiter = Limiter(key_func=get_remote_address, storage_uri=_storage)
