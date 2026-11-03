# Career Orchestrator: FRONTEND BRIEF (Dev 1)

{{PREAMBLE}}

Paste this whole brief into your AI assistant at the start of each chat, then your task id (F1 to F9, section 9). Also paste `frontend/api.js` when the task uses it.

## 1. Your mission

Build the seven screens and one side page of Career Orchestrator as a small website using **plain HTML, CSS and JavaScript (ES modules)**. No framework, no npm, no build step. The backend already works and serves your files, so you can see your changes by refreshing the browser.

Your whole job is to **show what the API returns and send what the user entered**. You never calculate scores, bands, hours, percentages or messages.

## 2. Files

Already in `frontend/` (a tested starter):

| File | Status | Purpose |
|---|---|---|
| `index.html` | starter | Page shell with navigation, `<main id="app">`, and a footer that shows the disclaimer |
| `app.js` | starter | Router by `location.hash` (`#/1` to `#/7`, `#/openness`) with empty stub screens |
| `config.js` | done | Sets the backend address in ONE place |
| `api.js` | **done and tested; do not edit** | One function per API call. The only file that uses `fetch` |
| `strings.js` | starter | ALL visible text. Add new text here, never inside screens |
| `styles.css` | starter | Plain readable styles (16px text, large buttons) |

You create: `frontend/screens/screen1.js` ... `screen7.js`, `screen_openness.js`. Each exports one function that returns the HTML for that screen (or fills `#app`) and wires its buttons. Replace the stubs in `app.js` one at a time.

## 3. Run it

```
make setup     (first time only)
make run       then open http://localhost:8000/   (API docs: http://localhost:8000/docs)
```
Edit files and refresh. The backend serves `frontend/` automatically. For the final demo Dev 4 copies the folder to `frontend_dist/`.

## 4. How `api.js` works (already written)

Import it: `import { api, ApiError } from "./api.js";`. Every function returns the parsed JSON, or `null` for HTTP 204. On any failure it **throws an `ApiError`** with `error.code`, `error.message`, `error.details`, `error.status`. Codes are the backend codes in section 8 plus two client-only codes: `NETWORK` (cannot reach server) and `TIMEOUT` (over 15 seconds).

| Function | Call | Notes |
|---|---|---|
| `api.meta()` | GET /meta | `disclaimers[0]` is the score disclaimer; `weights_are_provisional` |
| `api.roles()` | GET /roles | `{ roles: [{ role_id, title, summary, family, tags, data_note, requirements: [{ skill_id, name, required_level, mandatory }] }] }` |
| `api.skills()` | GET /skills | `{ skills: [{ skill_id, name, category }] }` (only scored skills) |
| `api.demoPersonas()` | GET /demo/personas | `{ synthetic: true, personas: [{ persona_id, display_name, current_role, work_examples, declared_skills, stated_goal_role_id }] }` |
| `api.createProfile(body)` | POST /profiles | body = ProfileCreate (section 5) |
| `api.getProfile(id)` / `api.deleteProfile(id)` | GET / DELETE /profiles/{id} | delete returns `null` |
| `api.extract(id)` | POST /profiles/{id}/extract | no body |
| `api.confirm(id, body)` | POST /profiles/{id}/confirm | body = ConfirmRequest |
| `api.recommendations(id)` | GET /profiles/{id}/recommendations | |
| `api.makePlan(id, { role_id, weekly_hours })` | POST /profiles/{id}/plan | `weekly_hours` optional |
| `api.getPlan(id)` | GET /profiles/{id}/plan | |
| `api.setMotivation(id, { styles, check_in, paused })` | PUT /profiles/{id}/motivation | |
| `api.getProgress(id)` / `api.updateProgress(id, { step_order, percent, hours_logged })` | GET / POST /profiles/{id}/progress | |
| `api.messageFeedback(id, messageId, true/false)` | POST /profiles/{id}/messages/{mid}/feedback | returns `null` |
| `api.readinessCheck(text)` | POST /readiness/check | |
| `api.startAudit(id, canary)` | POST /profiles/{id}/audit | `canary` true adds the biased test case |
| `api.getAudit(auditId)` / `api.reviewAudit(auditId, body)` | GET / POST /audits/{id}[/review] | |

## 5. Data shapes you send (exact field names; extra fields are rejected)

**ProfileCreate** (Screen 2 submit). All keys below; no other keys are allowed.

```json
{{FIX:01_profile_create_request:6}}
```

Limits: `display_name` 1 to 60 chars. `current_role` optional. `work_examples`: 1 to 5 items, each 10 to 1000 chars. `declared_skills`: up to 30 items, `level` is 1, 2 or 3 (1 Beginner, 2 Intermediate, 3 Advanced). `stated_goal_role_id` optional, one of `R001` to `R008`. `preferences.interests`: up to 3 of `people`, `data`, `operations`, `planning`, `compliance`; `preferences.weekly_hours`: 1 to 40 or null. `motivation.styles`: 1 or 2 of `progress`, `goals`, `encouragement`, `accountability`, `challenge`; `motivation.check_in`: `daily`, `weekly` or `off`; `motivation.paused`: true or false. **`consent` must be `true`** (the checkbox).

To fill the form with a demo person: take one object from `api.demoPersonas()`, remove `persona_id`, rename nothing else, add `consent`, `preferences` and `motivation`.

**ConfirmRequest** (Screen 3 submit): exactly one decision per suggestion.

```json
{{FIX:04_confirm_request:6}}
```
`action` is `accept`, `edit` (then `level` 1 to 3 is required) or `reject`. `added_skills` is a list of `{ "skill_id", "level" }` chosen from `api.skills()`.

**PlanRequest** (Screen 5): `{ "role_id": "R001", "weekly_hours": 6 }` (`weekly_hours` optional).
**ProgressUpdate** (Screen 6): `{ "step_order": 1, "percent": 40 }` (`percent` 0 to 100; `hours_logged` optional).
**MotivationPrefs** (Screen 6 settings): `{ "styles": ["progress", "goals"], "check_in": "weekly", "paused": false }`.
**ReviewRequest** (Screen 7): `{ "reviewer": "Name", "decision": "acknowledged" | "override" | "escalate", "note": "optional" }`.

## 6. Data shapes you receive (real output; long lists are shortened with "... n more")

**Profile** after create (keep only `profile_id`; see rule F8):
```json
{{FIX:02_profile:6}}
```

**Extract response** (Screen 3). `suggestions[]` has `suggestion_id`, `skill_id`, `name`, `suggested_level` (1 to 3), `source` (`declared`, `declared_alias`, `extracted`, `user_added`), `signal` (`declared_only`, `mentioned`, `performed`), `evidence[]` (`quote`, `work_example_index`), `explanation`. `unmatched_declared` is a list of names that could not be scored.
```json
{{FIX:03_extract_response:3}}
```

**Recommendations** (Screen 4). `recommendations` is the ranked list; `goal` is the worker's own stated goal with the same fields (or `null` if none was set). `blocking_gaps` holds **skill ids**: get the names from the `gaps` array (same `skill_id`).
```json
{{FIX:06_recommendations:1}}
```

**Plan** (Screen 5). A step has `status` `resource_found` (then `resource` is an object) or `no_verified_resource` (then `resource` is `null`). `resource.verification_status` is `verified`, `seed_unverified` or `sample_placeholder`.
```json
{{FIX:08_plan_response:3}}
```

**Progress** (Screen 6). `next_message` is `null` when no message applies.
```json
{{FIX:10_progress_response:3}}
```

**Audit** (Screen 7). Each variant has six `metrics` and a `flags` list (empty when fine).
```json
{{FIX:12_audit_canary:2}}
```

**Job advert check** (side page):
```json
{{FIX:13_readiness:4}}
```

## 7. Rules (check every screen against these)

| # | Rule |
|---|---|
| F1 | All network calls go through `api.js`. Never write `fetch` in a screen |
| F2 | Never calculate scores, bands, hours, percentages or messages. Display the API's fields exactly |
| F3 | Every screen handles four states: loading, empty, error, success. Errors show `error.message` and a "Try again" button |
| F4 | Show a "provisional" note wherever weights or scores appear; show a note if `includes_unverified_resources` is true |
| F5 | Wherever a score or band appears, show the disclaimer (`meta.disclaimers[0]`) |
| F6 | All visible text lives in `strings.js` |
| F7 | Plain words. 16px minimum text. Large buttons. Strong contrast. No jargon ("skills", not "taxonomy"; "step", not "node") |
| F8 | Store only `profile_id` in the browser (`setProfileId` in `app.js`). Never store the work text, skills or results |
| F9 | No keys or secrets in frontend code |
| F10 | Never write "guarantee", "will get", "hired" or "probability" in any text |
| F11 | A course whose `verification_status` is not `verified` shows a visible badge (`T.badgeUnverified` or `T.badgeSample`) |
| F12 | **There is no age, date of birth or gender field anywhere in the UI or in anything sent** |
| F13 | Insert user text with `textContent` (or escape it). Never put text from the worker or the API into `innerHTML` unescaped |

## 8. Errors: what to do for each code

| `error.code` | What the screen does |
|---|---|
| `CONSENT_REQUIRED` | Go to Screen 1 and show the message |
| `FORBIDDEN_FIELD` | A bug in the form: show the message; remove the field |
| `VALIDATION_ERROR` | Show `message`; if `details.errors` exists, point at the named fields |
| `SKILLS_NOT_CONFIRMED` | Go to Screen 3 |
| `NO_ACTIVE_PLAN` | Go to Screen 5 |
| `NOT_FOUND` | Call `setProfileId(null)` and go to Screen 1 |
| `INTERNAL`, `NETWORK`, `TIMEOUT` | Show `message` and a "Try again" button |

## 9. The screens (exact specification)

Fixed order: 1, 2, 3, 4, 5, 6. Screen 7 and the side page are separate.

### Screen 1: Welcome, consent, encouragement style
- Calls: `api.meta()` on load (show `disclaimers` in a small note).
- Inputs: consent checkbox (`T.consentLabel`, unchecked by default); choose 1 or 2 styles from the five (label `T.styles[x]`, help `T.styleHelp[x]`); check-in `daily`/`weekly`/`off`; pause switch.
- Continue is disabled until consent is ticked AND at least one style is chosen. Keep the choices in memory and send them with Screen 2's create call.
- Text to show: one short paragraph: "This tool helps you see which roles fit your real work and what to learn next. You decide at every step. It does not promise jobs." (add it to `strings.js`).

### Screen 2: Your work
- Fields: display name (required); current role (optional); 1 to 5 work-example boxes (10 to 1000 chars each; show a counter; "Add another example" up to 5); "skills you know" rows (name + Beginner/Intermediate/Advanced, up to 30); goal role (dropdown from `api.roles()`, optional); weekly study hours (optional number 1 to 40); interests (optional, up to 3 of the five tags).
- Button "Use a demo person (synthetic)": fills the form from `api.demoPersonas()` (see section 5).
- Submit: `api.createProfile(...)` then `setProfileId(profile.profile_id)` then `api.extract(profile_id)` then go to Screen 3. Show a spinner during both calls.
- **No age, date of birth or gender field.**

### Screen 3: Skill evidence review (Gate 1)
- Needs the extract response. If you arrive without it, call `api.extract(profileId)` again.
- For each item in `suggestions` show a card: skill `name`; level in words (`T.levels[suggested_level]`); `explanation`; a badge from `T.sourceBadge[source]`; each `evidence[].quote` in quotation marks with "From your example {work_example_index + 1}"; if `evidence` is empty show `T.noEvidence`.
- Each card has three choices: Accept, Edit (a Beginner/Intermediate/Advanced picker), Reject. **Continue is disabled until every card has a choice.**
- Below the cards: list `unmatched_declared` under "Skills we could not match yet (not scored)"; an "Add a skill" dropdown from `api.skills()` with a level.
- Submit builds ConfirmRequest (section 5) then calls `api.confirm`, then goes to Screen 4. A worker who goes back and re-confirms gets a new result.

### Screen 4: Role matches (Gate 2)
- Call `api.recommendations(profileId)`.
- Top card "Your goal: {goal.title}" using `goal` (band label `T.bands[band]`, `est_gap_hours`, names of blocking gaps, `explanation`). If `goal` is null, skip it. The goal card is shown even when that role is ranked low.
- Then every role in `recommendations` (already ranked): title, band label, `explanation`, and a "Why" section that opens to show `matched` (name, user level vs required level in words, and `evidence_quotes`) and `gaps` (name, hours, "required" if `mandatory`). List blocking gaps by name.
- Show the disclaimer (F5). Show the score only as "match score (provisional)", in small text, or not at all. The band and the reasons are what matter.
- Each card has "Choose this role" (Gate 2): store the `role_id` and go to Screen 5.

### Screen 5: Learning plan
- Call `api.makePlan(profileId, { role_id, weekly_hours })` (use the weekly hours the worker entered, or leave it out).
- Show `role_title`, `total_est_hours`, `weeks_at_pace` ("about N weeks at {weekly_hours} hours a week"; if null, say "Enter your weekly hours to see a timeline").
- Each step: skill name, `rationale`, `est_hours`; if `resource` exists show title, provider, `duration_text`, the link (`url`, opens in a new tab) and the badge by `verification_status` (F11), plus "Verified {last_verified}" when verified; if `status` is `no_verified_resource` show `T.noResource`.
- Show `disclaimer`. If `includes_unverified_resources` is true, make that note prominent.
- Button "Start my plan" goes to Screen 6.

### Screen 6: My progress
- Call `api.getProgress(profileId)`. If it returns `NO_ACTIVE_PLAN`, go to Screen 5.
- Show a progress bar from `percent`; "{hours_done} of {hours_total} hours"; "{steps_done} of {steps_total} steps".
- For each item of `steps`: skill name and four buttons (Not started = 0, Started = 25, Half = 50, Done = 100). Clicking calls `api.updateProgress(profileId, { step_order: order, percent })` and re-draws from the response.
- If the response `next_message` is not null show `text` in a friendly card. Under it "Helpful" / "Not helpful" call `api.messageFeedback`. If `suggested_action` is `share_summary`, show a "Copy my summary" button that copies a short text built from what is on screen.
- Settings link: change styles, check-in and pause with `api.setMotivation`.
- Do not invent your own motivational text. Only show `next_message.text`.

### Screen 7: Fairness check (adviser view)
- Title: "Fairness check (adviser view)". Buttons: "Run check" (`api.startAudit(profileId, false)`) and "Run with biased test case" (`api.startAudit(profileId, true)`).
- Show `status` (Pass / Flagged) clearly. Table of `variants`: `variant_id`, `cue`, the six `metrics`, and each `flags[].message` in words. Highlight rows that have flags.
- Show every `limitations` item and `T.fairnessNote`.
- Review form: reviewer name, decision (acknowledged / override / escalate), note, then `api.reviewAudit`. After success show the returned `review`.

### Side page: Job advert check
- A textarea (20 to 5000 chars) and a button calling `api.readinessCheck(text)`. Show each flag: `matched_text`, `why`, `suggestion`. If `status` is `no_flags` show `T.opennessNone`.

## 10. Tasks (one per AI chat)

| ID | Pri | Task | Done when |
|---|---|---|---|
| F1 | P0 | Run the backend and the starter page; click every link; try `api.meta()` in the browser console; write down anything unexpected | A short note posted to the group |
| F2 | P0 | Read `api.js` and explain each function to the group. Add a small debug page `#/debug` that calls `meta`, `roles`, `skills`, `demoPersonas` and prints the results | Debug page works |
| F3 | P0 | Screens 1 and 2 | Anitha can be created from the form; no age field exists |
| F4 | P0 | Screen 3 | Every card shows quotes or the no-evidence label; Continue disabled until all decided |
| F5 | P0 | Screen 4 | Anitha: HR Coordinator shows "Bridgeable", blocking gap "Confidentiality", about 24 hours |
| F6 | P0 | Screen 5 | Anitha's plan shows 24 hours, 4 weeks and "No verified resource yet" |
| F7 | P0 | Screen 6 | Setting step 1 to 25 or more shows a message |
| F8 | P1 | Screen 7 and the side page | Biased case shows Flagged; normal check shows Pass |
| F9 | P0 | Plain-words pass; check rules F1 to F13; test on a phone-sized window | Section 11 checklist passes |

## 11. What to expect with Anitha (use this to test)

Create Anitha with the demo-person button, interests empty, weekly hours 6, motivation Progress and Encouragement.

| Step | You should see |
|---|---|
| Screen 3 | Five suggestions: Communication (Advanced), Excel (Intermediate, **no supporting example yet**), Record management (Advanced) listed by her; Reporting and Scheduling (Intermediate) found in her work, with the quotes "prepared reports" and "Coordinated calendars" |
| Screen 4 | Goal: HR Coordinator, Bridgeable, blocking gap Confidentiality, about 24 hours. Ranking: HR Coordinator, Project Coordinator, Learning and Development Coordinator |
| Screen 5 | 24 hours; 4 weeks at 6 hours a week; one step "Confidentiality" with "No verified resource yet" |
| Screen 6 | Set step 1 to Started (25): a message in the Progress style: "You have begun. Your plan has 1 step and about 24 hours in all. 25% done so far." Set it to Done: an Encouragement message about finishing the plan |
| Screen 7 | Normal check: Pass. Biased case: Flagged, with the CANARY row showing flagged metrics |
| Job advert | "Freshers wanted. Up to 3 years of experience. Energetic team player." gives three flags |

## 12. Never do

Never add a framework or library. Never call the backend except through `api.js`. Never compute a score, band, percentage or message. Never store work text in the browser. Never write your own motivational text, course names, links or numbers. Never add an age, date of birth or gender input. Never change `api.js` field names or the backend. If you need a field the API does not return, tell Dev 4; do not invent one.

## Appendix: the full contract (do not change; shapes of every request and response)

```python
{{FILE:contracts/v2/models.py}}
```
