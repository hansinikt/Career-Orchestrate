# Part B: System, data, database and API

## 5. Architecture

### 5.1 The picture

![System architecture: frontend, backend, engine, database, catalogue and optional AI](diagrams/v2_arch.png)

**Reading the picture.** Solid lines are in the prototype and run today. Dashed orange boxes are optional: the AI adapter and SAP's model service are used only if they pass the tests in sections 10 and 17. The frontend calls the backend over HTTP. The backend validates each request, asks the engine to calculate, and stores results in SQLite. The catalogue is read from files in Git.

### 5.2 Components and who owns them

| Component | What it does | What it must not do | Owner |
|---|---|---|---|
| Frontend (`frontend/`) | Seven screens; one `api` file | Calculate anything; store work text; hold keys | Dev 1 |
| Routes (`backend/app/main.py`) | Validate requests against the contract, call the engine, store and return results, map errors to the error shape | Contain scoring rules | Dev 2 |
| Storage (`backend/app/db.py`, `schema.sql`) | SQLite through the standard library | Hold the catalogue | Dev 2 |
| Engine (`engine/`) | Pure functions: suggest skills, rank roles, build plans, select messages, check job adverts, compare audit variants | Read the network, the database, or any forbidden field | Dev 3 |
| Catalogue (`data/v2/*.json`) | Skills, roles, courses, aliases, personas, fixtures | Change at runtime | Dev 3; `resources.json` only Dev 4 |
| Contract (`contracts/v2/`) | The data shapes; the generated OpenAPI | Change without all four agreeing | All |
| Tests (`tests/`) | Lock behaviour and the worked numbers | Be skipped | Dev 4 |

### 5.3 Why this design [J]

A single Python process with plain functions is the smallest thing that satisfies the research document's methodology (evidence, readiness, human checkpoints, fairness review) and is something four beginners can understand, run and debug. The project's "agents" are modules with one job each, run in a fixed order with two human gates. They are not autonomous language-model agents. In the pitch, call them "specialised modules orchestrated in a fixed workflow", which is accurate and defensible. An optional wrapper in SAP Joule Studio is "designed next".

| Module (pitch name) | Code | Uses AI? | Section |
|---|---|---|---|
| Skills Discovery | `engine/extract_rules.py` | Rules in the prototype; optional model later | 9.1 |
| Inclusive Matching | `engine/core.py: score_role, rank` | No | 9.3 |
| Learning Pathway | `engine/core.py: build_plan` | No | 9.5 |
| Progress and Motivation | `engine/motivation.py` | No | 9.7 |
| Employer Readiness (openness check) | `engine/readiness.py` | No | 9.8 |
| Bias Audit | `engine/core.py: compare, flags_for`, `main.py: audit_run` | No | 9.9 |
| Market Intelligence | The catalogue plus a job-posting check by hand | No | 11.4 |

### 5.4 The request sequence

![Request sequence for the main journey](diagrams/v2_seq.png)

### 5.5 Running it

**First time (every developer):**

1. Install Python 3.11 or newer. Clone the repository.
2. `make setup` (creates a virtual environment and installs `backend/requirements.txt`).
3. `make test`. Expect 41 passed. If not, stop and tell Dev 4.
4. `make run`. Open `http://localhost:8000/docs` to see and try every endpoint.
5. Optional: `cp .env.example .env`. The app runs without it.

**Demo mode on one laptop (offline):** build the frontend, copy the build into `frontend_dist/` at the repository root, then `make demo`. Everything is at `http://localhost:8000`. Do the same rehearsal on the actual demo laptop with the Wi-Fi turned off.

**Smoke test with no frontend** (uses real data and shows the contract working): run `python data/build_fixtures_v2.py`, then open the files in `data/v2/fixtures/`. They are the exact request and response bodies for Anitha's journey, produced by the real backend.

### 5.6 Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `APP_MODE` | `replay` | `replay`: no network calls. `live`: allowed to call an LLM provider (only after section 10 tests) |
| `DB_PATH` | `./app.db` | SQLite file. User data only. In `.gitignore` |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins for development |
| `ALLOW_UNVERIFIED_RESOURCES` | `true` | Show `seed_unverified` courses (with badge) |
| `ALLOW_SAMPLE_RESOURCES` | `true` | Show `sample_placeholder` courses (with badge). Set to `false` when verified courses exist |
| `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `AICORE_*` | empty | Reserved for the optional adapter (section 10) |

### 5.7 Repository layout

```
career-orchestrator/
  AGENTS.md                  rules for AI assistants (read first)
  LEGACY_V1.md               which old files to ignore
  Makefile                   setup, test, run, demo, seed, fixtures, contracts
  .env.example               every setting, no secrets
  contracts/v2/
    models.py                THE CONTRACT (Appendix A)
    openapi.yaml, openapi.json, schemas/   generated by `make contracts`
  engine/                    pure functions, no network, no database
    core.py                  match, gaps, plan, grounding, audit maths
    extract_rules.py         skill suggestion from text and declared skills
    motivation.py            events, message library, selection
    readiness.py             job-advert openness rules
  backend/
    requirements.txt         pinned versions
    app/main.py              routes, error mapping, storage wiring
    app/db.py, schema.sql    SQLite
  data/
    source/                  the team's CSV files, unchanged
    build_seed_v2.py         CSV to catalogue (deterministic)
    build_fixtures_v2.py     runs Anitha's journey, saves every request/response
    run_v2_examples.py       worked examples quoted in this document
    v2/                      skills.json roles.json resources.json aliases.json personas.json fixtures/
  frontend/                  Dev 1
  frontend_dist/             built frontend for demo mode (not in Git until final)
  tests/test_v2.py           18 tests; tests/test_all.py is legacy v1 (23 tests)
  docs/                      this document and its sources
  .github/workflows/ci.yml   runs tests and contract check on every push
```



## 6. Data

### 6.1 Sources [S]

| File (data/source/) | Rows | How it is used |
|---|---|---|
| `career_roles.csv` | 8 roles | Role titles, summaries, families. Its `required_skills` column is NOT used for scoring (see 6.4, finding 1) |
| `role_skill_requirements.csv` | 38 rows | The source of truth for role requirements: skill, Required or Preferred, target proficiency |
| `learning_resources.csv` | 9 courses | Course catalogue (statuses in 6.4) |
| `user_profiles.csv` | 8 people | Demo personas. `years_experience`, `education` and `country` are never read by the engine |
| `user_skills.csv` | 29 rows | The skills each persona "declares" (all self-reported) |
| `work_experience.csv` | 8 rows | The persona's work text, used as the work example |
| `learning_progress.csv` | 8 rows | Sample progress rows. Not used by the engine (see 6.4, finding 5) |
| Research document, SAP tools PDF, screenshot | n/a | Positioning, SAP options, access |

All of these are labelled illustrative by their author ("validate against real job descriptions") [S].

### 6.2 Mapping rules (CSV to catalogue) [J]

| Source value | Becomes | Note |
|---|---|---|
| Beginner, Intermediate, Advanced | level 1, 2, 3 | The engine's scale is 0 to 3; 0 means no skill |
| Required, Preferred | importance 5 and mandatory true; importance 3 and mandatory false | Provisional |
| Skill hours per level | 12, 15 or 20 hours per level by skill group | Provisional. Course durations in the CSV are in weeks, so hours are our estimate, not a fact |
| Role interest tags | team-assigned: HR Coordinator = people, operations; Project Coordinator = planning, operations; Data Analyst = data; Business Analyst = data, planning; Operations Analyst = operations, data; L&D Coordinator = people, planning; CRM Analyst = data, people; Compliance Coordinator = compliance, operations | Provisional |
| `resource_url` that is a homepage only | `seed_unverified` | A homepage is not a course page |
| Course with no provider or URL ("Sample learning path") | `sample_placeholder` | Never presented as a real course |

Rebuild with `make seed` after editing a CSV. The output is deterministic.

### 6.3 Catalogue files (`data/v2/`)

| File | Content | Edited by |
|---|---|---|
| `skills.json` | 25 scored skills plus 9 extra names found in the data. Three extras are proposed aliases of scored skills. Fields: `skill_id`, `name`, `category`, `hours_per_level`, `alias_of`, `alias_status`, `scored` | Dev 3 |
| `roles.json` | 8 roles with `requirements[{skill_id, importance, required_level, mandatory}]`, `tags`, `data_note` | Dev 3 |
| `resources.json` | 9 courses with `verification_status`, `url`, `last_verified`, `note`. Only the values `verified`, `seed_unverified`, `sample_placeholder` exist | **Dev 4 only** |
| `aliases.json` | Keyword phrases per skill, used by the rules extractor | Dev 3 |
| `personas.json` | The 8 personas with `declared_skills`, `work_text`, `stated_goal_role_id` | Generated |
| `fixtures/` | Real request and response bodies | Generated |

**Skill identifiers.** `SK-EXCEL`, `SK-COMM`, `SK-RECORDS`, `SK-SCHED`, `SK-CONF`, `SK-DOC`, `SK-RISK`, `SK-REPORT`, `SK-SQL`, `SK-DATACLEAN`, `SK-STATS`, `SK-VIZ`, `SK-PROCANALYSIS`, `SK-REQ`, `SK-PROCIMPROVE`, `SK-DATAANALYSIS`, `SK-PROBLEM`, `SK-TRAINCOORD`, `SK-LEARNADMIN`, `SK-CRM`, `SK-DATAQUALITY`, `SK-DASH`, `SK-DOCCONTROL`, `SK-DETAIL`, `SK-COMPDOC`. Role ids are `R001` to `R008` exactly as in the CSV.

**Aliases and unscored skills.** The names below appear in `user_skills.csv` but not in any role. Three are *proposed* aliases of scored skills: "Stakeholder communication" to Communication, "Case documentation" to Documentation, "Sales reporting" to Reporting. These are team judgments; the worker is asked to confirm each one (badge "We matched your wording, please confirm"). The others ("Team coordination", "Presentation skills", "Microsoft Office", "Customer service", "Process coordination", "HR administration") have no scored equivalent; they are shown under "Skills we could not match yet" and are not scored. **Open decision OD1** (section 18): whether to add "HR administration" as a requirement of HR Coordinator, since course C005 teaches it.

### 6.4 What we found in the data (verified by script) [V]

| # | Finding | Consequence | Action | Owner |
|---|---|---|---|---|
| 1 | Seven skills are listed as required in `career_roles.csv` but marked Preferred in `role_skill_requirements.csv` (HR Coordinator: Scheduling; Project Coordinator: Risk tracking; Data Analyst: Visualization; Business Analyst: Excel; L&D Coordinator: Learning administration; CRM Analyst: Dashboard basics; Compliance Coordinator: Communication) | Two files disagree | We use `role_skill_requirements.csv` | Done |
| 2 | 10 of 25 role skills have no course: Attention to detail, Confidentiality, Dashboard basics, Data cleaning, Documentation, Learning administration, Problem solving, Process improvement, Statistics, Training coordination | Many plan steps will read "no verified resource yet". Anitha's one required gap (Confidentiality) has no course | Find and verify real courses (section 11) | Dev 4, Dev 3 |
| 3 | Six of nine courses have no provider or URL ("Sample learning path"); the other three link only to a homepage | None can be shown as verified | Replace with real course pages | Dev 4 |
| 4 | Skill names differ between files: "Stakeholder communication", "Case documentation", "Sales reporting" | Workers look like they lack skills they likely have | Alias table (6.3), worker confirms | Dev 3 |
| 5 | `learning_progress.csv` assigns Anitha a beginner Excel course (C001) though she lists Excel at Intermediate | The engine would not recommend it | Treat the file as sample data; Anitha's progress comes from her own plan | Dev 3 |
| 6 | Every skill is self-reported; each person has only 2 to 4 skills and one sentence of work text | Results are coarse; most other roles score low for everyone | Do not draw statistical conclusions; use for demonstration | All |
| 7 | `years_experience` is present (Anitha: 15) | Must never influence anything | Never read; test `test_contract_has_no_forbidden_fields` | All |
| 8 | Courses cover only level 0 to 1 (Beginner) | A gap of two levels needs a second resource that does not exist | Shown as "no verified resource yet" for the higher level | Dev 4 |

### 6.5 What the engine does with all eight personas [V]

Confirmed skills only, no interests, default weights. "Rank of goal" is where the person's own stated goal lands among the 8 roles.

| Persona | Stated goal | Rank of goal | Band | Score | Gap hours | Blocking gaps | Top three roles |
|---|---|---|---|---|---|---|---|
| Anitha Raman | HR Coordinator | 1 | bridgeable | 0.6368 | 48 | Confidentiality | HR Coordinator, Business Analyst, L&D Coordinator |
| Priya Sharma | Project Coordinator | 1 | bridgeable | 0.6515 | 42 | Reporting | Project Coordinator, L&D Coordinator, HR Coordinator |
| Rahul Kumar | Data Analyst | 3 | stretch | 0.3527 | 70 | SQL, Statistics | Operations Analyst, CRM Analyst, Data Analyst |
| Sneha Reddy | Business Analyst | 2 | stretch | 0.4172 | 75 | Process analysis, Requirements gathering | Project Coordinator, Business Analyst, L&D Coordinator |
| Kiran Patel | Operations Analyst | 4 | stretch | 0.2294 | 84 | Reporting, Process improvement, Data analysis, Problem solving | HR Coordinator, CRM Analyst, Data Analyst |
| Meera Nair | L&D Coordinator | 1 | strong_fit | 0.8529 | 12 | none | L&D Coordinator, Project Coordinator, HR Coordinator |
| Arjun Das | CRM Analyst | 1 | bridgeable | 0.6883 | 27 | Data quality | CRM Analyst, Operations Analyst, Project Coordinator |
| Fatima Khan | Compliance Coordinator | 1 | strong_fit | 0.8235 | 24 | none | Compliance Coordinator, L&D Coordinator, CRM Analyst |

Two lessons. First, for three people (Rahul, Sneha, Kiran) the system ranks other roles above their own goal; this is why Screen 4 always shows "Your goal" with its own analysis and never overrides it. Second, with only 2 to 4 skills each, scores for non-goal roles are very low; do not present them as meaningful rankings beyond the top few.



## 7. Database

### 7.1 Principles

1. SQLite, accessed with Python's built-in `sqlite3`. No ORM and no migration tool; the schema is one file, `backend/app/schema.sql`, applied at startup [J].
2. The database holds **user data only**. The catalogue is read from `data/v2/*.json`.
3. Structured results (suggestions, confirmed skills, plans, audits) are stored as JSON text in a `payload` column, because the contract (not the table) defines their shape.
4. Foreign keys are enforced and deletes cascade: deleting a profile deletes everything about that person except the audit log.
5. The `audit_log` stores identifiers, action names and small counts only, never work text, names or skills.
6. The database file is never committed. For the demo, start from an empty database and create Anitha live, or keep a copy of a prepared file.

### 7.2 The picture

![Database tables and relationships](diagrams/v2_er.png)

### 7.3 Schema (from `backend/app/schema.sql`)

```sql
{{FILE:backend/app/schema.sql}}
```

### 7.4 What each table holds and when it changes

| Table | Written by | When | Read by |
|---|---|---|---|
| `profiles` | `POST /profiles` | Screen 2 submit. Motivation changed by `PUT .../motivation` | Almost every endpoint |
| `extractions` | `POST .../extract` | Screen 2, after profile creation (replaces any earlier row) | `confirm` |
| `confirmations` | `POST .../confirm` | Gate 1. Also deactivates any active plan | `recommendations`, `plan`, `audit` |
| `plans` | `POST .../plan` | Gate 2. Older plans are set `active = 0` | `GET .../plan`, `progress` |
| `progress` | `POST .../progress` | Each step update (one row per plan and step, replaced on update) | `progress` |
| `messages` | `POST .../progress`, `GET .../progress` (a "behind" nudge) | When a motivation event happens | `progress`, feedback |
| `audits` | `POST .../audit`, `POST /audits/{id}/review` | Fairness check; review sets the `review` field | `GET /audits/{id}` |
| `audit_log` | every write endpoint | Append only | The adviser, the demo |

### 7.5 Retention and deletion

`DELETE /api/v1/profiles/{id}` removes the profile and all dependent rows. The audit log keeps one line, `profile_deleted`, with the identifier. For the prototype there is no automatic purge; do not store real personal data (all demo data is synthetic).

### 7.6 Backup and failure

SQLite writes are durable at each request. Before the demo, copy `app.db` to a second location after loading the demo personas. If the database is corrupted, delete the file; the app recreates it and the journey takes about two minutes to re-enter.



## 8. API contract

### 8.1 Conventions

| Topic | Rule |
|---|---|
| Base path | `/api/v1`. Contract version `2.0` (returned by `GET /api/v1/meta`) |
| Format | JSON in, JSON out. `Content-Type: application/json` |
| Unknown fields | Rejected with `422`. A forbidden field (age, date of birth, gender and similar) returns code `FORBIDDEN_FIELD` |
| Ids | `prof_` + 10 hex, `plan_`, `msg_`, `aud_`; suggestion ids are `sg_` + the skill id |
| Time | ISO 8601 in UTC, seconds precision |
| Errors | Always `{"error": {"code", "message", "details"}}` (section 4.5) |
| Idempotency | `extract` can be run again (replaces the earlier suggestions; the earlier confirmation stays in force until a new `confirm` is sent); `confirm` replaces the earlier confirmation and deactivates any plan; `plan` creates a new active plan |
| Order | profile, extract, confirm, recommendations, plan, progress. Out-of-order calls return `409` |
| Auth | None in the prototype. Do not expose the backend to the internet [J] |
| Documentation | `http://localhost:8000/docs` (generated, always current) |

### 8.2 Endpoints (generated from `contracts/v2/openapi.json`)

{{ENDPOINTS}}

### 8.3 Worked requests and responses (real output from Anitha's journey)

Long lists are shortened with "... n more". Identifiers differ on every run.

**1. Create the profile** `POST /api/v1/profiles`

```json
{{FIX:01_profile_create_request:6}}
```

Response `201` (the profile with its `profile_id` and `created_at`):

```json
{{FIX:02_profile:6}}
```

**2. Suggest skills** `POST /api/v1/profiles/{id}/extract` (no body)

```json
{{FIX:03_extract_response:3}}
```

Look at the two `extracted` suggestions: their level is 2 (inference never exceeds 2), their evidence is the worker's own words, and they are not yet part of her profile until she accepts them.

**3. Confirm (Gate 1)** `POST /api/v1/profiles/{id}/confirm`. Exactly one decision per suggestion.

```json
{{FIX:04_confirm_request:6}}
```

Response: `confirmed_skills` (with evidence) and `rejected_skill_ids`.

```json
{{FIX:05_confirm_response:3}}
```

**4. Role matches** `GET /api/v1/profiles/{id}/recommendations` (first role shown)

```json
{{FIX:06_recommendations:1}}
```

**5. Choose a role and get the plan (Gate 2)** `POST /api/v1/profiles/{id}/plan`

```json
{{FIX:07_plan_request:3}}
```

```json
{{FIX:08_plan_response:3}}
```

The single step has `"status": "no_verified_resource"` because no course in the data teaches Confidentiality (finding 2 in 6.4). This is the honest result today; section 11 explains how to change it.

**6. Update progress** `POST /api/v1/profiles/{id}/progress`

```json
{{FIX:09_progress_update_request:3}}
```

```json
{{FIX:10_progress_response:3}}
```

**7. Fairness check** `POST /api/v1/profiles/{id}/audit` with `{"canary": true}` (variants shortened)

```json
{{FIX:12_audit_canary:3}}
```

**8. Job-advert check** `POST /api/v1/readiness/check`

```json
{{FIX:13_readiness:4}}
```

**9. Errors**

```json
{{FIX:14_error_forbidden_field:3}}
```

```json
{{FIX:15_error_consent:3}}
```

### 8.4 A frontend call example (shape only)

The same pattern is used for every call. Write it once in the `api` file and reuse it.

```
function call(method, path, body):
    response = send HTTP request to BASE_URL + path with JSON body
    if response is not OK:
        error = parse JSON body  (it always has error.code and error.message)
        raise error                (the screen shows error.message and a Try again button)
    return parse JSON body
```

### 8.5 Contract change process

1. A developer who needs a change writes down: the field, the screen or function that needs it, and what breaks without it.
2. Dev 4 gathers a yes from all four. If any developer says no, the change waits until after the demo.
3. Dev 3 or Dev 2 edits `contracts/v2/models.py`; run `make contracts`; commit the regenerated files with the change in one commit.
4. CI fails if the generated files do not match, so nobody can change a shape quietly.
5. Frontend and backend update their code the same evening. Until the demo, no breaking change is allowed after Monday 22:00.
