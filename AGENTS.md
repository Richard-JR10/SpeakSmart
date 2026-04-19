# Repository Guidelines

## Project Structure & Module Organization
`Frontend/` contains the Vue 3 + Vite PWA. Main app code lives in `Frontend/src`, with views under `views/student` and `views/instructor`, shared UI in `components`, shadcn primitives in `components/ui`, routing in `router`, API clients in `api`, and Pinia stores in `stores`.  
`Backend/` contains the FastAPI service. Core application code is in `Backend/app`, Alembic migrations are in `Backend/alembic`, and operational/test scripts live in `Backend/scripts`. Repository-level docs include `AGENT.md` and this guide.

## Build, Test, and Development Commands
Frontend:
- `cd Frontend && npm install --legacy-peer-deps` installs dependencies.
- `npm run dev` starts the Vite dev server.
- `npm run build` runs `vue-tsc` and creates a production build.
- `npm run preview` serves the built frontend locally.

Backend:
- `cd Backend && uv sync` installs Python dependencies.
- `uv run uvicorn app.main:app --reload` starts the API locally.
- `uv run alembic upgrade head` applies migrations.
- `docker-compose up -d` starts local PostgreSQL.

## Coding Style & Naming Conventions
Use TypeScript for frontend logic and typed Python on the backend. Follow existing Vue SFC structure with `<template>` then `<script setup lang="ts">`. Use 2-space indentation in Vue/TS/CSS and 4 spaces in Python. Prefer PascalCase for Vue views/components (`LoginView.vue`), camelCase for variables/functions, and kebab-case only for CSS utility composition or file names already using it. Reuse shadcn components in `@/components/ui` before adding custom UI.

## Testing Guidelines
Backend tests use `pytest`.
- `cd Backend && uv run pytest`
- `uv run pytest -v --cov=app`
- `uv run python scripts/test_scoring.py` for scoring checks

The frontend currently has no dedicated test runner configured, so treat `npm run build` as the minimum verification step for UI changes.

## Commit & Pull Request Guidelines
Recent history uses Conventional Commits, especially `feat:`. Follow that pattern, for example: `feat: remake signup page with shadcn components` or `fix: narrow button reset to avoid shadcn conflicts`.  
PRs should include:
- A short summary of user-facing changes
- Linked issue/task when applicable
- Screenshots or short recordings for frontend updates
- Notes about migrations, env vars, or manual verification steps

## Security & Configuration Tips
Never commit `.env` files, Firebase service credentials, or generated secrets. Use `uv run` for backend commands to stay inside the managed environment. Keep role checks server-side and avoid bypassing router/auth guards for convenience.
