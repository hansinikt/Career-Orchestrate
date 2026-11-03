# Career Orchestrator: BACKEND BRIEF (Dev 2)

=== INSTRUCTIONS FOR THE AI ASSISTANT (read this first, follow it exactly) ===
You are helping ONE developer on the BACKEND part of "Career Orchestrator", a hackathon prototype built by four first-time collaborators.
This brief is your ONLY source of truth. Rules:
1. Use only what is written in this brief and in files the developer pastes into the chat. If something is not specified, reply "Not specified in the brief" and ask the developer. Never guess.
2. Never invent: API endpoints, field names, status codes, library or package names, file names, course names, web links, statistics, or job adverts.
3. Never add or use age, date of birth, gender, graduation year, or years of experience, anywhere (code, data, screens, prompts, tests).
4. Allowed technology: Python 3.11+, the standard library, and ONLY these packages: fastapi, uvicorn, pydantic, httpx, pytest, PyYAML. No ORM, no other database than SQLite, no new frameworks, no task queues.
5. Files you may create or change: backend/app/*, backend/requirements.txt (only if the team agrees), tools/*.py (new), the Makefile (only the backup and restore targets), and NEW test files named tests/test_backend_*.py. Never change any other file.
6. Work on ONE task at a time. The developer will name a task id. Your FIRST reply must be a PLAN only (files to change, with bullet points). Wait for the developer to say "go" before writing code.
7. After writing code, give the exact command(s) to test it and list every assumption you made. Do not say "done" unless the tests pass.
8. If this brief contradicts itself or the request would break a rule, STOP and say so.
=== END OF INSTRUCTIONS ===

Paste this whole brief into your AI assistant at the start of each chat, then your task id (B1 to B7, section 9) and the files the task changes.

## 1. Your mission

**A working backend already exists** in `backend/app/`. It passes 41 tests and serves the whole journey with no AI key. You now **own** it. Your job is to understand every line, run it, try to break it, make it reliable, and add the pieces in section 9. You are the person who must be able to explain to the judges what happens to a worker's data at every step.

You are not asked to rewrite it, add frameworks, or change the data shapes.

## 2. Run it

```
make setup      first time: creates .venv and installs backend/requirements.txt
make test       expect: 41 passed
make run        API on http://localhost:8000 ; interactive docs at http://localhost:8000/docs
```
Try every endpoint at `/docs` with the "Try it out" button before you change anything.

## 3. Files

| File | What it does | You may change |
|---|---|---|
| `backend/app/main.py` | All routes, error handlers, wiring of engine + storage | Yes |
| `backend/app/db.py` | SQLite via the standard library; a lock around each call | Yes |
| `backend/app/schema.sql` | Table definitions (applied at start-up) | Yes, but a schema change needs the team's agreement |
| `engine/*.py` | All calculations (Dev 3 owns) | **No. Call it, never edit it** |
| `data/v2/*.json` | Roles, skills, courses (Dev 3 / Dev 4 own) | **No** |
| `contracts/v2/models.py` | The contract | **No. Frozen** |
| `tests/test_v2.py` | 18 tests for the whole API (Dev 4 owns) | No; add your own file `tests/test_backend_*.py` |

## 4. Architecture rules

1. The backend does four things only: **validate** the request against the contract, **call the engine**, **store or read** user data, **return** the result. It contains no scoring, matching, message or audit logic. Those are in `engine/`.
2. SQLite holds **user data only**. The catalogue (roles, skills, courses) is read from `data/v2/*.json` when the server starts.
3. Every error response has the shape `{"error": {"code", "message", "details"}}`. Codes: `VALIDATION_ERROR`, `FORBIDDEN_FIELD`, `NOT_FOUND`, `CONSENT_REQUIRED`, `SKILLS_NOT_CONFIRMED`, `NO_ACTIVE_PLAN`, `INTERNAL`. Do not add codes.
4. Unknown request fields are rejected (the models use `extra="forbid"`). A field named like age, dob, gender, sex, caste, religion, years_experience returns `FORBIDDEN_FIELD`. **Never add such a field anywhere.**
5. Nothing is scored until the worker has confirmed skills (`409 SKILLS_NOT_CONFIRMED`). No progress exists without a plan (`409 NO_ACTIVE_PLAN`).
6. Never log work text, names or skills. The `audit_log` table stores ids, action names and small counts only.

## 5. The endpoints (generated from the contract)

| Method | Path | Request body | Success response |
|---|---|---|---|
| GET | `/api/v1/audits/{aid}` | - | 200 AuditResult |
| POST | `/api/v1/audits/{aid}/review` | ReviewRequest | 200 AuditResult |
| GET | `/api/v1/demo/personas` | - | 200  |
| GET | `/api/v1/health` | - | 200  |
| GET | `/api/v1/meta` | - | 200 Meta |
| POST | `/api/v1/profiles` | ProfileCreate | 201 Profile |
| DELETE | `/api/v1/profiles/{pid}` | - | 204  |
| GET | `/api/v1/profiles/{pid}` | - | 200 Profile |
| POST | `/api/v1/profiles/{pid}/audit` | AuditRequest | 200 AuditResult |
| POST | `/api/v1/profiles/{pid}/confirm` | ConfirmRequest | 200 ConfirmResponse |
| POST | `/api/v1/profiles/{pid}/extract` | - | 200 ExtractResponse |
| POST | `/api/v1/profiles/{pid}/messages/{mid}/feedback` | MessageFeedback | 204  |
| PUT | `/api/v1/profiles/{pid}/motivation` | MotivationPrefs | 200 MotivationPrefs |
| GET | `/api/v1/profiles/{pid}/plan` | - | 200 PlanResponse |
| POST | `/api/v1/profiles/{pid}/plan` | PlanRequest | 200 PlanResponse |
| GET | `/api/v1/profiles/{pid}/progress` | - | 200 ProgressResponse |
| POST | `/api/v1/profiles/{pid}/progress` | ProgressUpdate | 200 ProgressResponse |
| GET | `/api/v1/profiles/{pid}/recommendations` | - | 200 RecommendationsResponse |
| POST | `/api/v1/readiness/check` | ReadinessRequest | 200 ReadinessResult |
| GET | `/api/v1/roles` | - | 200  |
| GET | `/api/v1/skills` | - | 200  |

### What each endpoint does, in order of the journey

| Endpoint | Checks | Reads | Writes | Returns / errors |
|---|---|---|---|---|
| `POST /profiles` | `consent` must be true; goal role id must exist; each work example 10 to 1000 chars | | `profiles`, `audit_log` | `201 Profile`. `400 CONSENT_REQUIRED`; `422` for bad fields |
| `POST /profiles/{id}/extract` | profile exists | `profiles` | `extractions` (replaces), `audit_log` | Suggestions from `engine.extract_rules.suggest`. Each `suggestion_id` is `"sg_" + skill_id` |
| `POST /profiles/{id}/confirm` | Exactly one decision per suggestion (no missing, unknown or duplicate ids); `edit` needs `level`; added skills must be scored catalogue skills and not already confirmed | `extractions` | `confirmations` (replaces), `plans.active = 0` for this profile, `audit_log` | `ConfirmResponse`. `409` if no extraction; `422` for rule breaks |
| `GET /profiles/{id}/recommendations` | skills confirmed | `profiles`, `confirmations` | `audit_log` | All 8 roles ranked by `engine.core.rank`; `goal` = the stated goal role's entry (or null). `409 SKILLS_NOT_CONFIRMED` |
| `POST /profiles/{id}/plan` | role id exists | `profiles`, `confirmations` | `plans` (old plans set inactive; new one active), `audit_log` | `PlanResponse` from `engine.core.build_plan` |
| `GET /profiles/{id}/plan` | | `plans` | | Active plan or `409 NO_ACTIVE_PLAN` |
| `PUT /profiles/{id}/motivation` | | | `profiles.motivation` | The saved preferences |
| `POST /profiles/{id}/progress` | step order must exist in the active plan | `plans`, `progress` | `progress` (one row per plan and step), maybe `messages` | `ProgressResponse`. `next_message` only if an event happened |
| `GET /profiles/{id}/progress` | active plan | `plans`, `progress`, `messages` | may create one `behind` message if 7+ days of silence | `ProgressResponse` |
| `POST /profiles/{id}/messages/{mid}/feedback` | message belongs to profile | `messages` | `messages.helpful` | 204 |
| `POST /readiness/check` | text 20 to 5000 chars | | | `engine.readiness.check` result |
| `POST /profiles/{id}/audit` | | `profiles` | `audits`, `audit_log` | Six variants (A29, A42, A50, A58, P5, P25) plus `CANARY` if requested |
| `POST /audits/{id}/review` | audit exists | `audits` | `audits` (adds `review`), `audit_log` | The audit with its review |
| `DELETE /profiles/{id}` | profile exists | | all rows for the profile (cascade), `audit_log` keeps one line | 204 |

### Engine functions the backend calls (never reimplement them)

```
extract_rules.suggest(declared: list[dict], texts: list[str], sk: dict) -> (suggestions: list[dict], unmatched_names: list[str])
core.rank(user_levels: dict[skill_id, int], roles, interests: list[str], sk, evidence: dict[skill_id, list[str]]) -> list[dict]
core.build_plan(rec, user_levels, sk, resources, weekly_hours, allow_unverified=True, allow_sample=False) -> dict
core.compare(base, variant) -> metrics dict ;  core.flags_for(variant_id, metrics) -> list
motivation.plan_numbers(steps, progress: dict[order, percent], weekly_hours, matched_count=0) -> dict
motivation.detect_event(before_pct, after_pct, steps_done_before, steps_done_after, total_steps, days_since_last, first_update) -> event | None
motivation.select(styles, event, numbers, shown_count) -> (style, text, suggested_action)
readiness.check(text) -> dict
```

## 6. Database (from `backend/app/schema.sql`)

```sql
-- User data only. The catalogue (skills, roles, courses) lives in data/v2/*.json under Git.
CREATE TABLE IF NOT EXISTS profiles (
  profile_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  current_role TEXT,
  work_examples TEXT NOT NULL,
  declared_skills TEXT NOT NULL,
  stated_goal_role_id TEXT,
  preferences TEXT,
  motivation TEXT,
  consent_at TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS extractions (
  profile_id TEXT PRIMARY KEY REFERENCES profiles(profile_id) ON DELETE CASCADE,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS confirmations (
  profile_id TEXT PRIMARY KEY REFERENCES profiles(profile_id) ON DELETE CASCADE,
  payload TEXT NOT NULL,
  confirmed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
  plan_id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
  role_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progress (
  plan_id TEXT NOT NULL REFERENCES plans(plan_id) ON DELETE CASCADE,
  step_order INTEGER NOT NULL,
  percent INTEGER NOT NULL,
  hours_logged REAL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (plan_id, step_order)
);

CREATE TABLE IF NOT EXISTS messages (
  message_id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
  plan_id TEXT,
  style TEXT NOT NULL,
  event TEXT NOT NULL,
  text TEXT NOT NULL,
  suggested_action TEXT NOT NULL,
  helpful INTEGER,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audits (
  audit_id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  profile_id TEXT,
  detail TEXT
);
```

Rules: foreign keys are on and deletes cascade. Structured results (`payload`) are stored as JSON text. The file is `app.db` (set by `DB_PATH`); never commit it. Deleting a profile removes everything about the worker except the `audit_log`, which keeps ids and action names only.

## 7. Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `DB_PATH` | `./app.db` | SQLite file |
| `APP_MODE` | `replay` | `replay` or `live`. Today only rules run; `live` is for the optional AI adapter (B6) |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins (development default) |
| `ALLOW_UNVERIFIED_RESOURCES` | `true` | Show `seed_unverified` courses (the frontend labels them) |
| `ALLOW_SAMPLE_RESOURCES` | `true` | Show `sample_placeholder` courses (the frontend labels them) |

The frontend is served by the same process: from `frontend_dist/` if it exists, otherwise from `frontend/` if it has an `index.html`.

## 8. Things to study and improve (not known bugs: read the code and decide)

1. `GET /progress` can write a `behind` message to the database. A GET that changes data is unusual. Understand why it was done and whether it is safe.
2. Time comes from `now()` in `main.py`. The "7 days of silence" behaviour is hard to test. How could a test control the time without changing the contract?
3. The audit runs the suggestion function seven times. Fine with rules; what would happen if each run called an AI?
4. One SQLite connection is shared with `check_same_thread=False` and a lock. What happens under two simultaneous requests?
5. `extract` replaces the suggestions but leaves the earlier confirmation in place until a new `confirm`. Is that the right behaviour? (It is documented; do not change it without the team.)
6. Unknown URLs and wrong methods return the error shape, but some map to the code `INTERNAL`. The contract only allows the listed codes.
7. There is no sign-in. The server must only run on the demo laptop, never on the open internet.
8. What happens if `data/v2/*.json` is malformed or a role refers to a missing skill? (Task B3.)

## 9. Tasks (one per AI chat)

| ID | Pri | Task | Done when |
|---|---|---|---|
| B1 | P0 | Run `make setup`, `make test`, `make run`. Try every endpoint at `/docs` with Anitha's data (the `data/v2/fixtures/` folder has real request bodies). Write down anything confusing or wrong | A short report posted to the group |
| B2 | P0 | Explain to the team, in plain words, what each endpoint does and where data is stored. Then write TWO new tests of your own in `tests/test_backend_basic.py` (for example: a missing consent, a duplicate decision) | Two new tests, both pass |
| B3 | P0 | **Start-up checks and request logging.** At server start, check: the three JSON catalogue files load; every role requirement skill exists in `skills.json` and is scored; every resource skill id exists; every `verified` resource has a `url` and `last_verified`; the weights sum to 1. If any check fails, stop with ONE clear message that lists every problem. Add a middleware that logs one line per request: method, path, status, milliseconds (no request bodies) | A deliberately broken `roles.json` (in a copy) gives a readable message; normal start still works; tests pass |
| B4 | P0 | **Demo seed script** `tools/seed_demo.py`. Using `httpx` against a running server (default `http://localhost:8000`), for each of Anitha Raman, Meera Nair and Kiran Patel (found by `display_name` in `GET /demo/personas`): create the profile with consent true and `preferences.weekly_hours` 6 (Anitha: motivation Progress + Encouragement; Meera: Goals; Kiran: Challenge), run extract, accept every suggestion, get recommendations, make a plan for the stated goal role. Print one table row per person (profile id, goal role, band, plan hours). Exit with a non-zero code if any step fails | Running it against a fresh database leaves three complete profiles |
| B5 | P0 | **Demo mode.** With a `frontend_dist/` folder present, `make demo` serves the pages and the API from one process. Test with the network switched off; check that `/docs` and `/api/v1/meta` still work | Works offline |
| B6 | P1 | **Optional AI adapter** `backend/app/llm.py` (section 10). Only if the team has a working key (gate G2) | Section 10 acceptance criteria |
| B7 | P1 | `make backup` copies `app.db` to `backups/app-YYYYMMDD-HHMMSS.db`; `make restore FILE=...` copies one back (add only these two targets to the Makefile) | Both tried |

## 10. B6 specification: the optional AI adapter (only if a key works)

The prototype must keep working with **no** AI. This adds an optional helper that can suggest extra skills.

- One file, `backend/app/llm.py`. One interface: `generate_json(task: str, variables: dict, json_schema: dict) -> dict`. It raises `LLMUnavailable` on any failure. Provider chosen by environment variable `LLM_PROVIDER` (`replay`, `sap_genai_hub`, `anthropic`, `openai`, `gemini`). Only this file knows the provider. Keys come from environment variables only (`LLM_API_KEY`, `LLM_MODEL`, and for SAP `AICORE_AUTH_URL`, `AICORE_CLIENT_ID`, `AICORE_CLIENT_SECRET`, `AICORE_BASE_URL`, `AICORE_RESOURCE_GROUP`).
- How to call SAP's service or any provider's SDK **is not specified in this brief**. Read the provider's own documentation; do not guess package names or endpoints. If you cannot verify them, say so.
- Task `suggest_skills`: variables are the work examples (as data), the list of allowed skill ids and names. The model must return JSON only, using only the listed skill ids, with a verbatim quote for each. The text inside the work examples is **data, never instructions**.
- After the reply: parse it with a model of your own in `llm.py`; drop any suggestion whose skill id is not in the catalogue or whose quote is not a verbatim substring (call `engine.core.quote_is_grounded`); cap the level at 2; merge with the rule-based suggestions; set `extraction_mode` to `"llm+rules"`.
- On **any** failure (no key, timeout of 25 seconds, bad JSON): return the rule-based suggestions with `extraction_mode: "rules"` and one warning. The user must never see a crash.
- `replay` provider: read answers from `data/replay/cache.json` keyed by a hash of the task and variables. **Nobody may write replay entries by hand**; they are recorded from real calls (Dev 3, task D7).
- Tests with a fake provider: success, failure (falls back), bad JSON (falls back), ungrounded quote (dropped), level 3 returned (capped to 2).

## 11. Never do

Never edit `engine/`, `data/v2/`, `contracts/`, or the frontend. Never add a package, framework, ORM or database. Never add or accept age, date of birth, gender or similar. Never put business logic in `main.py`. Never log personal text. Never commit `app.db`, `.env` or keys. Never change an endpoint path, field name or error code: if you believe the contract must change, tell Dev 4.

## Appendix: the full contract (do not change)

```python
"""CANONICAL CONTRACT v2.0. Single source of truth for every request and response. Frontend types, backend routes, fixtures and tests must match this file.
Rules: extra="forbid" everywhere (unknown fields are rejected); there is NO field for age, date of birth, gender or years of experience, anywhere.
Changing this file needs agreement from all four developers, then `make contracts` regenerates contracts/v2/openapi.yaml."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class S(BaseModel):
    model_config = ConfigDict(extra="forbid")

Interest = Literal["people", "data", "operations", "planning", "compliance"]
Style = Literal["progress", "goals", "encouragement", "accountability", "challenge"]
Band = Literal["strong_fit", "bridgeable", "stretch"]
Source = Literal["declared", "declared_alias", "extracted", "user_added"]
Signal = Literal["declared_only", "mentioned", "performed"]

# ---------- profile ----------
class DeclaredSkill(S):
    name: str = Field(min_length=1, max_length=80)
    level: int = Field(ge=1, le=3, description="1 Beginner, 2 Intermediate, 3 Advanced (the worker's own statement)")
class Preferences(S):
    interests: list[Interest] = Field(default_factory=list, max_length=3, description="Ordered, most wanted first")
    weekly_hours: Optional[int] = Field(default=None, ge=1, le=40)
class MotivationPrefs(S):
    styles: list[Style] = Field(min_length=1, max_length=2, description="1 or 2 styles the worker chose; first is primary")
    check_in: Literal["daily", "weekly", "off"] = "weekly"
    paused: bool = False
class ProfileCreate(S):
    display_name: str = Field(min_length=1, max_length=60)
    current_role: Optional[str] = Field(default=None, max_length=80)
    work_examples: list[str] = Field(min_length=1, max_length=5, description="Each 10..1000 chars, in the worker's own words")
    declared_skills: list[DeclaredSkill] = Field(default_factory=list, max_length=30)
    stated_goal_role_id: Optional[str] = Field(default=None, description="Role the worker says they want, e.g. R001. Always shown back to them.")
    preferences: Optional[Preferences] = None
    motivation: Optional[MotivationPrefs] = None
    consent: bool = Field(description="Must be true. Worker agrees to processing of the text they entered.")
class Profile(S):
    profile_id: str
    display_name: str
    current_role: Optional[str]
    work_examples: list[str]
    declared_skills: list[DeclaredSkill]
    stated_goal_role_id: Optional[str]
    preferences: Optional[Preferences]
    motivation: Optional[MotivationPrefs]
    created_at: str

# ---------- skills discovery and confirmation ----------
class Evidence(S):
    quote: str = Field(description="Verbatim substring of one of the worker's work examples")
    work_example_index: int = Field(ge=0)
class SkillSuggestion(S):
    suggestion_id: str
    skill_id: str
    name: str
    suggested_level: int = Field(ge=1, le=3)
    source: Source
    signal: Signal
    evidence: list[Evidence]
    explanation: str
class ExtractResponse(S):
    profile_id: str
    suggestions: list[SkillSuggestion]
    unmatched_declared: list[str] = Field(description="Declared skills with no scored equivalent; shown to the worker, not scored")
    extraction_mode: Literal["rules", "llm+rules"]
    warnings: list[str] = Field(default_factory=list)
class Decision(S):
    suggestion_id: str
    action: Literal["accept", "edit", "reject"]
    level: Optional[int] = Field(default=None, ge=1, le=3, description="Required when action is edit")
class AddedSkill(S):
    skill_id: str
    level: int = Field(ge=1, le=3)
class ConfirmRequest(S):
    decisions: list[Decision] = Field(description="Exactly one decision per suggestion")
    added_skills: list[AddedSkill] = Field(default_factory=list)
class ConfirmedSkill(S):
    skill_id: str
    name: str
    level: int = Field(ge=1, le=3)
    source: Source
    evidence: list[Evidence]
class ConfirmResponse(S):
    profile_id: str
    confirmed_skills: list[ConfirmedSkill]
    rejected_skill_ids: list[str]

# ---------- roles ----------
class FeatureScores(S):
    skill_coverage: float
    preference_fit: Optional[float] = Field(description="null when the worker gave no interests (feature dropped, weights renormalised)")
    learnability: float
class MatchedSkill(S):
    skill_id: str
    name: str
    user_level: int
    required_level: int
    coverage: float
    evidence_quotes: list[str]
class SkillGap(S):
    skill_id: str
    name: str
    required_level: int
    user_level: int
    gap_levels: int
    mandatory: bool
    importance: int
    est_hours: float
    priority: float
class RoleRecommendation(S):
    rank: int
    role_id: str
    title: str
    score: float
    band: Band
    feature_scores: FeatureScores
    weights_used: dict[str, float]
    blocking_gaps: list[str]
    matched: list[MatchedSkill]
    gaps: list[SkillGap]
    est_gap_hours: float
    openness_flags: list[str]
    explanation: str
    provisional_weights: bool = True
class RecommendationsResponse(S):
    profile_id: str
    recommendations: list[RoleRecommendation]
    goal: Optional[RoleRecommendation] = Field(description="The worker's stated goal role with its own analysis, even if it is not in the top ranks")
    disclaimer: str

# ---------- learning plan ----------
class Resource(S):
    resource_id: str
    title: str
    provider: str
    url: Optional[str]
    skill_ids: list[str]
    level_from: int
    level_to: int
    est_hours: Optional[float]
    duration_text: str
    cost: str
    verification_status: Literal["verified", "seed_unverified", "sample_placeholder"]
    last_verified: Optional[str]
    note: str
class PlanRequest(S):
    role_id: str
    weekly_hours: Optional[int] = Field(default=None, ge=1, le=40)
class PlanStep(S):
    order: int
    skill_id: str
    skill_name: str
    status: Literal["resource_found", "no_verified_resource"]
    resource: Optional[Resource]
    est_hours: float
    rationale: str
    builds_on: list[str]
class PlanResponse(S):
    plan_id: str
    profile_id: str
    role_id: str
    role_title: str
    total_est_hours: float
    weekly_hours: Optional[int]
    weeks_at_pace: Optional[int]
    steps: list[PlanStep]
    unresolved_skill_ids: list[str]
    includes_unverified_resources: bool
    disclaimer: str

# ---------- progress and motivation ----------
class ProgressUpdate(S):
    step_order: int = Field(ge=1)
    percent: int = Field(ge=0, le=100)
    hours_logged: Optional[float] = Field(default=None, ge=0, le=100)
class StepProgress(S):
    order: int
    skill_name: str
    est_hours: float
    percent: int
class NextMessage(S):
    message_id: str
    style: Style
    event: Literal["start", "step_done", "halfway", "behind", "welcome_back", "plan_done"]
    text: str
    suggested_action: Literal["none", "share_summary"]
class ProgressResponse(S):
    profile_id: str
    plan_id: str
    percent: int
    hours_done: float
    hours_total: float
    steps_done: int
    steps_total: int
    steps: list[StepProgress]
    last_activity_at: Optional[str]
    next_message: Optional[NextMessage]
class MessageFeedback(S):
    helpful: bool

# ---------- job-ad openness check ----------
class ReadinessRequest(S):
    text: str = Field(min_length=20, max_length=5000)
class ReadinessFlag(S):
    rule_id: str
    matched_text: str
    why: str
    suggestion: str
class ReadinessResult(S):
    status: Literal["flagged", "no_flags"]
    flags: list[ReadinessFlag]
    skills_first: bool
    limitations: list[str]

# ---------- bias audit ----------
class AuditRequest(S):
    canary: bool = Field(default=False, description="Demo only: add a deliberately biased variant to prove the audit can catch bias")
class AuditMetrics(S):
    skills_jaccard: float
    top3_overlap: int
    kendall_tau: float
    max_abs_score_delta: float
    plan_hours_delta: float
    lexicon_hits: int
class AuditFlag(S):
    variant_id: str
    metric: str
    observed: float
    threshold: float
    message: str
class AuditVariant(S):
    variant_id: str
    cue: str
    metrics: AuditMetrics
    flags: list[AuditFlag]
class ReviewRequest(S):
    reviewer: str = Field(min_length=1, max_length=60)
    decision: Literal["acknowledged", "override", "escalate"]
    note: Optional[str] = Field(default=None, max_length=500)
class AuditReview(S):
    reviewer: str
    decision: str
    note: Optional[str]
    reviewed_at: str
class AuditResult(S):
    audit_id: str
    profile_id: str
    status: Literal["pass", "flagged"]
    canary: bool
    variants: list[AuditVariant]
    thresholds: dict[str, float]
    limitations: list[str]
    review: Optional[AuditReview]
    created_at: str

# ---------- meta and errors ----------
class Meta(S):
    app_version: str
    contract_version: str
    mode: Literal["replay", "live"]
    extraction_mode: Literal["rules", "llm+rules"]
    weights: dict[str, float]
    weights_are_provisional: bool
    catalog: dict[str, int]
    resource_policy: dict[str, bool]
    disclaimers: list[str]
class ErrorBody(S):
    code: Literal["VALIDATION_ERROR", "FORBIDDEN_FIELD", "NOT_FOUND", "CONSENT_REQUIRED", "SKILLS_NOT_CONFIRMED", "NO_ACTIVE_PLAN", "INTERNAL"]
    message: str
    details: Optional[dict] = None
class ErrorResponse(S):
    error: ErrorBody
```
