import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

from app.config import settings

TOKEN_CLOCK_SKEW_SECONDS = 5

_credential_dict = {
    "type": "service_account",
    "project_id": settings.FIREBASE_PROJECT_ID,
    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
    "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
    "client_email": settings.FIREBASE_CLIENT_EMAIL,
    "client_id": settings.FIREBASE_CLIENT_ID,
    "auth_uri": settings.FIREBASE_AUTH_URI,
    "token_uri": settings.FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
    "universe_domain": settings.FIREBASE_UNIVERSE_DOMAIN,
}

_cred = credentials.Certificate(_credential_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(_cred, {"projectId": settings.FIREBASE_PROJECT_ID})


def verify_firebase_token(id_token: str) -> dict:
    try:
        decoded = firebase_auth.verify_id_token(
            id_token,
            clock_skew_seconds=TOKEN_CLOCK_SKEW_SECONDS,
        )
        return decoded
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {str(e)}")
