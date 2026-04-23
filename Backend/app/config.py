from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: str = "development"
    SECRET_KEY: str

    DATABASE_URL: str

    FIREBASE_API_KEY: str
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_CLIENT_ID: str
    FIREBASE_AUTH_URI: str
    FIREBASE_TOKEN_URI: str
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str
    FIREBASE_CLIENT_X509_CERT_URL: str
    FIREBASE_UNIVERSE_DOMAIN: str

    R2_ACCOUNT_ID: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    R2_PUBLIC_URL: str

    GOOGLE_APPLICATION_CREDENTIALS: str

    MAX_AUDIO_SIZE_MB: int = 10
    ASR_PROVIDER: str = "openai_whisper"
    OPENAI_WHISPER_MODEL: str = "small"
    OPENAI_WHISPER_DEVICE: str = "cpu"
    OPENAI_WHISPER_LANGUAGE: str = "ja"
    OPENAI_WHISPER_CACHE_DIR: str = ".cache/openai-whisper"
    VERIFICATION_MAX_CANDIDATES: int = 8
    VERIFICATION_MIN_VOICED_RATIO: float = 0.2
    VERIFICATION_ACCEPTANCE_CONFIDENCE: float = 0.78
    VERIFICATION_WRONG_PHRASE_CONFIDENCE: float = 0.82
    VERIFICATION_MIN_MARGIN: float = 0.12
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

settings = Settings()
