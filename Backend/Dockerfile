FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml ./
COPY uv.lock ./
COPY scripts ./scripts

ENV ASR_PROVIDER=openai_whisper
ENV OPENAI_WHISPER_MODEL=small
ENV OPENAI_WHISPER_DEVICE=cpu
ENV OPENAI_WHISPER_LANGUAGE=ja
ENV OPENAI_WHISPER_CACHE_DIR=/app/.cache/openai-whisper

RUN uv sync --frozen --no-dev
RUN uv run python scripts/prefetch_whisper_model.py

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
