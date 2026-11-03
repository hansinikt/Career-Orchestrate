# Career Orchestrator: Build Specification (PRD v2.0)

**SAP Hackfest 2026, Grand Finale, Theme 2: Inclusive Workforce** | Team: The Creative Coders | Version 2.0 | Prepared Sunday 1 November 2026 | Build deadline: Tuesday 3 November 2026, night (team decision) | Finale: Wednesday 4 November 2026

**What this document is.** It is the single source of truth for building the prototype in about two and a half working days with four first-time collaborators who use AI coding assistants on free plans. It replaces the 54-page v1 PRD for building purposes. The v1 PRD remains useful as a long-term roadmap and as the source for panel answers about what could be built later.

**What changed from v1, and why.** Each change responds to something the team told us.

| # | Change | Reason |
|---|---|---|
| 1 | Scope cut to one journey and three demo personas (Anitha, Meera, Kiran) | About 2.5 build days; teammates are in class 08:40-16:30 on Monday and Tuesday |
| 2 | Asynchronous workflow and polling replaced by simple request and response endpoints | Fewer moving parts for beginners; each step can be tested alone |
| 3 | The LLM is optional. The reference system works fully with no AI key (rules mode) | Free-tier AI limits; only some teammates have SAP access; the demo must not depend on a network service |
| 4 | Your CSV files become the catalogue (8 roles, 25 skills, 9 courses) | The team wrote them and the demo personas already exist in them |
| 5 | New module: Progress and Motivation (templates, no AI) | Team request: track progress and motivate each person in the way they prefer |
| 6 | Course accuracy policy: only people verify courses; unverified ones are labelled | Team concern: we cannot guarantee courses or recruiter value |
| 7 | A working reference backend and 41 passing tests are provided | So every developer can run the whole journey on day one |
| 8 | Practical proof task and AI-graded rubric moved to "designed next" | Research document calls it a differentiator, but an AI-graded score is the risk it warns about |
| 9 | Joule Studio, HANA vector search, Build Process Automation, Work Zone dropped from the build | Not needed for the prototype; Joule Studio is not in the tool list the team can reach |

**Evidence labels used throughout.**

| Label | Meaning |
|---|---|
| **[S]** | Supplied by the team: the research document, the SAP tools PDF, the CSV files, the screenshot, or what a team member told us |
| **[V]** | Verified by running code in this repository (tests, worked examples) or read from a source during v1 research |
| **[J]** | Engineering judgment: our reasoned choice, not a sourced fact. All scoring weights and thresholds are [J] and provisional |
| **[U]** | Unverified: must be checked by a named person before anyone relies on it |

**Reading guide.** Everyone reads Part A (sections 1 to 4) and section 13 for their own tasks. Frontend reads sections 4 and 8. Backend reads sections 5, 7, 8 and 9. Data/AI reads sections 6, 9, 10 and 11. Integration reads everything. Appendix A is the full contract.

**Companion files in the repository.** `contracts/v2/models.py` (the contract), `contracts/v2/openapi.yaml` (generated), `data/v2/` (catalogue and fixtures), `engine/` (the algorithms), `backend/app/` (reference backend), `tests/test_v2.py`, `AGENTS.md` (rules for AI assistants), `.env.example`, `Makefile`.

\newpage

# Part A: Product, rules, team and screens

## 1. Purpose, users and scope

### 1.1 The problem [S]

Experienced administrative and clerical workers in India (the research document says roughly ages 35 to 50) have valuable skills but struggle to translate them into terms employers recognise, to see which adjacent roles are realistic, to understand what is missing, and to show readiness. Career Orchestrator helps one worker at a time move from "what I do" to "what I can show" to "what I should learn next", with a human confirming every important step.

### 1.2 The one-sentence claim

"The worker can see why a role fits, what is missing, and how to show readiness, and is helped to keep going in the way that suits them." [S, adapted from the research document's conclusion]

### 1.3 Users

| User | What they do | What they never do |
|---|---|---|
| Worker | Enters work examples, confirms skills, picks a role, follows a plan, tracks progress | Is never ranked down for age or experience years |
| Adviser / reviewer | Looks at the fairness check, signs off or escalates flags | Does not reject candidates through this tool |
| Employer representative (demo role) | Pastes a job advert to see if wording is skills-first | Does not see any worker data |

### 1.4 What the prototype does (P0, must work)

1. Consent, then the worker chooses how they like to be encouraged (section 9.7).
2. The worker enters work examples (their own words) and lists skills they know.
3. The system suggests skills, each with the exact words from the worker's text that support it. The worker accepts, edits or rejects every suggestion. This is **Gate 1**.
4. The system ranks the 8 roles with a plain-language explanation, always showing the worker's own stated goal role with its own analysis even if it is not ranked first.
5. The worker picks a role. This is **Gate 2**. The system builds a learning plan from the course catalogue, marking any skill with no verified course as "no verified resource yet".
6. The worker tracks progress by step. The system shows a progress percentage and one message in the style they chose.
7. An adviser runs a fairness check (age-cue variants, plus an optional deliberately biased "canary") and signs off.
8. Anyone can paste a job advert and get a skills-first wording check.

### 1.5 Out of scope for the prototype

An AI-graded proof task, live job-vacancy data, enterprise single sign-on, SAP SuccessFactors integration, HANA vector search, SAP approval workflows, mobile apps, payments, and any automated decision about a person. These are "designed next" (section 16.3).

### 1.6 Demo personas [V]

The eight people in `user_profiles.csv` are synthetic and illustrative. Three are the demo set because they show the three bands.

| Persona | Stated goal | Result in the engine (confirmed skills only, no interests) | Why it is in the demo |
|---|---|---|---|
| Anitha Raman (U001) | HR Coordinator | Rank 1, bridgeable, 48 gap hours, one blocking gap: Confidentiality | The main story; her two inferred skills change the result |
| Meera Nair (U006) | Learning and Development Coordinator | Rank 1, strong fit (score 0.8529), 12 gap hours, no blocking gap | Shows a near-ready worker |
| Kiran Patel (U005) | Operations Analyst | Rank 4, stretch (score 0.2294), 84 gap hours, four blocking gaps | Shows an honest stretch, and that the goal is still shown |

### 1.7 Success criteria for the demo

| ID | Criterion | How we check |
|---|---|---|
| S1 | Anitha's full journey runs start to finish in under 5 minutes with no error | Manual checklist (section 15.3) |
| S2 | Every skill shown has the worker's own words as evidence, or is clearly labelled "no supporting example yet" | Automated test `test_evidence_is_grounded_and_inference_capped` |
| S3 | Sending an `age` field is refused | Automated test `test_forbidden_fields_rejected` |
| S4 | The fairness canary is flagged and the real variants are not | Automated test `test_audit_clean_pass_and_canary_flagged` |
| S5 | No course is shown as verified unless a person verified it | Automated test `test_catalog_consistency` |
| S6 | The demo runs on one laptop with no internet | Rehearsal 3 (section 15.3) |



## 2. Ground rules (non-negotiable)

These apply to every person and every AI assistant. They exist because beginners with AI assistants fail in predictable ways: building too much, inventing things, and writing code that does not connect.

| # | Rule | Enforced by |
|---|---|---|
| R1 | **No age, date of birth, gender, name-as-a-feature, graduation year or years of experience** in any model, function, prompt or screen. The CSV column `years_experience` is never read by any code | `extra="forbid"` on every model; `FORBIDDEN_FIELD` error; `test_contract_has_no_forbidden_fields` |
| R2 | **Two human gates.** Nothing is scored until the worker has decided on every suggestion (Gate 1). No plan exists until the worker picks a role (Gate 2) | `409 SKILLS_NOT_CONFIRMED`, `409 NO_ACTIVE_PLAN`; `test_gates` |
| R3 | **Every skill needs evidence or an honest label.** Evidence is a verbatim quote from the worker's own text, checked by code | `quote_is_grounded`; `test_evidence_is_grounded_and_inference_capped` |
| R4 | **Inference never exceeds "performed" (level 2).** Only the worker can set level 3 | Cap in `extract_rules.suggest` |
| R5 | **Nobody invents courses, URLs, hours, statistics or job postings.** A person opens the course page, then records it. `verified` requires a course-page URL and a date | `test_catalog_consistency`; AGENTS.md rule 3 |
| R6 | **Everything numeric is provisional and says so.** Weights, thresholds, hours per level and importance values are team judgment, labelled in the API (`provisional_weights`, `weights_are_provisional`) | `/meta`, every recommendation |
| R7 | **A match score is not a hiring probability.** The disclaimer text in section 12.4 appears wherever a score appears | Frontend rule F5 |
| R8 | **Claim only what was tested.** SAP is described as "tested" only if someone ran it; otherwise "designed for" | Section 17; demo slide in section 16.2 |
| R9 | **The contract is frozen.** Only `contracts/v2/models.py` defines data shapes. Changes need all four developers to agree | CODEOWNERS; CI `contracts-check` |
| R10 | **Business logic lives only in `engine/`.** The frontend displays what the API returns | Frontend rule F2 |
| R11 | **The catalogue lives in Git, user data lives in SQLite.** The database never holds roles, skills or courses | Section 7 |
| R12 | **Small tasks, tests after each, human review of every AI-written change** | AGENTS.md; section 14 |
| R13 | **The demo works offline.** Rules mode and the built frontend run on one laptop | Section 5.5 |
| R14 | **No secrets in Git.** Keys live in `.env` | `.gitignore`; AGENTS.md rule 6 |



## 3. Team, constraints and schedule

### 3.1 Team and roles [S]

| Dev | Role | Name | Owns | Has SAP access |
|---|---|---|---|---|
| Dev 1 | Frontend | ________ | `frontend/` | ____ |
| Dev 2 | Backend | ________ | `backend/app/` | ____ |
| Dev 3 | Data and AI (agent building and management) | ________ | `engine/`, `data/v2/` except `resources.json` | ____ |
| Dev 4 | Integration | ________ | `tests/`, `.github/`, `docs/`, `data/v2/resources.json`, demo | Yes |

Team members: Ravva Sai Charan, Sri Durgaa, Sai Hansini K, Sara Vaivswat. The team has told us three people now have SAP access, from the organisers [S]. Each person must still test their own access (section 17).

### 3.2 Constraints [S]

- This is the team's first collaboration and first project of this kind. Everyone is new.
- AI assistants run on free plans or a personal Pro plan. We treat usage limits as real and unknown [U].
- Monday: everyone is busy 08:40 to 16:30. Tuesday: Dev 4 is free all day; Devs 1 to 3 are busy 08:40 to 16:30.
- The 3 November deadline is the team's own choice, not set by the organisers. The finale is Wednesday 4 November; its time is not yet known [U].
- Times in this document are India Standard Time (IST) [J].

### 3.3 Schedule

| When | Who | What | Done means |
|---|---|---|---|
| **Sunday (today), first 2 hours** | All | Decisions G0 below; repo created; each person tests their SAP access (30 minutes); reference backend running on at least two laptops | Checklist G0 ticked |
| **Sunday, rest of day** | Dev 1 | Screens 1 to 3 working against the running backend | Screens call the API and show real data |
| | Dev 2 | Read and run the reference backend; fix anything wrong; add deployment notes | `make test` green on their machine |
| | Dev 3 | Review aliases and role tags; start the course search list (section 11) | Aliases reviewed; list of 10 skills to source |
| | Dev 4 | Repo, CI, CODEOWNERS, contract frozen at v2.0, send team message | CI green; contract frozen |
| **Monday after 17:00** | Devs 1 to 3 | Merge small, tested work: Dev 1 screens 4 to 6; Dev 2 hardening; Dev 3 courses and message review | Each task id in section 13 closed or cut |
| **Monday 20:30** | All | 30-minute call: demo what works; decide what is cut | Cut list agreed |
| **Monday 22:00** | All | **Feature freeze.** Only bug fixes from now | Anything not working end to end is cut |
| **Tuesday daytime** | Dev 4 | Integration alone: run full journey, fix seams, add verified courses, build frontend into `frontend_dist`, record notes | Checklist 15.3 passes |
| **Tuesday 17:00 to 20:00** | All | Bug fixes only; rehearsal 1 and 2 | No open P0 bugs |
| **Tuesday 20:00** | All | **Deadline.** Tag `v2-demo`. No more code changes | Tag exists |
| **Tuesday 20:00 to 22:00** | All | Rehearsal 3 (offline), record backup video | Video file saved in two places |
| **Wednesday** | All | Finale. Polish of talk only. If the demo breaks, restore tag `v2-demo` | |

### 3.4 Gates (decide and write the answer in the group chat)

| Gate | Question | Owner | When | If "no" |
|---|---|---|---|---|
| G0a | Does a frontend already exist? What technology? | Dev 1 | Sunday, first 2 hours | Build a minimal new one (section 4.7) |
| G0b | Is Python 3.11 or newer installed on at least two laptops? | Dev 2 | Sunday, first 2 hours | Use the cloud workspace or install it today |
| G0c | Contract v2.0 accepted? | All | Sunday, first 2 hours | Dev 4 resolves objections before anyone codes |
| G1 | SAP check: can a model be called from AI Launchpad and a service key created? | Each SAP user | Sunday night | Skip SAP model; say "designed for" |
| G2 | Does anyone have a usable LLM key (any provider)? | All | Sunday night | Rules mode only; LLM is "designed next" |
| G3 | Are at least 3 courses verified by a person? | Dev 4 | Tuesday 14:00 | Ship "no verified resource yet" as a feature |

### 3.5 Kill-list (cut in this order when time runs short)

1. Role openness check screen (section 9.8)
2. Fairness check screen (keep the API; show the result as a table)
3. Style rotation and "was this helpful" feedback
4. Accountability and challenge styles (keep progress, goals, encouragement)
5. Interest preferences (the engine already handles their absence)
6. Switching of target role after the plan exists

Never cut: consent, Gate 1, Gate 2, evidence quotes, the stated-goal display, the unverified labels, the disclaimers.



## 4. Screens and the frontend rules

### 4.1 Frontend rules

| # | Rule |
|---|---|
| F1 | All network calls go through ONE file (`frontend/src/api.*`). It reads the base URL from one config value. Screens never call `fetch` directly |
| F2 | The frontend never computes scores, bands, hours, percentages or messages. It displays the API's fields exactly |
| F3 | Every screen has four states: loading, empty, error, success. Errors show `error.message` from the API in plain words and a "Try again" button |
| F4 | Show `provisional_weights`, `weights_are_provisional` and `includes_unverified_resources` where the screens below say so |
| F5 | Wherever a score or band is shown, show the disclaimer from `/meta` (`disclaimers[0]`) |
| F6 | Keep all visible text in one file so it can be translated later (English, Hindi, Telugu appear in the data) [J] |
| F7 | Plain words, 16px minimum body text, large touch targets, strong contrast, no jargon ("skills" not "taxonomy", "step" not "node") |
| F8 | Store only `profile_id` in the browser (so a refresh resumes). Never store the work text in the browser |
| F9 | Never put a key or secret in frontend code |
| F10 | Never use the words "guarantee", "will get", "hired" or "probability" in any text |
| F11 | A resource whose `verification_status` is not `verified` shows a visible badge: "Not yet verified. Check the course page" (or "Sample") |

### 4.2 Screen map

![Screen flow and gates](diagrams/v2_flow.png)

### 4.3 Screen specifications

**Screen 1: Welcome, consent and encouragement style.** Purpose: explain in two sentences what the tool does and does not do; get consent; get the style. Calls: none until submit; `GET /api/v1/meta` on load to show disclaimers. Fields: consent checkbox (required, unchecked by default), motivation style (choose 1 or 2 of: Progress, Goals, Encouragement, Accountability, Challenge, each with a one-line example from section 9.7), check-in (daily, weekly, off), a pause switch. Validation: the Continue button is disabled until consent is ticked and at least one style is chosen. Copy rules: say the styles can be changed any time.

**Screen 2: Your work.** Purpose: collect the worker's own words and skills. Calls: `POST /api/v1/profiles`, then `POST /api/v1/profiles/{id}/extract`. Fields: display name; current role (optional); 1 to 5 work examples (10 to 1000 characters each); skills you know (name plus level Beginner/Intermediate/Advanced, up to 30); goal role (dropdown from `GET /api/v1/roles`, optional); weekly study hours (1 to 40, optional); interests (up to 3 of people, data, operations, planning, compliance, optional). There must be NO age, date of birth or gender field. A "Use a demo person" button fills the form from `GET /api/v1/demo/personas` and is labelled "synthetic".

**Screen 3: Skill evidence review (Gate 1).** Purpose: the worker decides on every suggestion. Data: `suggestions` from the extract response. Each card shows: skill name; suggested level as words (Beginner, Intermediate, Advanced); the `explanation`; each `evidence.quote` shown in quotation marks with its work example number; if `evidence` is empty, the label "No supporting example yet"; a badge for `source` (You listed it / We matched your wording, please confirm / Found in your work). Actions per card: Accept, Edit level, Reject. All cards need a decision before Continue is enabled. Also show `unmatched_declared` under "Skills we could not match yet" (not scored) and an "Add a skill" control (from `GET /api/v1/skills`). Submit calls `POST /api/v1/profiles/{id}/confirm`.

**Screen 4: Role matches.** Calls: `GET /api/v1/profiles/{id}/recommendations`. Top card: "Your goal: {goal.title}" with its band, gap hours, blocking gaps and explanation, even if it is not top-ranked. Then the ranked list: for each role, title, band label (Strong fit, Bridgeable, Stretch), `explanation`, a "Why" panel listing `matched` skills with their evidence quotes and `gaps` with hours, and the `blocking_gaps` named. Show the disclaimer (F5). A "Choose this role" button on each card is Gate 2. Do not show a percentage as a hiring chance. The `score` may be shown as "match score (provisional)" or hidden; the band and the reasons are what matter.

**Screen 5: Learning plan.** Calls: `POST /api/v1/profiles/{id}/plan` with `role_id` and optional `weekly_hours`. Shows: total hours, weeks at the chosen pace, each step with skill, rationale, hours, and either the resource (title, provider, duration text, link opening in a new tab, verification badge per F11) or the label "No verified resource yet. Ask your adviser or search for a course on this skill" for `no_verified_resource`. Shows the `disclaimer`. A button "Start my plan" goes to Screen 6.

**Screen 6: My progress.** Calls: `GET /api/v1/profiles/{id}/progress`, `POST /api/v1/profiles/{id}/progress`, `POST /api/v1/profiles/{id}/messages/{mid}/feedback`, `PUT /api/v1/profiles/{id}/motivation`. Shows: percentage bar, hours done of total, steps done of total, a list of steps each with a 0 to 100 slider or buttons (Not started, Started, Half, Done), and the `next_message` text in a friendly card. If `suggested_action` is `share_summary`, show a "Copy my summary" button (frontend builds text from the data on screen). Under each message: "Helpful" and "Not helpful" buttons. A settings link changes the style, check-in and pause.

**Screen 7: Fairness check (adviser).** Calls: `POST /api/v1/profiles/{id}/audit` (with `{"canary": true}` for the demo), `POST /api/v1/audits/{id}/review`. Shows: status (Pass or Flagged), a table of variants (id, cue, the six metrics, any flags in words), the `limitations` list, and a review form (reviewer name, decision acknowledged / override / escalate, note). The page title says "Fairness check (adviser view)". Text under the table: "This checks the variants listed. It does not prove the system is free of bias."

**Role openness check (side page).** Calls: `POST /api/v1/readiness/check`. A text box for a job advert (20 to 5000 characters) and a result list of flags (matched text, why, suggestion), or "No flags found. This does not prove the role is fair."

### 4.4 State and navigation rules

The order is fixed: 1, 2, 3, 4, 5, 6. If the user jumps ahead, the API returns `409` with a code and a message; show the message and a button to the missing step. After Gate 1 is submitted again (the worker changes their mind), the old plan is deactivated by the backend; Screen 5 will then need a new plan.

### 4.5 Error handling

Every error has this shape: `{"error": {"code": "...", "message": "...", "details": ...}}`. Handle by `code`:

| Code | HTTP | What the frontend does |
|---|---|---|
| `CONSENT_REQUIRED` | 400 | Return to Screen 1 with the message |
| `FORBIDDEN_FIELD` | 422 | Developer error: the form sent a forbidden field. Show the message and fix the form. Never reach this in production |
| `VALIDATION_ERROR` | 422 | Show `message`; if `details.errors` exists, highlight the named fields |
| `SKILLS_NOT_CONFIRMED` | 409 | Go to Screen 3 |
| `NO_ACTIVE_PLAN` | 409 | Go to Screen 5 |
| `NOT_FOUND` | 404 | Profile expired or deleted: clear `profile_id`, return to Screen 1 |
| `INTERNAL` | 500 | "Something went wrong. Nothing was lost. Try again." plus a Try again button |

### 4.6 How the frontend connects to the backend and the database

The frontend never talks to the database. The chain is: screen, then `api` file, then HTTP to the backend routes, then the engine (calculations) and `db.py` (storage), then SQLite. Section 5 shows the picture and section 8 lists every call.

For local development, run the backend (`make run`, port 8000) and the frontend dev server (its own port). The backend accepts calls from any origin in development (`CORS_ORIGINS=*`). The base URL is `http://localhost:8000/api/v1`; it must be a single config value so it can change on demo day.

For the demo, build the frontend and copy the build into a folder called `frontend_dist` at the repository root. The backend then serves the pages itself at `http://localhost:8000/` and the API at `/api/v1`, so there is one process, one address, no CORS, and no second server to forget to start.

### 4.7 If there is no existing frontend (or Dev 1 decides to replace it)

Build the smallest thing that follows sections 4.1 to 4.5: a single-page app with seven views and one `api` file. Any technology the developer already knows is acceptable; do not learn a new framework this week [J]. If the choice is open, plain HTML with JavaScript `fetch` is the least risky for a beginner; a component framework is acceptable if the developer already uses one. Types for the API can be written by hand from Appendix A, or generated from `contracts/v2/openapi.yaml` with a tool the developer already trusts.

### 4.8 If an existing frontend exists

Do not rewrite it. Add an adapter: create the one `api` file, map the existing forms to the fields in Appendix A, and remove any code that computes scores or invents data. Add the missing screens (3, 6, 7) in the existing style. Dev 1 reports the inventory (technology, pages, where mock data lives) at gate G0a.
