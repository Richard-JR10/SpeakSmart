# SpeakSmart — Complete Project Documentation

> Japanese Pronunciation Analysis and Language Training System for Tourism Students
> Gordon College — Tourism Department | Olongapo City, Philippines

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Proposed Solution](#3-proposed-solution)
4. [SDG Alignment](#4-sdg-alignment)
5. [Features](#5-features)
6. [System Architecture](#6-system-architecture)
7. [Final Tech Stack](#7-final-tech-stack)
8. [Database Design — ERD & Data Dictionary](#8-database-design--erd--data-dictionary)
9. [SDLC Model — Agile Scrum](#9-sdlc-model--agile-scrum)
10. [Hardware Requirements](#10-hardware-requirements)
11. [Software Requirements](#11-software-requirements)
12. [Use Case Diagram](#12-use-case-diagram)
13. [Activity Diagrams](#13-activity-diagrams)
14. [UI/UX Wireframes](#14-uiux-wireframes)
15. [Reference Audio Strategy](#15-reference-audio-strategy)
16. [Speech Scoring Pipeline](#16-speech-scoring-pipeline)
17. [Backend Development Guide](#17-backend-development-guide)
18. [Implementation Roadmap](#18-implementation-roadmap)
19. [Risk Register](#19-risk-register)
20. [Glossary](#20-glossary)
21. [Cost Estimation](#21-cost-estimation)

---

## 1. Project Overview

| Field | Details |
|---|---|
| Project Title | SpeakSmart: A Pronunciation Analysis and Language Training System for Tourism Students |
| Client / Beneficiary | Gordon College — Tourism Department |
| Target Language | Japanese (primary); architecture is multi-language extensible |
| Target Users | Tourism students (practitioners) and instructors (administrators) |
| SDG Alignment | SDG 4: Quality Education · SDG 8: Decent Work and Economic Growth |
| Version | 1.0 — Initial Release |

SpeakSmart is a Progressive Web Application (PWA) and FastAPI backend system that enables tourism students at Gordon College to practice and improve their Japanese pronunciation through AI-driven speech comparison scoring. Instructors monitor student performance through a role-based analytics dashboard.

---

## 2. Problem Statement

Tourism students at Gordon College are required to learn Japanese to communicate effectively with Japanese tourists. However, several gaps exist in traditional classroom language instruction:

- Manual instructor feedback is not scalable. A single instructor cannot reliably evaluate pronunciation for an entire class in real time, leading to inconsistent assessment quality.
- Students lack independent practice tools with objective feedback. Existing mobile language apps are not tailored to tourism-domain vocabulary or Filipino learner profiles.
- Instructor visibility into student progress is limited. Without a centralized data system, identifying students who need additional support requires manual tracking.
- Low student confidence when speaking with foreign visitors. Without consistent practice and objective scoring, students are unable to self-assess improvement.

### Core phonological challenges for Filipino learners of Japanese

Japanese presents specific pronunciation challenges for Filipino L1 speakers:

| Challenge | Description |
|---|---|
| Mora timing | Japanese is mora-timed — each syllable unit must be held for a precise duration. Filipino speakers often rush through long vowels (e.g. おかあさん) which changes word meaning. |
| R-sound (ら り る れ ろ) | Does not exist in Filipino or English. One of the most common errors. |
| Double consonants | Words like きって require a full stop between consonants which Filipino speakers tend to skip. |
| Vowel purity | Japanese has only 5 pure vowels (a, i, u, e, o) that must be pronounced cleanly without diphthong drift. |

---

## 3. Proposed Solution

SpeakSmart is a PWA-based pronunciation analysis and language training system with two distinct user interfaces served from a single Vue 3 codebase:

### Student interface (mobile PWA)
Students record themselves speaking Japanese tourism phrases. The system analyzes pronunciation using speech comparison algorithms and returns a 0–100% accuracy score with phoneme-level feedback within 3 seconds.

### Instructor interface (web dashboard)
Instructors monitor class-wide performance through analytics dashboards — accuracy trends, phoneme error heatmaps, individual student drill-downs, and custom exercise assignment.

### Key differentiators
- Japanese-specific phoneme analysis — mora timing, R-sound accuracy, consonant scoring, vowel purity
- Real-time scoring via in-memory DTW algorithm — no audio stored unnecessarily
- Role-based access — students see only their own data; instructors see their entire class
- Audio playback — instructors can listen to student recordings for qualitative review

---

## 4. SDG Alignment

| SDG | Goal | How SpeakSmart contributes |
|---|---|---|
| SDG 4 — Quality Education | Ensure inclusive and equitable quality education | Provides objective, technology-assisted language assessment that raises the quality and consistency of pronunciation instruction for tourism students. |
| SDG 8 — Decent Work and Economic Growth | Promote sustained, inclusive and sustainable economic growth | Improves the employability and professional readiness of tourism graduates by verifiably developing Japanese communication skills valued by the hospitality industry. |

---

## 5. Features

### 5.1 Student PWA — 10 features

| # | Feature | Description |
|---|---|---|
| 1 | Pronunciation recording | Record voice practicing tourism-domain Japanese phrases |
| 2 | Reference audio playback | Hear a TTS native-quality reference before recording |
| 3 | Real-time pronunciation scoring | 0–100% accuracy score returned within 3 seconds |
| 4 | Phoneme-level feedback | Highlights exactly which syllable was wrong and why |
| 5 | Japanese-specific scoring | Mora timing, R-sound accuracy, vowel purity, consonant scoring |
| 6 | Lesson modules | Structured tourism vocabulary: greetings, hotel, directions, food, emergency, tour guide |
| 7 | Progress tracking | Personal accuracy trends, weekly bar chart, attempt history |
| 8 | Practice streak | Daily streak counter to encourage consistent practice |
| 9 | Installable PWA | Add to home screen — works like a native app on iOS and Android |
| 10 | Personal dashboard | Weekly accuracy average, phrases practiced, module completion |

### 5.2 Instructor web dashboard — 11 features

| # | Feature | Description |
|---|---|---|
| 1 | Class overview | Class-wide average accuracy, active student count, weekly attempts, flagged students |
| 2 | Accuracy trend chart | Week-by-week class performance over the term |
| 3 | Phoneme error breakdown | Class-wide error rates per phoneme type |
| 4 | Student table | Full class list with accuracy scores, module progress, attempt counts, weekly trend |
| 5 | Individual student drill-down | Full attempt history, phoneme breakdown, streak, weakest area |
| 6 | Phoneme error heatmap | Color-coded grid showing which sounds are most commonly mispronounced per module |
| 7 | Flagging system | Auto-surfaces students below a threshold accuracy |
| 8 | Audio playback | Instructors can listen to student recordings for qualitative review |
| 9 | Custom exercise authoring | Create targeted vocabulary sets and assign to specific students or groups |
| 10 | Exercise tracking | Monitor completion progress per assigned exercise |
| 11 | PDF report export | Downloadable performance reports for grading and academic records |

### 5.3 Backend system — 8 features

| # | Feature | Description |
|---|---|---|
| 1 | Speech feature extraction | Converts audio to MFCC, pitch contour, phoneme duration features using librosa |
| 2 | DTW speech comparison | Aligns student speech against reference audio regardless of speaking speed |
| 3 | Pronunciation scoring engine | Computes accuracy score with per-phoneme error localization |
| 4 | Mora timing analysis | Specialized duration ratio checker for Japanese long vowels and double consonants |
| 5 | Role-based access control | Students see only their own data; instructors see their assigned class |
| 6 | Audio quality validation | Checks file type, size, and minimum duration before scoring |
| 7 | Reference audio generation | Google TTS generates native-quality Japanese reference audio automatically |
| 8 | Multi-language ready | Language-specific analysis modules can be added for future languages |

---

## 6. System Architecture

### 6.1 High-level architecture

```
┌──────────────────────────────────────────────────────────┐
│               Vue 3 + Vite PWA                            │
│                                                          │
│   Student views ←── Role-based routing ──→ Instructor views │
│                                                          │
│   MediaRecorder API (audio capture)                      │
│   Service Worker (offline + installable)                 │
│   Firebase Auth SDK (login only)                         │
│   Axios (all API calls → FastAPI)                        │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTPS / REST
                       ▼
        ┌──────────────────────────────────────┐
        │           FastAPI Backend             │
        │                                      │
        │  Firebase Auth token verification    │
        │  SQLAlchemy 2.0 async ORM            │
        │  In-memory audio scoring (librosa)   │
        │  Cloudflare R2 audio storage         │
        │  Alembic database migrations         │
        └──────────┬───────────────┬───────────┘
                   │               │
        ┌──────────▼────┐   ┌──────▼──────────────┐
        │  PostgreSQL   │   │  Cloudflare R2       │
        │               │   │                      │
        │  All app data │   │  Student audio       │
        │               │   │  Reference audio     │
        └───────────────┘   └─────────────────────┘
                   │
        ┌──────────▼────┐
        │  Firebase Auth │
        │  (login only) │
        └───────────────┘
```

### 6.2 Responsibility split

| Action | Handled by |
|---|---|
| Login / logout / get JWT token | Firebase Auth SDK (frontend) |
| All data requests | FastAPI via Axios |
| Audio submission and scoring | FastAPI |
| Audio file storage and retrieval | Cloudflare R2 via FastAPI |
| Role enforcement | FastAPI dependencies |
| Database reads and writes | FastAPI + SQLAlchemy + PostgreSQL |

### 6.3 Audio processing flow

```
Student records audio (PWA)
        │
        ▼
FastAPI receives multipart upload
        │
        ├── 1. Validate audio file (type, size)
        ├── 2. Read student audio → RAM (bytes)
        ├── 3. Fetch reference audio URL from PostgreSQL
        ├── 4. Download reference audio from R2 → RAM
        ├── 5. Extract MFCC features (librosa) — both in memory
        ├── 6. Run DTW alignment
        ├── 7. Score mora timing, consonants, vowels
        ├── 8. Compute weighted overall score (0–100%)
        ├── 9. Generate feedback text
        ├── 10. Upload student audio to Cloudflare R2
        ├── 11. Save scores + audio URL to PostgreSQL
        └── 12. Return JSON to PWA (score + feedback)
```

---

## 7. Final Tech Stack

> This stack is locked. No further changes.

| Layer | Technology | Notes |
|---|---|---|
| Frontend | Vue 3 + Vite + TypeScript (PWA) | Single codebase for students and instructors |
| State management | Pinia | Industry standard for Vue 3 |
| HTTP client | Axios | All calls to FastAPI |
| PWA framework | vite-plugin-pwa | Service worker, manifest, installable |
| Authentication (frontend) | Firebase Auth SDK | Login only — Email + Google sign-in |
| Backend API | Python FastAPI | Async, production-grade |
| ORM | SQLAlchemy 2.0 async | Industry standard for FastAPI |
| Migrations | Alembic | Database versioning |
| Authentication (backend) | Firebase Admin SDK | JWT token verification only |
| Audio processing | librosa + DTW | In-memory, no temp files |
| Reference audio | Google TTS → Cloudflare R2 | Generated once during seeding |
| Audio storage | Cloudflare R2 | S3-compatible, zero egress fees |
| Database | PostgreSQL | Docker locally, Cloud SQL deployed |
| Package manager (backend) | uv | Faster than pip, pyproject.toml based |
| Backend hosting | Google Cloud Run | Scales to zero, covered by $300 credit |
| Frontend hosting | Cloudflare Pages | Free forever, deploys from Git |
| Database hosting | Cloud SQL (PostgreSQL) | ~$7–10/month |

### 7.1 Why this combination

**Firebase Auth** — handles JWT issuance, Google sign-in, and password reset for free. Zero infrastructure to maintain for authentication.

**PostgreSQL over Firestore** — full SQL means complex instructor dashboard queries (class averages, student rankings, phoneme error rates) are simple. Runs fully offline with Docker during development. No Firebase credentials needed for local development.

**Cloudflare R2 over Firebase Storage** — zero egress fees. Student recordings and reference audio downloads are free regardless of volume. Free tier covers 10GB storage and 1M requests per month — more than enough for a 32–100 student pilot.

**Vue 3 PWA over Flutter** — single codebase for both student mobile interface and instructor web dashboard. No app store submission. Audio recording via browser `MediaRecorder` API works on iOS 14.3+ and Android 8+. Students install via "Add to Home Screen."

**uv over pip** — significantly faster dependency resolution and installation. Uses `pyproject.toml` standard. `uv.lock` ensures reproducible builds across team members.

---

## 8. Database Design — ERD & Data Dictionary

### 8.1 PostgreSQL tables

| Table | Primary purpose |
|---|---|
| `users` | All system users — students and instructors distinguished by `role` field |
| `classes` | Course sections taught by an instructor |
| `modules` | Lesson modules organized by tourism topic |
| `phrases` | Individual Japanese phrases with reference audio URL |
| `attempts` | Every pronunciation recording result with scores and feedback |
| `progress_summary` | Pre-aggregated rolling averages per student per module |
| `exercises` | Custom drill sets created by instructors |
| `exercise_phrases` | Junction table — links exercises to phrases |
| `exercise_assignments` | Which students are assigned which exercises |
| `class_analytics` | Weekly pre-computed class-wide statistics |

### 8.2 Data dictionary — key fields

#### users
| Field | Type | Constraint | Description |
|---|---|---|---|
| uid | string | PK | Firebase UID — primary key across all tables |
| email | string | | Registered email address |
| display_name | string | | Full name shown in app and dashboard |
| role | string | | `student` or `instructor` |
| class_id | string | FK | References classes table. Null for instructors |
| created_at | timestamp | | UTC account creation time |
| last_login | timestamp | | UTC last login — used to detect inactive students |

#### phrases
| Field | Type | Constraint | Description |
|---|---|---|---|
| phrase_id | string | PK | Auto-generated unique identifier |
| module_id | string | FK | References modules table |
| japanese_text | string | | Japanese script (kanji/hiragana/katakana) |
| romaji | string | | Hepburn romanization |
| english_translation | string | | English meaning |
| reference_audio_url | string | | Cloudflare R2 URL to TTS-generated WAV |
| difficulty_level | integer | | 1 (easy) to 5 (hard) |

#### attempts
| Field | Type | Constraint | Description |
|---|---|---|---|
| attempt_id | string | PK | Auto-generated unique identifier |
| student_uid | string | FK | References users table |
| phrase_id | string | FK | References phrases table |
| audio_file_url | string | | Cloudflare R2 URL to student recording |
| accuracy_score | float | 0–100 | Overall weighted pronunciation accuracy |
| mora_timing_score | float | 0–100 | Long vowel and double consonant duration accuracy |
| consonant_score | float | 0–100 | Consonant accuracy — emphasis on R-sound |
| vowel_score | float | 0–100 | Vowel purity without diphthong drift |
| phoneme_error_map | json | | Per-phoneme error flags |
| feedback_text | string | | Human-readable feedback message |
| attempted_at | timestamp | | UTC submission time |

### 8.3 Cloudflare R2 bucket structure

```
speaksmart-audio/
├── reference-audio/
│   ├── module_greetings/
│   │   ├── ph_greet_001.wav
│   │   └── ph_greet_002.wav
│   ├── module_hotel/
│   │   └── ph_hotel_001.wav
│   └── ...
└── student-audio/
    └── {student_uid}/
        └── {attempt_id}.wav
```

---

## 9. SDLC Model — Agile Scrum

SpeakSmart is developed using **Agile Scrum** because the project involves technically uncertain components — the speech comparison algorithm and Japanese phoneme analysis engine — that cannot be fully designed upfront and must be validated through real student testing. Agile Scrum organizes development into short iterative cycles called Sprints, allowing the team to build, test, and refine each feature incrementally while continuously gathering feedback from Gordon College instructors and students after every cycle. This ensures that issues such as inaccurate pronunciation scoring or unclear student feedback messages are caught and corrected early rather than discovered at the end of the project, making it the most practical and responsive approach for a system of this complexity.

### Scrum roles

| Role | Responsibility |
|---|---|
| Product Owner | Prioritizes features delivering most value to Gordon College |
| Scrum Master | Facilitates the process and removes blockers |
| Development Team | Designs, builds, and tests the system |

---

## 10. Hardware Requirements

### Server-side (Google Cloud Run)

| Component | Specification |
|---|---|
| API server (Cloud Run) | 2 vCPU, 4GB RAM per container instance |
| Minimum always-on instances | 1 instance during academic hours (6AM–10PM) |
| Estimated monthly cost | $5–15 USD for 50–100 students |
| Database (Cloud SQL) | 1 vCPU, 3.75GB RAM — db-f1-micro instance |
| ML audio processing job | Not needed for V1 — DTW runs in API container |

### Client-side — Student devices (Mobile)

| Component | Minimum Specification |
|---|---|
| Processor | Any modern smartphone (2018 or newer) |
| RAM | 2GB |
| Operating system | iOS 14.3+ or Android 8.0 (API 26)+ |
| Browser | Chrome 90+, Safari 14+, Firefox 88+ |
| Storage | 100MB free (PWA cache) |
| Microphone | Built-in, 16kHz sampling rate minimum |
| Connectivity | Internet required (no offline audio submission) |

### Client-side — Instructor devices (Web)

| Component | Minimum Specification |
|---|---|
| Processor | Intel Core i3 or equivalent (2016 or newer) |
| RAM | 4GB |
| Browser | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| Internet connection | 5 Mbps minimum (stable) |

### Audio input quality note

| Setting | Recommendation |
|---|---|
| Casual / home practice | Built-in phone microphone (acceptable) |
| Classroom / lab sessions | Basic earphone-microphone set (≈ ₱200/unit) |
| Impact of poor microphone | Up to 10–15% reduction in scoring accuracy in noisy environments |

---

## 11. Software Requirements

### 11.1 Backend dependencies

```
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
alembic
python-multipart
firebase-admin
boto3
google-cloud-texttospeech
librosa
scipy
numpy
pydantic-settings
python-dotenv
python-jose[cryptography]
passlib[bcrypt]
httpx
```

Dev dependencies:
```
pytest
pytest-asyncio
pytest-cov
httpx
```

### 11.2 Frontend dependencies

```
vue
vite
typescript
pinia
vue-router
axios
firebase
vite-plugin-pwa
```

### 11.3 Tools and services

| Tool | Purpose |
|---|---|
| Docker Desktop | Local PostgreSQL via docker-compose |
| uv | Python package manager |
| Node.js 18+ | Frontend build toolchain |
| Google Cloud SDK | Cloud Run + Cloud SQL deployment |
| Cloudflare account | R2 storage + Pages hosting |
| Firebase project | Auth only |

---

## 12. Use Case Diagram

### Actors

| Actor | Description |
|---|---|
| Student | Tourism student using the PWA on mobile to practice Japanese pronunciation |
| Instructor | Tourism department teacher using the web dashboard to monitor performance |
| System | Automated backend process — scoring pipeline, progress updates |

### Student use cases

| Use Case | Description |
|---|---|
| Record pronunciation | Student records themselves speaking a Japanese phrase |
| Play reference audio | Hear native-quality TTS reference before recording |
| View score and feedback | See accuracy score and phoneme-level feedback after submission |
| Browse lesson modules | Navigate tourism-domain Japanese modules |
| View personal progress | Track accuracy trends, streaks, and attempt history |
| Sync offline recordings | Reconnect and sync queued attempts (future feature) |

### Instructor use cases

| Use Case | Description |
|---|---|
| View class analytics | Class-wide accuracy trends and phoneme error rates |
| Monitor student progress | Individual student drill-down with attempt history |
| View error heatmap | Color-coded phoneme × module error frequency grid |
| Assign custom exercises | Create targeted drill sets and assign to students |
| Export PDF report | Generate downloadable performance reports |

### System (automated) use cases

| Use Case | Triggered by |
|---|---|
| Analyze and score speech | Every student audio submission |
| Update progress summary | After each scored attempt |
| Compute class analytics | Weekly batch job |

### Key relationships

- Record pronunciation **`<<include>>`** Analyze and score speech
- View score and feedback **`<<include>>`** Analyze and score speech
- View class analytics **`<<include>>`** Analyze and score speech

---

## 13. Activity Diagrams

### 13.1 Student practice flow

**Swimlanes:** Student | Mobile PWA | Backend / Firebase

1. Student opens SpeakSmart PWA
2. Browses lesson modules
3. **Decision:** Module unlocked? → No: show locked message | Yes: continue
4. Selects a phrase
5. Plays reference audio (fetches from Cloudflare R2)
6. Taps record and speaks
7. **Decision:** Audio quality acceptable? → No: show retry prompt | Yes: continue
8. Uploads audio to FastAPI backend
9. Backend scores and saves to PostgreSQL
10. Returns score and feedback to PWA
11. PWA displays results
12. **Decision:** Try again or next phrase? → Retry: back to step 6 | Next: update progress summary

### 13.2 Speech scoring pipeline

**Swimlanes:** FastAPI Backend | AI/ML Engine | PostgreSQL + R2

1. Receive audio upload (multipart)
2. **Decision:** JWT token valid? → No: return 401 | Yes: continue
3. Fetch phrase + reference audio URL from PostgreSQL
4. Download reference audio from R2 → RAM
5. Send both audio arrays to ML Engine
6. Extract MFCC features (librosa)
7. Run DTW alignment
8. Analyze mora timing
9. Score consonants and vowels
10. Compute final 0–100% score
11. Generate feedback text
12. Upload student audio to R2
13. Save attempt record to PostgreSQL
14. Return JSON response to PWA

### 13.3 Instructor monitoring flow

**Swimlanes:** Instructor | Web Dashboard | FastAPI + PostgreSQL

1. Instructor opens web dashboard
2. FastAPI validates JWT and fetches class data
3. View class overview (stats, trend chart, error categories)
4. **Decision:** Instructor action? → Drill down: select student, view attempts | Heatmap: query analytics
5. **Decision:** Students below 60%? → Yes: flag on dashboard | No: continue
6. Export PDF report

### 13.4 Exercise assignment flow

**Swimlanes:** Instructor | Web Dashboard | Student PWA

1. Instructor navigates to Exercises tab
2. Clicks New Exercise
3. Enters title, selects phrases, selects students, sets due date
4. **Decision:** Confirm assignment? → No: return to form | Yes: save
5. Exercise appears in student's PWA
6. Student completes and syncs
7. Dashboard tracks completion progress

### 13.5 User login and authentication flow

**Swimlanes:** User | Firebase Auth | App / Dashboard

1. User enters email and password
2. **Decision:** Credentials valid? → No: show error | Yes: issue JWT token
3. **Decision:** User role? → Student: open student PWA views | Instructor: open instructor dashboard views
4. Session active — proceed

---

## 14. UI/UX Wireframes

### 14.1 Student PWA — 8 screens

| Screen | Key components |
|---|---|
| M1 Onboarding | App logo, tagline, Get started button, Sign in button, Gordon College branding |
| M2 Login | Email and password fields, Forgot password link, Sign in button, Google sign-in |
| M3 Home | Greeting, 7-day streak card, accuracy and phrases stats, continue card, recent scores, Start practice CTA, bottom nav |
| M4 Lessons | Module list with status icons (completed/active/locked), progress bars, scores |
| M5 Practice | Phrase card (kanji + romaji + English), Hear reference button, waveform visualizer, record button, phoneme chips (green/red), See results button |
| M6 Results | Score circle (0–100%), Needs practice badge, phoneme breakdown chips, feedback bullet points, Try again / Next phrase buttons |
| M7 Progress | Weekly bar chart, avg accuracy + delta stats, weak area alert card, recent attempts list |
| M8 Settings | User avatar, daily reminder toggle, auto-play toggle, offline mode toggle, language target, sign out |

### 14.2 Instructor web dashboard — 5 screens

| Screen | Key components |
|---|---|
| W1 Overview | 4 stat cards, weekly accuracy trend chart, phoneme error category chart, flagged students table |
| W2 Students | Full class table with accuracy pills and progress bars, student drill-down panel with tone breakdown and attempt history |
| W3 Heatmap | Phoneme × module color grid (teal=low error, red=high error), top errors summary |
| W4 Exercises | Exercise assignment table with completion bars, new exercise form (title, phrases, students, due date) |
| W5 Settings | Account profile, class settings (real-time sync toggle, email alerts), flagging threshold |

### 14.3 AI prompt for UI generation (Student PWA)

Use the following prompt in Galileo AI, v0.dev, or Uizard:

> Design a modern, clean mobile app UI for a Japanese pronunciation training app called "SpeakSmart" for Filipino tourism students at Gordon College. Primary color: Teal green (#1D9E75). Platform: iOS and Android PWA. Style: Clean, minimal, flat design with white backgrounds and 12px rounded corners. Design 8 screens: Onboarding, Login, Home (streak card + stats), Lessons (module list with status icons), Practice (phrase card + waveform + record button + phoneme chips), Results (score circle + feedback), Progress (bar chart + weak area alert), Settings (toggles + sign out). Typography: SF Pro Display for headings. Output as flat canvas with all 8 phone frames side by side.

### 14.4 AI prompt for UI generation (Instructor Dashboard)

> Design a professional data-rich instructor analytics web dashboard for "SpeakSmart" at 1440px width. Primary color: Teal (#1D9E75) for active states. Style: Clean SaaS dashboard, flat white cards, minimal borders, no shadows. Left sidebar (180px) with logo and navigation. Design 5 screens: Class Overview (4 stat cards + trend chart + flagged students table), Students (class table + drill-down), Error Heatmap (phoneme × module color grid), Exercises (assignment table + new exercise form), Settings (account + class config). Output as 5 stacked full-width browser frames.

---

## 15. Reference Audio Strategy

### How reference audio is generated

Reference audio is generated once using **Google Cloud Text-to-Speech** with the `ja-JP-Wavenet-B` neural voice (natural female, slightly slower speaking rate for learners). Generated WAV files are stored in Cloudflare R2 under `reference-audio/{module_id}/{phrase_id}.wav`.

### Why TTS is the right choice

- Google Wavenet Japanese TTS produces accurate mora timing, correct vowel pronunciation, and proper consonant articulation
- For students learning Japanese from scratch, these voices are accurate enough to train against
- The DTW scoring pipeline compares acoustic features regardless of whether audio comes from TTS or a human recording
- The entire phrase library (~500 Japanese characters) fits well within Google TTS's 1 million character free tier monthly — zero cost
- Audio can be regenerated instantly if phrase text is updated

### Speaking rate configuration

```python
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,    # Matches librosa scoring pipeline
    speaking_rate=0.85,         # Slightly slower — better for learners
    pitch=0.0,
)
```

### Upgrade path

For V2, TTS reference audio can be replaced with professional native speaker recordings without any changes to the scoring architecture — simply upload new WAV files to the same R2 paths.

---

## 16. Speech Scoring Pipeline

### 16.1 Feature extraction (librosa)

| Feature | Description | Use in scoring |
|---|---|---|
| MFCC (13 coefficients) | Mel-Frequency Cepstral Coefficients — compact power spectrum representation | Primary phoneme comparison input for DTW |
| F0 (fundamental frequency) | Pitch contour over time | Not used for Japanese (non-tonal) — reserved for future tonal languages |
| Duration | Total audio length | Mora timing score |

### 16.2 DTW algorithm

Dynamic Time Warping computes the minimum-cost alignment between the student's MFCC sequence and the reference MFCC sequence. It accommodates natural variation in speaking rate — a student speaking slightly faster or slower is not penalized for tempo difference, only for phoneme accuracy.

### 16.3 Scoring weights

| Component | Weight | What it measures |
|---|---|---|
| DTW distance | 10% | Overall acoustic similarity to reference |
| Mora timing | 35% | Long vowel duration accuracy (key Filipino learner error) |
| Consonant accuracy | 35% | Upper MFCC bands — R-sound and consonant clarity |
| Vowel purity | 20% | Lower MFCC bands — clean 5-vowel system |

### 16.4 Score interpretation

| Range | Label | Feedback approach |
|---|---|---|
| 85–100% | Excellent | Positive reinforcement, encourage consistency |
| 70–84% | Good | Minor specific tips |
| 55–69% | Needs practice | Targeted error explanation |
| 0–54% | Needs significant work | Specific phoneme errors with correction tips |

### 16.5 Feedback generation examples

| Error detected | Feedback message |
|---|---|
| Mora timing below 70% | "Long vowels need more duration — hold each vowel for a full mora beat." |
| Consonant score below 70% | "The R-sound needs work — curl the tongue slightly and let it flap lightly." |
| Vowel score below 70% | "Keep Japanese vowels pure — avoid the diphthong drift common in Filipino speech." |
| All scores above 70% | "Great pronunciation! Keep practicing to improve consistency." |

---

## 17. Backend Development Guide

### 17.1 Final project structure

```
speaksmart-backend/
├── app/
│   ├── main.py                    ← FastAPI entry point + lifespan
│   ├── config.py                  ← Pydantic Settings from .env
│   ├── api/
│   │   └── v1/
│   │       ├── router.py          ← Aggregates all endpoint routers
│   │       └── endpoints/
│   │           ├── auth.py        ← /auth/me, /auth/verify
│   │           ├── users.py       ← User profile management
│   │           ├── modules.py     ← Lesson module CRUD
│   │           ├── phrases.py     ← Phrase retrieval
│   │           ├── attempts.py    ← Audio upload + scoring (core endpoint)
│   │           ├── progress.py    ← Student progress summaries
│   │           ├── exercises.py   ← Exercise creation and assignment
│   │           └── analytics.py   ← Class-wide analytics
│   ├── core/
│   │   ├── security.py            ← Firebase JWT verification
│   │   ├── dependencies.py        ← get_current_user, require_instructor
│   │   └── exceptions.py          ← Custom exception classes
│   ├── db/
│   │   ├── base.py                ← SQLAlchemy async engine + Base
│   │   ├── session.py             ← Async session factory + get_db
│   │   └── models/                ← SQLAlchemy ORM models
│   │       ├── user.py
│   │       ├── class_.py
│   │       ├── module.py
│   │       ├── phrase.py
│   │       ├── attempt.py
│   │       ├── progress.py
│   │       ├── exercise.py
│   │       └── analytics.py
│   ├── schemas/                   ← Pydantic request/response models
│   │   ├── user.py
│   │   ├── attempt.py
│   │   ├── phrase.py
│   │   ├── module.py
│   │   ├── exercise.py
│   │   ├── progress.py
│   │   └── analytics.py
│   └── services/
│       ├── firebase_auth.py       ← Firebase Admin SDK (auth only)
│       ├── r2_storage.py          ← Cloudflare R2 via boto3
│       ├── speech.py              ← librosa feature extraction
│       ├── scoring.py             ← DTW scoring pipeline
│       └── tts.py                 ← Google TTS reference audio generation
├── alembic/
│   ├── env.py                     ← Async Alembic configuration
│   └── versions/                  ← Migration files (auto-generated)
├── scripts/
│   └── seed_phrases.py            ← Generate TTS + seed DB + upload to R2
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_attempts.py
│   └── test_scoring.py
├── .env                           ← Never commit
├── .env.example                   ← Commit this
├── .gitignore
├── docker-compose.yml             ← Local PostgreSQL
├── Dockerfile
├── pyproject.toml                 ← uv dependencies
└── uv.lock                        ← Locked dependency versions
```

### 17.2 Environment variables

```env
# App
APP_ENV=development
SECRET_KEY=change-this-to-a-long-random-string

# Database
DATABASE_URL=postgresql+asyncpg://speaksmart:speaksmart_secret@localhost:5432/speaksmart

# Firebase (Auth only)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id

# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=speaksmart-audio
R2_PUBLIC_URL=https://your-bucket.your-account.r2.dev

# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS=serviceAccountKey.json

# Audio limits
MAX_AUDIO_SIZE_MB=10
```

### 17.3 Local development setup

```bash
# 1. Clone and enter project
git clone https://github.com/your-org/speaksmart-backend
cd speaksmart-backend

# 2. Install dependencies with uv
uv sync

# 3. Copy and fill environment variables
cp .env.example .env

# 4. Start local PostgreSQL
docker-compose up -d

# 5. Run database migrations
uv run alembic upgrade head

# 6. Seed phrases (generates TTS + uploads to R2 + seeds DB)
uv run python scripts/seed_phrases.py

# 7. Start the API
uv run uvicorn app.main:app --reload
```

### 17.4 uv cheat sheet

| Task | Command |
|---|---|
| Add a package | `uv add package-name` |
| Add a dev package | `uv add --dev package-name` |
| Remove a package | `uv remove package-name` |
| Run a command | `uv run command` |
| Sync all dependencies | `uv sync` |
| Show installed packages | `uv pip list` |
| Run tests | `uv run pytest` |
| Run migrations | `uv run alembic upgrade head` |

### 17.5 API endpoints reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Health check |
| GET | `/api/v1/auth/me` | Any | Current user profile from JWT |
| GET | `/api/v1/auth/verify` | Any | Verify token validity |
| GET | `/api/v1/modules` | Student | List all lesson modules |
| GET | `/api/v1/modules/{id}/phrases` | Student | Get phrases for a module |
| GET | `/api/v1/phrases/{id}` | Student | Get a single phrase |
| POST | `/api/v1/attempts` | Student | Submit audio for scoring |
| GET | `/api/v1/attempts/{uid}` | Student/Instructor | Get attempt history |
| GET | `/api/v1/progress/{uid}` | Student/Instructor | Get progress summary |
| GET | `/api/v1/analytics/class/{id}` | Instructor | Class-wide analytics |
| GET | `/api/v1/analytics/students/{id}` | Instructor | All students with stats |
| POST | `/api/v1/exercises` | Instructor | Create exercise |
| POST | `/api/v1/exercises/{id}/assign` | Instructor | Assign exercise to students |
| GET | `/api/v1/exercises/{uid}` | Student | Get assigned exercises |

### 17.6 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for librosa
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 18. Implementation Roadmap

### 18.1 Backend build steps

| Step | Deliverable | Estimated duration |
|---|---|---|
| Step 1 | Project scaffold + Docker + PostgreSQL + Alembic setup + uv | 1 day |
| Step 2 | SQLAlchemy ORM models + first Alembic migration | 1–2 days |
| Step 3 | Firebase Auth service + JWT dependencies + auth endpoints | 1 day |
| Step 4 | Cloudflare R2 storage service (upload/download) | 1 day |
| Step 5 | Modules + Phrases endpoints | 1–2 days |
| Step 6 | Google TTS seeder script | 1 day |
| Step 7 | Speech processing + DTW scoring pipeline | 2–3 days |
| Step 8 | Attempts endpoint — full audio upload and scoring flow | 2 days |
| Step 9 | Progress endpoints | 1 day |
| Step 10 | Analytics endpoints | 2 days |
| Step 11 | Exercises endpoints | 1–2 days |
| Step 12 | Dockerfile + Cloud Run deployment | 1 day |

### 18.2 Development phases (Agile Scrum)

| Phase | Sprint deliverables | Duration |
|---|---|---|
| Phase 1 — Foundation | Project scaffold, DB models, Firebase Auth, basic API running | 2 weeks |
| Phase 2 — Audio Pipeline | TTS seeder, librosa feature extraction, DTW prototype, scoring pipeline | 4 weeks |
| Phase 3 — Scoring & Feedback | Full scoring endpoint, feedback generation, score storage | 3 weeks |
| Phase 4 — Student PWA | Full lesson module UI, practice screen, real-time score display, progress screen | 3 weeks |
| Phase 5 — Instructor Dashboard | Class analytics, student drill-down, heatmap, PDF export, exercise authoring | 3 weeks |
| Phase 6 — Testing & UAT | Unit testing, integration testing, UAT with Gordon College | 2 weeks |
| Phase 7 — Deployment | Cloud Run + Cloud SQL + Cloudflare Pages deployment, documentation, handover | 2 weeks |

Total estimated duration: **19 weeks (~5 months)**

---

## 19. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Speech scoring accuracy insufficient for Japanese phonemes | Medium | High | Prototype DTW scoring in Phase 2; benchmark against Azure Pronunciation Assessment API as fallback |
| Inconsistent audio quality from student devices | High | Medium | Audio quality validation (noise floor, SNR check) before scoring; in-app guidance on recording best practices |
| PWA audio recording not supported on target iOS version | Low | High | Verify on iOS 14.3+ early in Phase 4; fallback to guided WAV file upload if MediaRecorder fails |
| PostgreSQL Cloud SQL cost exceeds budget | Low | Medium | Monitor via Google Cloud billing alerts; scale down instance if needed |
| Firebase Auth token verification latency | Low | Low | Cache verified tokens briefly; Firebase verifies locally using cached public keys |
| Limited labeled Japanese training data for Filipino speakers | Medium | High | Use Google TTS as reference for V1; collect student recordings in Phase 6 for future model training |
| Student adoption and consistent usage | Medium | Medium | Gamification (streaks, progress badges); instructor-assigned exercises create structured usage |
| Data Privacy Act (RA 10173) compliance gaps | Low | High | Include explicit consent in onboarding; limit audio storage to consenting users; implement data deletion |

---

## 20. Glossary

| Term | Definition |
|---|---|
| DTW (Dynamic Time Warping) | A sequence alignment algorithm that computes the minimum distance between two time-series of different lengths, used to compare student and reference speech at varying speaking speeds. |
| MFCC (Mel-Frequency Cepstral Coefficients) | A compact representation of the short-term power spectrum of speech, widely used as the primary feature for pronunciation and speech recognition tasks. |
| Mora | The smallest unit of sound in Japanese phonology. Japanese is mora-timed — each mora takes approximately equal duration to pronounce. Long vowels count as two morae. |
| Mora timing | The accuracy with which a student holds long vowels and double consonant pauses for the correct duration. One of the most common errors for Filipino learners. |
| Phoneme | The smallest unit of sound in a language that distinguishes meaning. Japanese phonology has approximately 100 distinct morae combinations. |
| F0 (Fundamental Frequency) | The lowest frequency component of a speech signal, perceived as pitch. Used for tonal language analysis (Mandarin) but less critical for Japanese. |
| DTW distance | A numerical value representing how acoustically different a student's pronunciation is from the reference. Lower = more similar. |
| L1 transfer | The influence of a speaker's first language (Filipino) on their pronunciation of a second language (Japanese). |
| librosa | An open-source Python library for audio analysis, including MFCC extraction, pitch tracking, and spectrogram computation. |
| FastAPI | A modern, high-performance Python web framework for building REST APIs with automatic OpenAPI documentation generation. |
| SQLAlchemy | Python's standard ORM (Object-Relational Mapper) for interacting with SQL databases using Python class definitions. |
| Alembic | Database migration tool for SQLAlchemy. Tracks schema changes and applies them to the database incrementally. |
| uv | A fast Python package manager written in Rust. Replaces pip + virtualenv with a single tool. |
| PWA (Progressive Web App) | A web application that uses modern browser APIs to behave like a native app — installable, offline-capable, and accessible via URL. |
| Cloudflare R2 | Cloudflare's S3-compatible object storage service with zero egress fees. Used to store student and reference audio files. |
| Firebase Auth | Google's authentication service that handles user identity, JWT issuance, and social login. Used by SpeakSmart for authentication only. |
| JWT (JSON Web Token) | A compact, digitally signed token used to securely transmit authentication claims between client and server. |
| MediaRecorder API | A browser API that allows recording audio from the device microphone. The core mechanism for capturing student pronunciation in the PWA. |
| TTS (Text-to-Speech) | Automated conversion of text to spoken audio. Used to generate Japanese reference audio via Google Cloud TTS. |
| Agile Scrum | An iterative software development framework organizing work into fixed-length Sprints, with continuous feedback and adaptation. |

---

## 21. Cost Estimation

### Monthly cost breakdown

| Service | Monthly cost | Notes |
|---|---|---|
| Google Cloud Run (FastAPI) | ~$5–15 | Scales to zero when unused |
| Google Cloud SQL (PostgreSQL) | ~$7–10 | db-f1-micro, smallest instance |
| Firebase Auth | $0 | Free forever |
| Cloudflare R2 (audio storage) | $0 | Free tier: 10GB, 1M requests/month |
| Cloudflare Pages (Vue PWA) | $0 | Free forever |
| Google TTS (reference audio) | $0 | One-time generation, free tier |
| Total | ~$12–25/month | |

### Budget analysis with $300 Google credit

| Scenario | Monthly spend | Credit duration |
|---|---|---|
| Minimum (Cloud Run scales to zero mostly) | ~$12 | 25 months |
| Average (normal academic usage) | ~$20 | 15 months |
| Maximum (Cloud Run always warm) | ~$25 | 12 months |

The $300 Google credit covers Cloud Run and Cloud SQL for a full development period (6 months) plus a complete academic semester deployment (4 months) — approximately 10 months total with comfortable headroom.

### Storage estimate for 50–100 students

| Factor | Value |
|---|---|
| Average student recording size | ~70KB (WAV, 16kHz, 3–5 seconds) |
| Attempts per student per day | 20 |
| Students | 100 |
| Semester duration | 16 weeks × 5 days |
| Total audio per semester | 100 × 20 × 80 days × 70KB ≈ 11GB |
| R2 storage cost at $0.015/GB | ~$0.17/month |
| R2 egress cost | $0 (free egress) |

Audio storage costs are effectively zero for the entire pilot semester.

---

*SpeakSmart Project Documentation — Gordon College Tourism Department — Version 1.0*
*Generated from project planning and development sessions — April 2026*
