# AGENT.md — SpeakSmart

> Japanese Pronunciation Analysis and Language Training System
> Gordon College — Tourism Department | Olongapo City, Philippines

This file is the authoritative reference for any AI agent, developer, or LLM working on the SpeakSmart codebase. Read this before making any changes.

---

## Project Overview

SpeakSmart is a full-stack PWA that enables tourism students to practice Japanese pronunciation and receive AI-driven scoring. Instructors monitor student performance through a role-based analytics dashboard.

| Field | Value |
|---|---|
| Target language | Japanese (primary) |
| Target users | Tourism students + instructors |
| Student interface | Mobile PWA (Vue 3) |
| Instructor interface | Web dashboard (Vue 3) |
| Backend | Python FastAPI |
| Version | 1.0 |

---

## Repository Structure
@ is set to /frontend/src. You can use this for frontend.
```
SpeakSmart/
├── backend/                  ← FastAPI backend
│   ├── app/
│   │   ├── main.py           ← FastAPI entry point + lifespan
│   │   ├── config.py         ← Pydantic Settings from .env
│   │   ├── api/v1/
│   │   │   ├── router.py     ← Aggregates all routers
│   │   │   └── endpoints/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── modules.py
│   │   │       ├── phrases.py
│   │   │       ├── attempts.py
│   │   │       ├── progress.py
│   │   │       ├── analytics.py
│   │   │       └── exercises.py
│   │   ├── core/
│   │   │   ├── dependencies.py   ← get_current_user, require_instructor
│   │   │   ├── exceptions.py     ← Custom HTTP exceptions
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── base.py           ← SQLAlchemy async engine + Base
│   │   │   ├── session.py        ← get_db dependency
│   │   │   └── models/
│   │   │       ├── user.py
│   │   │       ├── class_.py
│   │   │       ├── module.py
│   │   │       ├── phrase.py
│   │   │       ├── attempt.py
│   │   │       ├── progress.py
│   │   │       ├── exercise.py
│   │   │       └── analytics.py
│   │   ├── schemas/              ← Pydantic request/response models
│   │   └── services/
│   │       ├── firebase_auth.py  ← Firebase Admin SDK
│   │       ├── r2_storage.py     ← Cloudflare R2 via boto3
│   │       ├── speech.py         ← librosa feature extraction
│   │       ├── scoring.py        ← DTW scoring pipeline
│   │       ├── progress.py       ← Progress update helper
│   │       └── tts.py            ← Google TTS
│   ├── alembic/                  ← Database migrations
│   ├── scripts/
│   │   ├── phrase_data.py        ← All 36 tourism phrases
│   │   ├── seed_phrases.py       ← TTS + R2 + DB seeder
│   │   ├── test_r2.py
│   │   ├── test_scoring.py
│   │   ├── get_test_token.py
│   │   └── start.sh              ← Cloud Run startup
│   ├── tests/
│   ├── .env                      ← Never commit
│   ├── .env.example
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── pyproject.toml
│
└── frontend/                 ← Vue 3 PWA
    ├── src/
    │   ├── api/              ← All Axios API call functions
    │   ├── stores/           ← Pinia state stores
    │   ├── router/           ← Vue Router + guards
    │   ├── layouts/          ← StudentLayout, InstructorLayout
    │   ├── views/
    │   │   ├── student/      ← 8 student screens
    │   │   └── instructor/   ← 4 instructor screens
    │   ├── components/shared/
    │   ├── composables/      ← useAudioRecorder, usePWA
    │   ├── types/            ← TypeScript interfaces
    │   ├── firebase.ts
    │   ├── main.ts
    │   └── style.css
    ├── public/icons/
    ├── index.html
    ├── vite.config.ts
    └── tailwind.config.js
```

---

## Tech Stack

### Backend
Check the pyproject.toml for the exact version
| Layer | Technology |
|---|---|
| Language | Python 3.14 |
| Framework | FastAPI (async) |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Package manager | uv |
| Auth | Firebase Admin SDK (JWT verification only) |
| Audio processing | librosa + scipy (DTW) |
| Object storage | Cloudflare R2 via boto3 |
| Reference audio | Google Cloud TTS (ja-JP-Wavenet-B) |
| Database | PostgreSQL (Docker locally, Cloud SQL deployed) |
| Hosting | Google Cloud Run |

Check the package-lock.json for the exact version
### Frontend
| Layer | Technology |
|---|---|
| Framework | Vue 3 + Vite + TypeScript |
| State | Pinia |
| Router | Vue Router 4 |
| HTTP | Axios |
| Auth | Firebase Auth SDK |
| Styling | Tailwind CSS + CSS variables |
| PWA | vite-plugin-pwa + Workbox |
| Hosting | Cloudflare Pages |

---

## Environment Variables

### Backend `.env`
```env
APP_ENV=development
SECRET_KEY=

DATABASE_URL=postgresql+asyncpg://speaksmart:speaksmart_secret@localhost:5432/speaksmart

FIREBASE_PROJECT_ID=
FIREBASE_PRIVATE_KEY_ID=
FIREBASE_PRIVATE_KEY=
FIREBASE_CLIENT_EMAIL=
FIREBASE_CLIENT_ID=

R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=speaksmart-audio
R2_PUBLIC_URL=

GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json

MAX_AUDIO_SIZE_MB=10
```

### Frontend `.env`
```env
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=

VITE_API_BASE_URL=http://localhost:8000
```

---

## Local Development

### Backend
```bash
cd backend

# Start PostgreSQL
docker-compose up -d

# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head

# Seed phrases + generate TTS + upload to R2 (run once)
uv run python scripts/seed_phrases.py

# Start API server
uv run uvicorn app.main:app --reload
# API available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Start dev server
npm run dev
# Available at http://localhost:5173
```

---

## Database

### Tables
| Table | Purpose |
|---|---|
| `users` | All users — role field distinguishes student/instructor |
| `classes` | Course sections taught by an instructor |
| `modules` | Lesson modules by tourism topic |
| `phrases` | Japanese phrases with reference audio URL |
| `attempts` | Every scored pronunciation attempt |
| `progress_summary` | Rolling averages per student per module |
| `exercises` | Custom drill sets created by instructors |
| `exercise_phrases` | Junction — exercises ↔ phrases |
| `exercise_assignments` | Which students are assigned which exercises |
| `class_analytics` | Weekly pre-computed class-wide statistics |

### Key rules
- `users.uid` is the Firebase UID — primary key across all tables
- `users.role` is either `"student"` or `"instructor"` — never anything else
- `attempts` is append-only — never update or delete attempt records
- `progress_summary` is upserted automatically after every attempt via `services/progress.py`
- All timestamps are UTC

### Migrations
```bash
# Create new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Health check |
| GET | `/api/v1/auth/me` | Any | Current user profile |
| GET | `/api/v1/auth/verify` | Any | Verify token |
| PATCH | `/api/v1/users/me` | Any | Update display name / class |
| GET | `/api/v1/modules` | Any | List all modules |
| GET | `/api/v1/modules/{id}` | Any | Get single module |
| GET | `/api/v1/modules/{id}/phrases` | Any | Get phrases for module |
| POST | `/api/v1/modules` | Instructor | Create module |
| GET | `/api/v1/phrases/{id}` | Any | Get single phrase |
| POST | `/api/v1/phrases` | Instructor | Create phrase |
| DELETE | `/api/v1/phrases/{id}` | Instructor | Delete phrase |
| POST | `/api/v1/attempts` | Any | Submit audio for scoring |
| GET | `/api/v1/attempts/{uid}` | Any | Get attempt history |
| GET | `/api/v1/attempts/{uid}/{id}` | Any | Get attempt detail |
| GET | `/api/v1/progress/{uid}` | Any | Student dashboard data |
| GET | `/api/v1/progress/{uid}/module/{id}` | Any | Module progress |
| GET | `/api/v1/analytics/class/{id}` | Instructor | Class overview |
| GET | `/api/v1/analytics/students/{id}` | Instructor | All students stats |
| GET | `/api/v1/analytics/student/{uid}` | Instructor | Student drill-down |
| GET | `/api/v1/analytics/heatmap/{id}` | Instructor | Phoneme heatmap |
| POST | `/api/v1/exercises` | Instructor | Create exercise |
| POST | `/api/v1/exercises/{id}/assign` | Instructor | Assign to students |
| GET | `/api/v1/exercises/instructor/mine` | Instructor | My exercises |
| GET | `/api/v1/exercises/detail/{id}` | Instructor | Exercise detail |
| GET | `/api/v1/exercises/student/{uid}` | Any | Student exercises |
| PATCH | `/api/v1/exercises/{id}/complete` | Any | Mark complete |
| DELETE | `/api/v1/exercises/{id}` | Instructor | Delete exercise |

### Auth rules
- All protected endpoints require `Authorization: Bearer <Firebase ID Token>`
- Students can only access their own data (`student_uid` must match `current_user.uid`)
- Instructors can access any student data within their class
- Role is enforced via `require_instructor` dependency — never trust client-supplied role

---

## Speech Scoring Pipeline

The core scoring logic lives in `backend/app/services/scoring.py`.

### Flow (called in `attempts.py`)
```
1. validate_audio(student_bytes)          — size, duration, silence check
2. extract_features(student_bytes)        — MFCC (13 coeff), duration, RMS
3. extract_features(reference_bytes)      — same for reference audio
4. dtw_distance(student_mfcc, ref_mfcc)   — full DTW on all 13 coefficients
5. score_mora_timing(student_dur, ref_dur) — duration ratio scorer
6. score_consonants(student_mfcc, ref_mfcc) — upper MFCC bands (6–12)
7. score_vowels(student_mfcc, ref_mfcc)   — lower MFCC bands (1–5)
8. weighted_score = dtw*0.10 + mora*0.35 + consonant*0.35 + vowel*0.20
9. generate_feedback(scores)              — human-readable message
10. build_phoneme_error_map(scores)       — per-component flags for frontend
```

### Scoring weights
| Component | Weight | What it measures |
|---|---|---|
| DTW distance | 10% | Overall acoustic similarity |
| Mora timing | 35% | Long vowel duration accuracy |
| Consonant accuracy | 35% | Upper MFCC — R-sound and consonant clarity |
| Vowel purity | 20% | Lower MFCC — clean 5-vowel system |

### Score thresholds
| Range | Label |
|---|---|
| 85–100% | Excellent |
| 70–84% | Good |
| 55–69% | Needs Practice |
| 0–54% | Needs Significant Work |

### Audio format
- Sample rate: 16000 Hz (always resampled by librosa)
- Channels: Mono
- Format: WAV or WebM (browser MediaRecorder output)
- Maximum size: 10MB
- Minimum duration: 0.3 seconds

---

## Cloudflare R2 Bucket Structure

```
speaksmart-audio/
├── reference-audio/
│   ├── module_greetings/
│   │   ├── ph_greet_001.wav
│   │   └── ...
│   ├── module_hotel/
│   ├── module_directions/
│   ├── module_food/
│   ├── module_emergency/
│   └── module_tour_guide/
└── student-audio/
    └── {student_uid}/
        └── {attempt_id}.wav
```

### Rules
- Reference audio is generated once by the TTS seeder — never overwrite unless re-seeding intentionally
- Student audio is uploaded after scoring — the bytes are processed in RAM first, then stored
- Never store audio to disk — all processing is in-memory
- `get_object_key_from_url(url)` extracts the R2 key from a full public URL

---

## Frontend Architecture

### Role-based routing
```
/ (onboarding)          → public
/login                  → public
/home                   → student only
/lessons                → student only
/practice/:mid/:pid     → student only
/results                → student only
/progress               → student only
/settings               → student only
/instructor             → instructor only
/instructor/students    → instructor only
/instructor/heatmap     → instructor only
/instructor/exercises   → instructor only
```

The router guard in `src/router/index.ts` enforces these rules. If an authenticated user visits the wrong role's route, they are redirected to their home route.

### Pinia stores
| Store | File | Manages |
|---|---|---|
| `useAuthStore` | `stores/auth.ts` | Firebase auth state, user profile, sign in/out |
| `useModulesStore` | `stores/modules.ts` | Lesson modules and phrases (cached by module_id) |
| `useAttemptsStore` | `stores/attempts.ts` | Attempt submission, last result, history |
| `useProgressStore` | `stores/progress.ts` | Student dashboard, per-module progress |

### API layer
All HTTP calls go through `src/api/axios.ts` which automatically:
- Attaches the Firebase JWT to every request
- Signs out and redirects to `/login` on 401 responses
- Has a 30s default timeout (60s for attempt submission)

### PWA
- Service worker registered via `vite-plugin-pwa` with Workbox
- Reference audio from R2 is cached with `CacheFirst` (30 days)
- Module API responses cached with `NetworkFirst` (1 hour)
- Install prompt handled by `usePWA` composable
- Update notifications shown via `UpdateBanner` component

---

## Design Tokens

```css
--color-primary:       #1D9E75   /* teal green — main brand color */
--color-primary-dark:  #157a5a   /* hover states */
--color-primary-light: #e6f7f2   /* backgrounds, chips */
--color-danger:        #EF4444
--color-warning:       #F59E0B
--color-success:       #10B981
--color-text:          #111827
--color-subtext:       #6B7280
--color-border:        #E5E7EB
--color-bg:            #F9FAFB
--radius:              12px
```

Max content width is `480px` (mobile-first). The instructor dashboard breaks out of this via `InstructorLayout` which uses a full-width sidebar + content layout.

---

## Deployment

### Backend — Google Cloud Run
```bash
# Build and push image
docker build -t asia-southeast1-docker.pkg.dev/speaksmart-backend/speaksmart/api:latest .
docker push asia-southeast1-docker.pkg.dev/speaksmart-backend/speaksmart/api:latest

# Deploy
gcloud run deploy speaksmart-api \
  --image=asia-southeast1-docker.pkg.dev/speaksmart-backend/speaksmart/api:latest \
  --region=asia-southeast1 \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --memory=2Gi \
  --cpu=2 \
  --add-cloudsql-instances=speaksmart-backend:asia-southeast1:speaksmart-db
```

All secrets are stored in Google Secret Manager — never passed as plain env vars in production.

The startup script `scripts/start.sh` runs `alembic upgrade head` before starting uvicorn, so migrations apply automatically on every deploy.

### Frontend — Cloudflare Pages
```bash
cd frontend
npm run build
# Deploy the dist/ folder to Cloudflare Pages
# Set VITE_API_BASE_URL to your Cloud Run URL in Cloudflare Pages env vars
```

---

## Critical Rules for AI Agents

1. **Never modify the scoring weights** in `scoring.py` without explicit instruction. The 10/35/35/20 weights are tuned for Filipino learner phoneme error patterns.

2. **Never store audio to disk**. All audio processing must remain in-memory (RAM). The `validate_audio` and `extract_features` functions use `io.BytesIO` — keep it that way.

3. **Never skip the Firebase JWT verification**. The `get_current_user` dependency in `dependencies.py` must be on every protected endpoint. Do not bypass it for convenience.

4. **Never trust the client-supplied role**. Role is always read from `current_user.role` (fetched from the database after JWT verification), never from request body or query params.

5. **Never commit `.env` files or `serviceAccountKey.json`**. Both are in `.gitignore`. If you see them in a diff, stop and flag it.

6. **Always use `uv run` for Python commands** in the backend, never `python` directly. This ensures the correct virtualenv is used.

7. **Always use `--legacy-peer-deps`** for `npm install` in the frontend. Vite 8 has peer dependency conflicts with some plugins.

8. **The seeder is idempotent** — `seed_phrases.py` skips phrases that already have a `reference_audio_url`. It is safe to re-run but will not regenerate existing audio.

9. **All DB timestamps are UTC**. Always use `datetime.now(timezone.utc)` — never `datetime.now()` without timezone.

10. **progress_summary is always updated after an attempt** — call `update_progress_summary()` from `services/progress.py` after saving every attempt record. Do not skip this step.

---

## Testing

```bash
# Backend
cd backend
uv run pytest                         # all tests
uv run pytest tests/test_scoring.py  # scoring tests only
uv run pytest -v --cov=app           # with coverage

# Manual integration tests
uv run python scripts/test_r2.py      # R2 connection
uv run python scripts/test_scoring.py # DTW pipeline

# Get Firebase test token
uv run python scripts/get_test_token.py
```

---

## Known Limitations (V1)

| Limitation | Impact | V2 plan |
|---|---|---|
| DTW runs synchronously in the request thread | Scoring adds ~1–2s latency | Move to background task queue |
| No offline attempt queue | Students lose attempts if connectivity drops during submission | IndexedDB queue + background sync |
| Reference audio is TTS, not native speaker | ~5–10% lower phoneme accuracy benchmark | Replace with professional recordings in V2 |
| Instructor class assignment is manual SQL | Instructors must be assigned a class_id manually in DB | Add class management UI |
| No password reset UI | Students must contact instructor | Add Firebase password reset flow |

---

*SpeakSmart AGENT.md — Gordon College Tourism Department — Version 1.0*
*Last updated: April 2026*
