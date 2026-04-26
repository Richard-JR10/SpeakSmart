# SpeakSmart Backend Setup Guide

This guide explains how to set up the SpeakSmart backend on a new computer.

The backend uses FastAPI, PostgreSQL, Alembic, Firebase Auth, Cloudflare R2, Google Cloud Text-to-Speech, and OpenAI Whisper.

## Folder Reference

The commands below use these folder names:

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

Optional but recommended:

- FFmpeg, useful if audio decoding fails or if you need to support non-WAV uploads

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

The current frontend converts recordings to WAV before uploading them, so FFmpeg may not be required for the normal local setup.

Install FFmpeg only if audio validation/transcription fails, or if you need to handle browser WebM/non-WAV audio directly.

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

If the project already exists on the computer, open the terminal in the repository root:

```text
SpeakSmart
```

## 3. Install Python 3.14

This backend requires Python `3.14`.

Run from any folder:

```powershell
uv python install 3.14
```

Run from any folder:

```powershell
uv python list
```

The backend also has `.python-version` set to:

```text
3.14
```

## 4. Install Backend Dependencies

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

## 5. Create the `.env` File

Run from the Backend folder:

```powershell
Copy-Item .env.example .env
```

Open `Backend\.env` and fill in the real values.

Minimum local database value:

```env
DATABASE_URL=postgresql+asyncpg://speaksmart:speaksmart_secret@localhost:5432/speaksmart
```

Important values to configure:

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
OPENAI_WHISPER_DEVICE=cpu
OPENAI_WHISPER_LANGUAGE=ja
OPENAI_WHISPER_CACHE_DIR=.cache/openai-whisper
```

Notes:

- Never commit `.env`.
- Ask the project owner for real Firebase and R2 values.
- Keep `FIREBASE_PRIVATE_KEY` quoted and keep `\n` line breaks inside the value.
- Keep `OPENAI_WHISPER_DEVICE=cpu` unless the computer has CUDA set up correctly.

## 6. Add the TTS Service Account File

The `GOOGLE_APPLICATION_CREDENTIALS` value is used by Google Cloud Text-to-Speech when running the phrase seeding script.

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

## 9. Optional: Restore an Existing Database Dump

Use this path if another developer gave you a database dump, for example:

```text
SpeakSmart\Backend\speaksmart.dump
```

This is the easiest handoff path because the database already contains modules, phrases, users, classes, and the saved `reference_audio_url` values that point to R2.

Run from the Backend folder after `docker compose up -d`:

```powershell
docker compose cp .\speaksmart.dump db:/tmp/speaksmart.dump
docker compose exec db pg_restore -U speaksmart -d speaksmart --clean --if-exists /tmp/speaksmart.dump
```

If you restore a dump, you usually do not need to run:

```powershell
uv run python scripts/seed_phrases.py
```

Skip `seed_phrases.py` when:

- the dump already has phrase records
- phrase records already have `reference_audio_url`
- the R2 bucket URLs in the dump still work
- the other user is allowed to use the same R2 bucket or public R2 URLs

Only run `seed_phrases.py` if phrase data is missing, `reference_audio_url` is empty, the old R2 files are gone, or the user needs to upload reference audio to a different R2 bucket.

### Creating the Dump for Another User

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

## 11. Seed Modules, Phrases, and Reference Audio

Run this only if the database is new or empty and you are not restoring a database dump.

Run from the Backend folder:

```powershell
uv run python scripts/seed_phrases.py
```

This script:

- creates default learning modules
- creates default Japanese phrases
- generates reference audio using Google Cloud Text-to-Speech
- uploads the reference audio to Cloudflare R2
- saves phrase metadata and audio URLs in PostgreSQL

Before running this, make sure:

- PostgreSQL is running
- migrations were applied
- `.env` points `GOOGLE_APPLICATION_CREDENTIALS` to the TTS service account JSON
- `.env` has valid Cloudflare R2 credentials
- `serviceAccountKey.json` exists in the Backend folder

If you restored a database dump from another developer, skip this step unless phrase/audio data is missing.

## 12. Run the Backend Server

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

## 13. Run Backend Tests

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

Use this quick checklist to confirm the setup is complete:

- `git --version` works from any folder
- `docker --version` works from any folder
- `docker compose version` works from any folder
- `uv --version` works from any folder
- `ffmpeg -version` works from any folder, if FFmpeg was installed
- `uv python install 3.14` completed
- `uv sync` completed from the Backend folder
- `Backend\.env` exists and has real secrets
- `Backend\serviceAccountKey.json` exists if seeding phrase audio
- PostgreSQL is running from the Backend folder with `docker compose up -d`
- `uv run alembic upgrade head` completed from the Backend folder
- database dump was restored from the Backend folder, if using a shared dump
- `npm run setup:whisper` completed from the repository root, or `uv run python scripts/prefetch_whisper_model.py` completed from the Backend folder
- `uv run python scripts/seed_phrases.py` completed from the Backend folder only if using a fresh empty database without a dump
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

### Whisper model download is slow

This is normal the first time. The model is cached in:

```text
Backend\.cache\openai-whisper
```

### FFmpeg error

Run from any folder:

```powershell
ffmpeg -version
```

If it fails, install FFmpeg and add it to `PATH`.

### Firebase private key error

Use quotes and escaped newlines:

```env
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### Seeding fails during Text-to-Speech

Check:

- `GOOGLE_APPLICATION_CREDENTIALS` points to the right JSON file
- the TTS service account JSON file exists in the Backend folder
- the Google Cloud project has Text-to-Speech enabled
- the service account has permission to use Text-to-Speech

### Seeding fails during R2 upload

Check:

- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`
- `R2_PUBLIC_URL`
