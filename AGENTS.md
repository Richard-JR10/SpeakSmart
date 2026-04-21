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

## Frontend tasks

When doing frontend design tasks, avoid generic, overbuilt layouts.

**Use these hard rules:**
- One composition: The first viewport must read as one composition, not a dashboard (unless it's a dashboard).
- Brand first: On branded pages, the brand or product name must be a hero-level signal, not just nav text or an eyebrow. No headline should overpower the brand.
- Brand test: If the first viewport could belong to another brand after removing the nav, the branding is too weak.
- Typography: Use expressive, purposeful fonts and avoid default stacks (Inter, Roboto, Arial, system).
- Background: Don't rely on flat, single-color backgrounds; use gradients, images, or subtle patterns to build atmosphere.
- Full-bleed hero only: On landing pages and promotional surfaces, the hero image should be a dominant edge-to-edge visual plane or background by default. Do not use inset hero images, side-panel hero images, rounded media cards, tiled collages, or floating image blocks unless the existing design system clearly requires it.
- Hero budget: The first viewport should usually contain only the brand, one headline, one short supporting sentence, one CTA group, and one dominant image. Do not place stats, schedules, event listings, address blocks, promos, "this week" callouts, metadata rows, or secondary marketing content in the first viewport.
- No hero overlays: Do not place detached labels, floating badges, promo stickers, info chips, or callout boxes on top of hero media.
- Cards: Default: no cards. Never use cards in the hero. Cards are allowed only when they are the container for a user interaction. If removing a border, shadow, background, or radius does not hurt interaction or understanding, it should not be a card.
- One job per section: Each section should have one purpose, one headline, and usually one short supporting sentence.
- Real visual anchor: Imagery should show the product, place, atmosphere, or context. Decorative gradients and abstract backgrounds do not count as the main visual idea.
- Reduce clutter: Avoid pill clusters, stat strips, icon rows, boxed promos, schedule snippets, and multiple competing text blocks.
- Use motion to create presence and hierarchy, not noise. Ship at least 2-3 intentional motions for visually led work.
- Color & Look: Choose a clear visual direction; define CSS variables; avoid purple-on-white defaults. No purple bias or dark mode bias.
- Ensure the page loads properly on both desktop and mobile.
- For React code, prefer modern patterns including useEffectEvent, startTransition, and useDeferredValue when appropriate if used by the team. Do not add useMemo/useCallback by default unless already used; follow the repo's React Compiler guidance.

Exception: If working within an existing website or design system, preserve the established patterns, structure, and visual language.

## Tailwind CSS
Always prioritize standard Tailwind utility classes over arbitrary values (e.g., use rounded-3xl instead of rounded-[24px]). When arbitrary values are necessary (such as specific RGB colors with opacity), omit all spaces around the forward slash (e.g., use [rgb(0_0_0/0.5)] instead of [rgb(0_0_0_/_0.5)]).

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

## AI Assistant Skills & Instructions

When assisting in this repository, please adhere to the following installed skills and guidelines:

### 1. UI/UX Pro Max & Frontend Design (Anthropics)
- **Bold Aesthetics**: Create distinctive, production-grade frontend interfaces that avoid generic "AI slop" or cliche palettes (like default purple/pink gradients). Commit to a cohesive, intentional aesthetic direction (e.g., minimalist, brutalist, soft UI, etc.).
- **Typography & Polish**: Use appropriate font pairings (avoid defaulting to space grotesk/inter if it doesn't fit the mood). Add subtle depth, shadow layering, and smooth hover state transitions (150-300ms).
- **Spatial Composition**: Be creative with layouts, use generous negative space, grid-breaking elements, and contextual effects where beneficial.

### 2. Web Interface Guidelines (Vercel Labs)
- **Accessibility**: Use semantic HTML (`<button>`, `<nav>`, `<dialog>`). Ensure `aria-hidden` on decorative icons, `alt` tags on images, and visible focus states (`focus-visible:ring-*`). Do not use `outline-none` without replacing the focus indicator.
- **Interactions**: Ensure interruptible animations and respect `prefers-reduced-motion`. Buttons/links must have clear hover states. Use `touch-action: manipulation` to prevent zoom delays on mobile.
- **Hydration & i18n**: Use `Intl.*` APIs for formatting numbers and dates. Beware of server/client hydration mismatches. Use `translate="no"` for brand names or tokens.
- **Anti-patterns to Avoid**: `transition: all`, inline `onClick` without `<button>`, preventing paste via `onPaste`, missing image dimensions, and disabling zoom. 

### 3. shadcn-vue Guidelines
- Always prioritize using Vue ports of shadcn components via CLI before building custom UI blocks. 
- Keep components neatly stored in `components/ui/`.
- Combine utility classes carefully using tools like `tailwind-merge` and `clsx` (standard shadcn utils).

### 4. Code Refactoring (Simplify)
- **Simplify Skill**: When reviewing or refactoring code, aim to reduce technical debt and over-engineering without modifying core functionality.
- Focus strictly on: increasing component reuse, resolving unclear naming or complex conditionals, removing redundant computations, and ensuring consistent style.
- Balance readability with simplicity; do not write overly terse code at the expense of comprehension.
