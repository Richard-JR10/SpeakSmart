import firebase_admin
from firebase_admin import credentials, auth, firestore, storage, auth
from google.cloud.firestore import Client
from google.cloud.storage import Bucket
from core.config import settings
import logging

logger = logging.getLogger(__name__)

_firebase_app = None

def initialize_firebase() -> None:
    global _firebase_app

    if _firebase_app is not None:
        logger.info("Firebase already initialized.")
        return
    
    try:
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": settings.FIREBASE_CLIENT_ID,
            "auth_uri": settings.FIREBASE_AUTH_URI,
            "token_uri": settings.FIREBASE_TOKEN_URI,
            "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
            "universe_domain": settings.FIREBASE_UNIVERSE_DOMAIN
        })

        _firebase_app = firebase_admin.initialize_app(cred, {
            'storageBucket': settings.FIREBASE_STORAGE_BUCKET
        })
        logger.info("Firebase initialized successfully.")
    
    except Exception as e:
        logger.error(f"Error initializing Firebase: {e}")
        raise RuntimeError(f"Firebase initialization failed: {e}")
    
def get_firestore() -> Client:
    if _firebase_app is None:
        raise RuntimeError("Firebase is not initialized. Call initialize_firebase() first.")
    return firestore.client()

def get_storage_bucket() -> Bucket:
    if _firebase_app is None:
        raise RuntimeError("Firebase is not initialized. Call initialize_firebase() first.")
    return storage.bucket()

def get_auth() -> auth:
    if _firebase_app is None:
        raise RuntimeError("Firebase is not initialized. Call initialize_firebase() first.")
    return auth