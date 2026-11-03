# CLAUDE.md (read automatically by Claude Code)

Project: Career Orchestrator, SAP Hackfest 2026 Theme 2 (Inclusive Workforce). Demo person: Anitha Raman.

@AGENTS.md

## Where things are
- Rules for every change: AGENTS.md (the ten rules). The contract is `contracts/v2/models.py` and is frozen: never change a field without being told to.
- Role briefs (the source of truth for each role): `docs/briefs/out/00_TEAM_BRIEF.md`, `01_FRONTEND_BRIEF.md`, `02_BACKEND_BRIEF.md`, `03_DATA_AI_BRIEF.md`, `04_INTEGRATION_BRIEF.md`.
- Backend `backend/app/`, calculations `engine/`, catalogue `data/v2/`, tests `tests/`, plain HTML/CSS/JS frontend `frontend/` (no frameworks, no CDN, offline).
- The earlier SAP UI5 login app was moved to `archive/ui5-frontend/` (not used). `database/` holds old SQL scripts that the backend does NOT use (the backend uses SQLite via `backend/app/schema.sql`).

## How tasks arrive
The person will say "do the next task". Then:
1. Read `docs/tasks/NEXT.md` and the brief it names. Do not read other docs unless the task says so.
2. Reply with a PLAN only (files to change, bullets). Wait for "go".
3. Implement. Stay inside the files the task allows.
4. Run `make test`. Paste the result. Never say done while a test fails.
5. List every assumption. Commit on the current branch with a clear message.

## Run
`make setup` (once), `make test` (expect 41 passed or more), `make run` then open http://localhost:8000/
