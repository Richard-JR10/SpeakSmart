# SpeakSmart Backend Setup Guide

This guide explains how to set up the SpeakSmart backend on another computer.

The backend uses FastAPI, PostgreSQL, Alembic, Firebase Auth, Cloudflare R2, Google Cloud Text-to-Speech, and OpenAI Whisper.

## Folder Reference

```text
Repository root: SpeakSmart
Backend folder:  SpeakSmart\Backend
Frontend folder: SpeakSmart\Frontend
```

When a step says **Run from the repository root**, open the terminal in `SpeakSmart`.

When a step says **Run from the Backend folder**, open the terminal in `SpeakSmart\Backend`.

When a step says **Run from any folder**, the command does not depend on the project folder.

## 1. Install Required Software

Install these first:

- Git
- Docker Desktop
- `uv`

Optional:

- FFmpeg, only if audio validation/transcription fails or if you need to support non-WAV uploads

### Git

Download Git:

```text
https://git-scm.com/downloads
```

Run from any folder:

```powershell
git --version
```

### Docker Desktop

Download Docker Desktop:

```text
https://docs.docker.com/desktop/
```

Open Docker Desktop after installing and keep it running.

Run from any folder:

```powershell
docker --version
docker compose version
```

### uv

`uv` manages the Python version, virtual environment, and backend dependencies.

Run from any folder:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen the terminal after installing.

Run from any folder:

```powershell
uv --version
```

### Optional: FFmpeg

The current frontend converts recordings to WAV before uploading them, so FFmpeg may not be required for normal local setup.

Download FFmpeg:

```text
https://ffmpeg.org/download.html
```

Run from any folder:

```powershell
ffmpeg -version
```

If this command is not found and you need FFmpeg, add FFmpeg's `bin` folder to the system `PATH`, then reopen the terminal.

## 2. Clone the Project

Run this from the folder where you want to store the project, for example `Documents\code`.

Run from your chosen parent folder:

```powershell
git clone <repository-url>
cd SpeakSmart
```

After this, your terminal is in the repository root.

If the project already exists on the computer, open the terminal in:

```text
SpeakSmart
```

## 3. Install Python and Backend Dependencies

This backend requires Python `3.14`.

Run from any folder:

```powershell
uv python install 3.14
```

Run from any folder:

```powershell
uv python list
```

Then install the backend dependencies.

Run from the repository root:

```powershell
cd Backend
uv sync
```

Or, if your terminal is already in the Backend folder:

```powershell
uv sync
```

This installs all backend dependencies from `pyproject.toml` and `uv.lock`, including FastAPI, SQLAlchemy, Alembic, Firebase Admin, Google Cloud Text-to-Speech, Cloudflare R2 dependencies, OpenAI Whisper, PyTorch, and test tools.

You do not need to manually run `pip install` for this project.

## 4. Create and Configure `.env`

Run from the Backend folder:

```powershell
Copy-Item .env.example .env
```

Open `Backend\.env` and fill in the real values.

Minimum local database value:

```env
DATABASE_URL=postgresql+asyncpg://speaksmart:speaksmart_secret@localhost:5432/speaksmart
```

Important values:

```env
APP_ENV=development
SECRET_KEY=change-this-to-a-long-random-string

DATABASE_URL=postgresql+asyncpg://speaksmart:speaksmart_secret@localhost:5432/speaksmart

FIREBASE_API_KEY=
FIREBASE_PROJECT_ID=
FIREBASE_PRIVATE_KEY_ID=
FIREBASE_PRIVATE_KEY=
FIREBASE_CLIENT_EMAIL=
FIREBASE_CLIENT_ID=
FIREBASE_AUTH_URI=
FIREBASE_TOKEN_URI=
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=
FIREBASE_CLIENT_X509_CERT_URL=
FIREBASE_UNIVERSE_DOMAIN=

R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=

GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json

MAX_AUDIO_SIZE_MB=10
ASR_PROVIDER=openai_whisper
OPENAI_WHISPER_MODEL=small
OPENAI_WHISPER_DEVICE=auto
OPENAI_WHISPER_LANGUAGE=ja
OPENAI_WHISPER_CACHE_DIR=.cache/openai-whisper

PHONEME_ASSESSMENT_PROVIDER=hybrid_hf_ctc
PHONEME_CTC_MODEL_ID=sakasegawa/japanese-wav2vec2-large-hiragana-ctc
PHONEME_CTC_BASE_MODEL_ID=reazon-research/japanese-wav2vec2-large
PHONEME_CTC_CHECKPOINT_FILENAME=best-medium-ep5-inference.pt
PHONEME_CTC_DEVICE=auto
PHONEME_CTC_CACHE_DIR=.cache/hf-phoneme-ctc
PHONEME_CTC_FALLBACK_ENABLED=true
```

Notes:

- Never commit `.env`.
- Keep `FIREBASE_PRIVATE_KEY` quoted and keep `\n` line breaks inside the value.
- Use `OPENAI_WHISPER_DEVICE=auto` to use CUDA when PyTorch can see a GPU and fall back to CPU otherwise. Use `cpu` or `cuda` only when you want to force a specific path while testing.

## 5. Get Cloudflare R2 Credentials

R2 stores the actual audio files. The database only stores URLs such as `reference_audio_url`.

Get these values from Cloudflare:

```env
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=
```

### Where to Get Each Value

`R2_BUCKET_NAME`

- Go to Cloudflare Dashboard.
- Open **R2** or **Storage & databases > R2**.
- Create or choose the bucket used for SpeakSmart audio.
- Use the bucket name as `R2_BUCKET_NAME`.

`R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY`

- Go to **R2 > Manage API tokens**.
- Create an R2 API token.
- Use permissions that allow object read and write.
- Copy the generated Access Key ID and Secret Access Key.
- Save the secret immediately because Cloudflare will not show it again.

`R2_ACCOUNT_ID`

- Cloudflare R2 S3-compatible clients use an endpoint like:

```text
https://<ACCOUNT_ID>.r2.cloudflarestorage.com
```

- Use the Cloudflare account ID for `R2_ACCOUNT_ID`.

`R2_PUBLIC_URL`

- Open the R2 bucket settings.
- Use the bucket's Public Development URL or custom public domain.
- This must be the public base URL for uploaded audio files.

Example:

```env
R2_ACCOUNT_ID=abc123...
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=speaksmart-audio
R2_PUBLIC_URL=https://pub-your-bucket.r2.dev
```

Official Cloudflare docs:

- R2 API tokens: https://developers.cloudflare.com/r2/api/tokens/
- Public buckets: https://developers.cloudflare.com/r2/buckets/public-buckets/
- S3-compatible setup: https://developers.cloudflare.com/r2/get-started/s3/

## 6. Configure the TTS Service Account

The `GOOGLE_APPLICATION_CREDENTIALS` value is used by Google Cloud Text-to-Speech when running `seed_phrases.py`.

Best option for TTS:

- Go to Google Cloud Console.
- Select the project where Cloud Text-to-Speech API is enabled.
- Create or choose a service account.
- Give it permission to use Cloud Text-to-Speech.
- Create a JSON key for that service account.

The Firebase Admin SDK service account can also work if it belongs to the same Google Cloud project and has permission to use Text-to-Speech.

Put the JSON key in the Backend folder:

```text
SpeakSmart\Backend\serviceAccountKey.json
```

Then make sure `.env` points to it:

```env
GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json
```

Do not commit `serviceAccountKey.json`.

## 7. Start the Local Database

Make sure Docker Desktop is running first.

Run from the Backend folder:

```powershell
docker compose up -d
```

If your Docker version still uses the older command, run from the Backend folder:

```powershell
docker-compose up -d
```

This starts PostgreSQL using `Backend\docker-compose.yaml`.

Local database settings:

```text
host: localhost
port: 5432
database: speaksmart
username: speaksmart
password: speaksmart_secret
```

Adminer also starts at:

```text
http://localhost:8080
```

To check the containers, run from the Backend folder:

```powershell
docker compose ps
```

## 8. Run Database Migrations

Run from the Backend folder:

```powershell
uv run alembic upgrade head
```

Run this command:

- the first time you set up the backend
- after pulling new migration files
- after resetting the local database

## 9. Choose Data Setup Path

Choose only one path.

Use **Path A** if this is a trusted teammate who should use the project owner's current database and R2 audio.

Use **Path B** if this computer should have its own independent R2 bucket and generated phrase audio.

### Path A: Recommended Fast Path - Restore Shared Database Dump

This is the easiest handoff path for trusted teammates.

Use this path when the project owner gives you:

- `speaksmart.dump`
- the same R2 values used by the dumped database:

```env
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=
```

The `R2_PUBLIC_URL` must match the URLs already saved in the database dump.

Put the dump file here:

```text
SpeakSmart\Backend\speaksmart.dump
```

Run from the Backend folder after `docker compose up -d`:

```powershell
docker compose cp .\speaksmart.dump db:/tmp/speaksmart.dump
docker compose exec db pg_restore -U speaksmart -d speaksmart --clean --if-exists /tmp/speaksmart.dump
```

After restoring the dump, skip:

```powershell
uv run python scripts/seed_phrases.py
```

Why this works:

- The dump already contains modules and phrases.
- The phrase rows already contain `reference_audio_url`.
- The actual `.wav` files are already in R2.

Why a different R2 bucket can break:

- The database stores full `reference_audio_url` values.
- The backend extracts object keys by stripping the configured `R2_PUBLIC_URL`.
- If the dump has the owner's R2 URLs but the other user sets a different `R2_PUBLIC_URL`, reference audio downloads can fail.

Only use this path if the other user is allowed to use the same R2 bucket/settings or the same public R2 URLs.

#### Creating the Dump for Another User

If you are the person sharing your current local database, run this on your computer.

Run from the Backend folder:

```powershell
docker compose exec db pg_dump -U speaksmart -d speaksmart -Fc -f /tmp/speaksmart.dump
docker compose cp db:/tmp/speaksmart.dump .\speaksmart.dump
```

Send this file to the other user:

```text
SpeakSmart\Backend\speaksmart.dump
```

Do not commit `speaksmart.dump` if it contains real users, class data, attempts, or other private information.

### Path B: Independent Setup - Use Your Own R2 and Generate Phrases

Use this path if the other user should not use the owner's R2 bucket.

Before running this path, make sure:

- `.env` uses the user's own R2 bucket values.
- `.env` points `GOOGLE_APPLICATION_CREDENTIALS` to a TTS service account JSON.
- `serviceAccountKey.json` exists in the Backend folder.
- Cloud Text-to-Speech is enabled for the Google Cloud project.

Run from the Backend folder:

```powershell
uv run python scripts/seed_phrases.py
```

This script:

- creates default learning modules
- creates default Japanese phrases
- generates reference audio using Google Cloud Text-to-Speech
- uploads the reference audio to the configured R2 bucket
- saves phrase metadata and R2 audio URLs in PostgreSQL

Do not restore the owner's dump for this path unless the phrase audio URLs are cleared, regenerated, or migrated to the user's own R2 bucket.

## 10. Download the Whisper Model

Whisper is used for speech recognition.

Recommended option, run from the repository root:

```powershell
npm run setup:whisper
```

This runs `scripts/setup-whisper.ps1`, which:

- writes the local Whisper settings into `Backend\.env`
- runs `uv sync`
- creates `Backend\.cache\openai-whisper`
- downloads the configured Whisper model

If your terminal is currently in the Backend folder, go up to the repository root first:

```powershell
cd ..
npm run setup:whisper
```

You can also run the PowerShell script directly from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-whisper.ps1
```

Manual backend-only option, run from the Backend folder:

```powershell
uv run python scripts/prefetch_whisper_model.py
```

By default this downloads:

```env
OPENAI_WHISPER_MODEL=small
```

into:

```env
OPENAI_WHISPER_CACHE_DIR=.cache/openai-whisper
```

The first download can take a while. After it is cached, backend startup is faster.

## 11. Run the Backend Server

Run from the Backend folder:

```powershell
uv run uvicorn app.main:app --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

Useful URLs:

```text
Health check: http://127.0.0.1:8000/health
Swagger docs:  http://127.0.0.1:8000/docs
API v1:        http://127.0.0.1:8000/api/v1
```

Expected health response:

```json
{"status":"healthy"}
```

## 12. Run Backend Tests

Run from the Backend folder:

```powershell
uv run pytest
```

Run from the Backend folder:

```powershell
uv run pytest -v --cov=app
```

Run from the Backend folder:

```powershell
uv run python scripts/test_scoring.py
```

## 13. Run Objective Pronunciation Benchmarks

SpeakSmart uses AI as the pronunciation judge. Teachers do not need to label pronunciation correctness. To tune accuracy, create a JSON file with native/reference audio and controlled error recordings:

```json
[
  {
    "case_id": "missing-small-tsu-01",
    "target_text": "きって",
    "reference_audio_path": "benchmark_audio/kitte_reference.wav",
    "student_audio_path": "benchmark_audio/kitte_missing_small_tsu.wav",
    "expected_issue": "small_tsu"
  }
]
```

Run from the Backend folder:

```powershell
uv run python scripts/run_pronunciation_benchmark.py .\benchmark_cases.json
```

Optional external AI benchmark credentials can be added later:

```env
SPEECHSUPER_APP_KEY=
SPEECHSUPER_SECRET_KEY=
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=
```

These services are benchmark references only. Production scoring still uses SpeakSmart's local AI pipeline.

## 14. Connect the Frontend

Start the backend first.

If your terminal is in the repository root, run:

```powershell
cd Frontend
npm install --legacy-peer-deps
npm run dev
```

If your terminal is in the Backend folder, run:

```powershell
cd ..\Frontend
npm install --legacy-peer-deps
npm run dev
```

The frontend usually runs at:

```text
http://localhost:5173
```

The backend already allows these frontend origins:

```text
http://localhost:5173
http://127.0.0.1:5173
http://localhost:4173
http://127.0.0.1:4173
```

If another computer or phone needs to connect, add it to `.env`:

```env
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://192.168.1.20:5173
```

## Daily Startup Commands

From the repository root:

```powershell
cd Backend
docker compose up -d
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

From the Backend folder:

```powershell
docker compose up -d
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## Fresh Setup Checklist

Use this quick checklist to confirm setup is complete:

- `git --version` works from any folder
- `docker --version` works from any folder
- `docker compose version` works from any folder
- `uv --version` works from any folder
- `ffmpeg -version` works from any folder, if FFmpeg was installed
- `uv python install 3.14` completed
- `uv sync` completed from the Backend folder
- `Backend\.env` exists and has real secrets
- R2 values are configured in `Backend\.env`
- `Backend\serviceAccountKey.json` exists if running `seed_phrases.py`
- PostgreSQL is running from the Backend folder with `docker compose up -d`
- `uv run alembic upgrade head` completed from the Backend folder
- either the shared dump was restored with the owner's R2 settings, or `seed_phrases.py` was run with the user's own R2 settings
- `npm run setup:whisper` completed from the repository root, or `uv run python scripts/prefetch_whisper_model.py` completed from the Backend folder
- `uv run uvicorn app.main:app --reload` starts the server from the Backend folder
- `http://127.0.0.1:8000/health` returns healthy

## Common Problems

### `uv` is not recognized

Close and reopen the terminal. If it still fails, reinstall `uv` and make sure its install folder is on `PATH`.

### Python 3.14 is missing

Run from any folder:

```powershell
uv python install 3.14
```

Then run from the Backend folder:

```powershell
uv sync
```

### Docker is running but the database will not connect

Run from the Backend folder:

```powershell
docker compose ps
```

Make sure `.env` has:

```env
DATABASE_URL=postgresql+asyncpg://speaksmart:speaksmart_secret@localhost:5432/speaksmart
```

### Port 5432 is already used

Another PostgreSQL instance is probably running. Stop it, or change the database port in `docker-compose.yaml` and update `DATABASE_URL`.

### Alembic migration fails

Usually this means PostgreSQL is not running or `DATABASE_URL` is wrong.

Run from the Backend folder:

```powershell
docker compose up -d
uv run alembic upgrade head
```

### Restored Dump Cannot Download Reference Audio

Check:

- the other user is using the owner's same R2 values
- `R2_PUBLIC_URL` exactly matches the URL saved in `reference_audio_url`
- the R2 bucket still contains the `reference-audio/...` files
- the R2 access key has object read permission

If the other user wants to use their own R2 bucket, use Path B and run `seed_phrases.py` instead of restoring the dump.

### Whisper Model Download Is Slow

This is normal the first time. The model is cached in:

```text
Backend\.cache\openai-whisper
```

### FFmpeg Error

Run from any folder:

```powershell
ffmpeg -version
```

If it fails, install FFmpeg and add it to `PATH`.

### Firebase Private Key Error

Use quotes and escaped newlines:

```env
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### Seeding Fails During Text-to-Speech

Check:

- `GOOGLE_APPLICATION_CREDENTIALS` points to the right JSON file
- the TTS service account JSON file exists in the Backend folder
- the Google Cloud project has Text-to-Speech enabled
- the service account has permission to use Text-to-Speech

### Seeding Fails During R2 Upload

Check:

- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`
- `R2_PUBLIC_URL`
