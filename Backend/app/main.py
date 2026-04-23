import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.db.base import init_db
from app.api.v1.router import router
from app.services.asr import initialize_asr


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    backend_root = Path(__file__).resolve().parents[1]
    log_dir = backend_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "backend.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)


configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    initialize_asr()
    yield

app = FastAPI(
    title="SpeakSmart Backend",
    description="Backend API for the SpeakSmart language learning app.",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True   # <--- This helps keep the token after reload
    },
)

# Allow local frontend origins in development and configurable origins elsewhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SpeakSmart Backend is running! 🚀"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(router)

def custom_openapi():
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema.setdefault("components", {})
    schema["components"].setdefault("securitySchemes", {})

    schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "responses" in operation:
                operation["security"] = [{"BearerAuth": []}]

    return schema   # Do NOT cache it manually


app.openapi = custom_openapi
