# Career Orchestrator: Team Brief (everyone reads this first, about 10 minutes)

SAP Hackfest 2026, Theme 2: Inclusive Workforce. Team: The Creative Coders. **Deadline: Tuesday 3 November, 20:00 (our own choice). Finale: Wednesday 4 November.**

This brief is for the whole team. After it, each person reads their own brief (01 Frontend, 02 Backend, 03 Data/AI, 04 Integration). The full 44-page PRD is a reference; nobody needs to read all of it.

## 1. What we are building

An assistant that helps an experienced administrative worker in India move into a new role. The worker tells us what they do, in their own words. We suggest skills and show the exact words that support each one. The worker decides about every skill. We then show which roles fit and why, build a learning plan, track progress, and encourage the worker in the style they chose. A fairness check proves the system does not react to age.

The claim we make: **"The worker can see why a role fits, what is missing, and how to show readiness, and is helped to keep going in the way that suits them."**

It is a prototype. Numbers are provisional. Demo people are synthetic. We never promise jobs.

## 2. The journey (7 screens, 2 human gates)

1. Welcome: consent, and choose how you like to be encouraged.
2. Your work: write what you do, list skills you know, say your goal role.
3. Skill evidence review **(Gate 1)**: for every suggested skill, accept, edit or reject. The exact quote from the worker's text is shown.
4. Role matches: the worker's own goal first, then all roles ranked, each with reasons. The worker chooses a role **(Gate 2)**.
5. Learning plan: steps, hours, weeks. If no verified course exists, it says so.
6. My progress: percentage, and one message in the chosen style.
7. Fairness check (adviser): age-statement variants, a deliberately biased "canary", a human review.
A side page checks a job advert for non-skills-first wording.

The demo person is **Anitha Raman** (Administrative Coordinator who wants to be an HR Coordinator). Meera Nair and Kiran Patel are the other two demo people.

## 3. Who builds what

| Person | Role | Owns (only edit these) | Their brief |
|---|---|---|---|
| Dev 1 | Frontend | `frontend/` | 01_FRONTEND_BRIEF.md |
| Dev 2 | Backend | `backend/app/` | 02_BACKEND_BRIEF.md |
| Dev 3 | Data and AI | `engine/`, `data/v2/` (except `resources.json`) | 03_DATA_AI_BRIEF.md |
| Dev 4 | Integration | `tests/`, `.github/`, `docs/`, `data/v2/resources.json` | 04_INTEGRATION_BRIEF.md |

`contracts/v2/models.py` belongs to all four. **It is frozen.**

## 4. The architecture in one picture

```
Browser (frontend/)  --HTTP JSON /api/v1-->  Backend routes (backend/app/main.py)
                                                  |-- engine/  (calculations, no network, no database)
                                                  |-- SQLite app.db  (USER DATA ONLY)
                                                  '-- data/v2/*.json (roles, skills, courses: edited by humans, kept in Git)
```

- The frontend never calculates anything. It shows what the API returns.
- The engine never touches the network or the database.
- The database never holds roles, skills or courses.
- **A working backend already exists** (rules only, no AI key needed). Run it with `make run`.

## 5. Rules for everyone (non-negotiable)

1. **No age, date of birth, gender, graduation year or years of experience** anywhere. The API refuses such fields. The CSV column `years_experience` is never read.
2. **Two human gates.** Nothing is scored until the worker decides on every suggestion. No plan exists until the worker picks a role.
3. **Every skill has evidence (a verbatim quote from the worker's text) or the label "No supporting example yet".** Inference never gives level above 2. Only the worker can set level 3.
4. **Nobody invents courses, links, hours, statistics or job adverts.** A person opens the course page first. Only Dev 4 edits `data/v2/resources.json`.
5. **Every number is provisional and says so.** A score is not a hiring chance. Never write "guarantee", "will get hired" or "probability".
6. **Claim only what was tested.** SAP is "tested" only if someone ran it; otherwise "designed for".
7. **The contract is frozen.** To change a field, tell Dev 4. All four must agree. After Monday 22:00 no contract change is allowed.
8. **Business logic lives only in `engine/`.**
9. **No secrets in Git.** Keys go in a private `.env` file.
10. **Small tasks, tests after each, a person reads every AI-written change.**

## 6. Schedule (India time)

| When | What |
|---|---|
| **Sunday (today), first 2 hours** | Everyone: set up (section 8). Answer the gate questions in the group chat. Each person with SAP access does the 30-minute check in brief 04. |
| **Sunday, rest of day** | Everyone starts their first tasks (in their brief) |
| **Monday after 17:00** | Merge small, tested work. Call at **20:30**. **Features freeze 22:00**: only bug fixes after that |
| **Tuesday daytime** | Dev 4 integrates alone. Others are in class |
| **Tuesday 17:00 to 20:00** | Bug fixes only, rehearsals 1 and 2 |
| **Tuesday 20:00** | **DEADLINE.** Dev 4 tags `v2-demo`. No more code changes |
| **Tuesday 20:00 to 22:00** | Rehearsal 3 (offline), backup video |
| **Wednesday** | Finale |

**Gate questions to answer in the group today:** (a) Python 3.11+ installed and `make test` passes? (b) Result of your SAP check. (c) Which AI assistant do you use and do you have an API key? (d) Your class times.

**If time runs short, cut in this order:** job-advert check; fairness screen (keep the API); "was this helpful" feedback; accountability and challenge styles; interest preferences. **Never cut:** consent, the two gates, evidence quotes, the "your goal" display, the unverified labels, the disclaimers.

## 7. Working with AI assistants safely (we all use free plans)

AI assistants invent things, build too much, and break agreements. These habits stop that:

1. **One task per chat.** When the task is done, close the chat.
2. **Paste your role brief first**, then your task id. Do not paste anything else from the PRD.
3. **Ask for a plan before code.** Read the plan. If it touches files you do not own, say "stop".
4. **Run `make test` after every change.** Paste the result back to the AI. Never accept "done" without a passing test.
5. **Commit after every working step** so you can undo.
6. **Read the AI's code and ask it to explain each file in plain words.** You will explain your own part to the judges.
7. **Never paste keys or `.env`** into an AI.
8. If two AIs disagree, the contract file and the tests decide.

Prompt template for each task:

```
[paste your whole role brief here]
[paste contracts/v2/models.py here if your brief says so]

TASK: <task id and one sentence, copied from your brief>
DONE WHEN: <copy the "Done when" text>
FILES YOU MAY CHANGE: <list>
First reply with ONLY a plan (files and bullets). Do not write code until I say "go".
```

## 8. Setup (every developer, 10 minutes)

1. Install Python 3.11 or newer. Get the project folder (unzip, or clone the GitHub repository Dev 4 creates).
2. Open a terminal in the folder. Run: `make setup`
3. Run: `make test` . You must see **41 passed**. If not, tell Dev 4 before doing anything else.
4. Run: `make run` . Open `http://localhost:8000/docs` in a browser: every API call is listed and can be tried. Open `http://localhost:8000/` for the frontend starter page.
5. Optional: copy `.env.example` to `.env`. The app works without it.

Windows without `make`: ask Dev 4 for the equivalent commands, or use the cloud workspace.

## 9. How we work together

- **One folder, one owner.** Need a change in someone else's folder? Message them (or open an issue). Never edit it yourself.
- **Contract changes:** write down the field, the screen or function that needs it, and what breaks without it. Dev 4 asks all four. If anyone says no, it waits until after the demo.
- **Pull requests:** one task id per pull request. Describe what changed, assumptions, anything unfinished, how you tested. Dev 4 reviews.
- **Stuck for 30 minutes? Message the group.** None of us has done this before. Nobody struggles alone.
- **"Done" means:** `make test` is green, a person has read the code, and it is merged.

## 10. The API at a glance

Base path `/api/v1`. All data shapes are in `contracts/v2/models.py`. Every error has the same shape: `{"error": {"code": "...", "message": "...", "details": ...}}`.

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

Order of calls for the main journey: create profile, extract, confirm, recommendations, plan, progress. Calling out of order returns HTTP 409 with a code.

| Error code | HTTP | Meaning |
|---|---|---|
| `CONSENT_REQUIRED` | 400 | Consent was not given |
| `FORBIDDEN_FIELD` | 422 | A forbidden field (age, gender and similar) was sent |
| `VALIDATION_ERROR` | 422 | The request does not match the contract |
| `SKILLS_NOT_CONFIRMED` | 409 | Gate 1 has not been completed |
| `NO_ACTIVE_PLAN` | 409 | Gate 2 has not been completed |
| `NOT_FOUND` | 404 | Unknown profile, audit or message |
| `INTERNAL` | 500 | Unexpected error |

## 11. Words you may not know

**API**: web addresses the frontend calls to ask the backend for things. **Contract**: the agreed list of fields in every request and response (`contracts/v2/models.py`). **Engine**: the calculation code. **Rules mode**: the app works with fixed rules and no AI. **LLM**: an AI language model. **LLM key**: a secret code to use an LLM service; keep it private. **Gate**: a step where a person must decide. **Band**: strong fit, bridgeable or stretch. **Blocking gap**: a mandatory skill where the person has under half the required level. **Evidence**: the exact words from the worker that support a skill. **Canary**: a deliberately biased test case that proves our fairness check works. **Provisional**: a number we chose and have not validated. **CI**: automatic checks that run when you push. **Pull request**: a proposed change someone reviews before it is merged. **Tag**: a named, fixed version (`v2-demo`).
