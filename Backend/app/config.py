from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
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
    OPENAI_WHISPER_DEVICE: str = "auto"
    OPENAI_WHISPER_LANGUAGE: str = "ja"
    OPENAI_WHISPER_CACHE_DIR: str = ".cache/openai-whisper"
    VERIFICATION_MAX_CANDIDATES: int = 8
    VERIFICATION_MIN_VOICED_RATIO: float = 0.2
    VERIFICATION_ACCEPTANCE_CONFIDENCE: float = 0.78
    VERIFICATION_WRONG_PHRASE_CONFIDENCE: float = 0.82
    VERIFICATION_MIN_MARGIN: float = 0.12
    PHONEME_ASSESSMENT_PROVIDER: str = "azure_pronunciation_assessment"
    PRONUNCIATION_BENCHMARK_ENABLED: bool = True
    PRONUNCIATION_BENCHMARK_MIN_CORRECT_SCORE: float = 85.0
    PRONUNCIATION_BENCHMARK_MAX_ISSUE_SCORE: float = 82.0
    SPEECHSUPER_APP_KEY: str | None = None
    SPEECHSUPER_SECRET_KEY: str | None = None
    AZURE_SPEECH_KEY: str | None = None
    AZURE_SPEECH_REGION: str | None = None
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    # Redis — optional; in-memory storage used when unset (fine for single-worker dev/prod)
    REDIS_URL: str | None = None

    # Rate limits expressed as slowapi "count/period" strings; override in .env without code changes
    RATE_LIMIT_AUDIO_SUBMISSION:  str = "60/hour"   # Tier 1 — practice attempts (Whisper + Azure pipeline)
    RATE_LIMIT_EXERCISE_SUBMISSION: str = "30/hour" # Tier 1 — graded assignment submissions
    RATE_LIMIT_AUTH_REGISTER:     str = "5/hour"    # Tier 2 — IP-keyed account creation
    RATE_LIMIT_CLASS_JOIN:        str = "20/hour"   # Tier 2 — join code attempts
    RATE_LIMIT_JOIN_CODE_REGEN:   str = "10/hour"   # Tier 2 — join code regeneration
    RATE_LIMIT_ANALYTICS:         str = "60/minute" # Tier 3 — instructor analytics queries
    RATE_LIMIT_PROGRESS:          str = "60/minute" # Tier 3 — student progress reads
    RATE_LIMIT_ATTEMPTS_READ:     str = "60/minute" # Tier 3 — attempt history reads
    RATE_LIMIT_PUBLIC:            str = "30/minute" # Tier 4 — IP-keyed health/root endpoints

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

settings = Settings()
