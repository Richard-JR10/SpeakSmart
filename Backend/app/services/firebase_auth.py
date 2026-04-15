import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

from app.config import settings

_credential_dict = {
    "type": "service_account",
    "project_id": settings.FIREBASE_PROJECT_ID,
    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
    "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
    "client_email": settings.FIREBASE_CLIENT_EMAIL,
    "client_id": settings.FIREBASE_CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
}

_cred = credentials.Certificate(_credential_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(_cred)

def verify_firebase_token(id_token: str) -> dict:
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        raise ValueError(f"Invalid Firebase token: {str(e)}")











    