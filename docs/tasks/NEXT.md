# STATUS AND NEXT TASKS (updated 3 Nov 2026, v3 build)

## Done in this build (all covered by `make test`, 61 tests)
- LLM adapter `backend/app/llm.py` (Gemini, rules fallback, replay mode). Agents in `backend/app/agents.py`: Skills Discovery (model answer is checked: catalogue ids only, quote must be the worker's exact words), Course Scout (picks only catalogue courses, reasons checked for invented numbers, human approves).
- Market Intelligence `engine/market.py` (counts from OUR catalogue only, never live market data).
- Orchestrator trace `backend/app/orchestrator.py`, `GET /api/v1/profiles/{id}/trace`; the dashboard panel "Which agents worked on this".
- Missions from plan steps (`engine/missions.py`), proof saved on the server (`POST .../missions/{mid}/proof`, JSON base64, max 2 MB, never served back).
- Security: headers (CSP, nosniff, no-store), request size limit, rate limit on model endpoints, CORS limited to same origin by default.
- Contract: ADDITIVE models only (AgentStep, TraceResponse, MarketResponse, ScoutResponse, Mission...). No existing field changed. `make contracts` was run. Tell the other developers.

## Added in the second batch (3 Nov, afternoon; 83 tests)
- Encouragement: `agents.polish` lets Gemini re-word the template in the chosen voice (sassy and fun); code rejects invented numbers, promises, links, lost quoted names. Template is the fallback.
- Missions: tied to course chapters when `data/v2/curriculum.json` has them; own progress bar (0, 50 started, 100 proof); `start`, `decline` (shows the full-screen encouragement) and `reopen` endpoints.
- Chapters: `GET/POST /profiles/{id}/steps/{order}/chapters`; ticked chapters set the step percent (hours-weighted only when every chapter has hours).
- CV: `POST /cv/parse` (plain text; redacts contact details, years, age and gender lines; every value must be a piece of the cleaned text), `PUT/GET /profiles/{id}/background` (education, certificates, languages, tools, barriers, situation), `GET /profiles/{id}/cv` (updated plain-text CV for applicant tracking systems).
- Course Scout skips courses the person lists as done.

## Still open (in priority order)
0. **Questionnaire rework** (approved list pending) and CV autofill in the wizard (the endpoints above are ready). The wizard still asks the old questions and keeps most answers only in the browser.
0b. **Chapter lists** in `data/v2/curriculum.json` for each real SAP course (title, ordered chapters, hours if shown). Never invent chapters.
1. **Real SAP Learning Hub courses** in `data/v2/resources.json` (title, course page link, hours, skills; only a human sets `verified`). Without them the Course Scout has nothing real to pick from: Anitha's gap (Confidentiality) has no course in the catalogue yet.
2. **Gemini key** in a local `.env` (see `.env.example`), then `APP_MODE=live`, test the Anitha journey, set `LLM_RECORD=true` once to save the answers, then demo in `APP_MODE=replay`.
3. SAP platform: Cloud Foundry deployment, HANA Cloud for audit/trace records (`hdbcli` approved by the team lead), Credential Store for the key.
4. Not built: Skill Check questions, real accounts (demo sign-in only), CV reading for PDF and Word, certificate storage on the server.

## Rules reminder
No age, gender, date of birth or years of experience anywhere. Never invent course names, links or hours. Business logic only in `engine/`. The frontend never recomputes scores.
