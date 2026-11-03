# AGENTS.md - rules for every AI coding assistant in this repo (v2)

You build ONE small task of Career Orchestrator. The human gives you a task id from docs/PRD_v2 section 13. Read ONLY: this file, the task text, `contracts/v2/models.py`, and the files the task names.

1. `contracts/v2/models.py` is the ONLY definition of data shapes. Never rename, add, remove or "improve" a field, enum value, endpoint or error code. If you think a change is needed, STOP and tell the human; they raise a Contract Change.
2. Never add age, date of birth, gender, name-as-feature, graduation year or years of experience anywhere: not in models, not in functions, not in prompts, not in UI. Tests will fail if you do.
3. NEVER invent course names, URLs, hours, statistics, job postings or API endpoints. Only a human edits `data/v2/resources.json`. If data is missing, write `null` and say so.
4. No new libraries, frameworks, databases or services. Allowed: what is in `backend/requirements.txt` (Python) and what the frontend already uses. Ask first.
5. Stay in your own folder (see .github/CODEOWNERS). Do not edit other people's files.
6. No secrets in code. Configuration comes from environment variables (see .env.example). Never commit `.env` or `app.db`.
7. Business logic lives ONLY in `engine/`. The frontend shows what the API returns and never recomputes scores, bands, hours or messages.
8. Show your PLAN (files to change, in bullets) BEFORE writing code. Keep to the task. Do not add features.
9. After the task, run `make test`. Paste the result. Do not say "done" if any test fails.
10. If anything in the task or PRD is unclear or contradicts itself, STOP and ask. Never guess silently. List your assumptions at the end.

Ignore these legacy v1 paths (superseded, kept only for history): `contracts/models.py`, `contracts/openapi.*`, `contracts/schemas/`, `mock_api/`, `data/fixtures/`, `data/skills.json`, `data/roles.json`, `data/resources.json`, `docs/prd/`, `docs/PRD.*`, `tests/test_all.py`.
