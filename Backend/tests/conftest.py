import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _set_default_env(name: str, value: str) -> None:
    os.environ.setdefault(name, value)


_set_default_env("SECRET_KEY", "test-secret")
_set_default_env("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
_set_default_env("FIREBASE_API_KEY", "test")
_set_default_env("FIREBASE_PROJECT_ID", "test")
_set_default_env("FIREBASE_PRIVATE_KEY_ID", "test")
_set_default_env("FIREBASE_PRIVATE_KEY", "test")
_set_default_env("FIREBASE_CLIENT_EMAIL", "test@example.com")
_set_default_env("FIREBASE_CLIENT_ID", "test")
_set_default_env("FIREBASE_AUTH_URI", "https://example.com/auth")
_set_default_env("FIREBASE_TOKEN_URI", "https://example.com/token")
_set_default_env("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://example.com/cert")
_set_default_env("FIREBASE_CLIENT_X509_CERT_URL", "https://example.com/client-cert")
_set_default_env("FIREBASE_UNIVERSE_DOMAIN", "example.com")
_set_default_env("R2_ACCOUNT_ID", "test")
_set_default_env("R2_ACCESS_KEY_ID", "test")
_set_default_env("R2_SECRET_ACCESS_KEY", "test")
_set_default_env("R2_BUCKET_NAME", "test")
_set_default_env("R2_PUBLIC_URL", "https://example.com")
_set_default_env("GOOGLE_APPLICATION_CREDENTIALS", "test.json")
_set_default_env("PHONEME_ASSESSMENT_PROVIDER", "reference_aligned_phoneme_dtw")
