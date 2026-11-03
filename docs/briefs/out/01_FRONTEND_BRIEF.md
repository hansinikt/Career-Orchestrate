# Career Orchestrator: FRONTEND BRIEF (Dev 1)

=== INSTRUCTIONS FOR THE AI ASSISTANT (read this first, follow it exactly) ===
You are helping ONE developer on the FRONTEND part of "Career Orchestrator", a hackathon prototype built by four first-time collaborators.
This brief is your ONLY source of truth. Rules:
1. Use only what is written in this brief and in files the developer pastes into the chat. If something is not specified, reply "Not specified in the brief" and ask the developer. Never guess.
2. Never invent: API endpoints, field names, status codes, library or package names, file names, course names, web links, statistics, or job adverts.
3. Never add or use age, date of birth, gender, graduation year, or years of experience, anywhere (code, data, screens, prompts, tests).
4. Allowed technology: plain HTML, CSS and JavaScript (ES modules) only. No npm, no frameworks (React, Vue, Angular and similar), no build tools, no CSS frameworks, no scripts loaded from the internet.
5. Files you may create or change: everything inside frontend/ (index.html, app.js, config.js, strings.js, styles.css, screens/*.js). api.js is finished: change it only if the contract changes. Never change any other file.
6. Work on ONE task at a time. The developer will name a task id. Your FIRST reply must be a PLAN only (files to change, with bullet points). Wait for the developer to say "go" before writing code.
7. After writing code, give the exact command(s) to test it and list every assumption you made. Do not say "done" unless the tests pass.
8. If this brief contradicts itself or the request would break a rule, STOP and say so.
=== END OF INSTRUCTIONS ===

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
{
  "display_name": "Anitha Raman",
  "current_role": "Administrative Coordinator",
  "work_examples": [
    "Coordinated calendars, maintained records, prepared reports, supported cross-team communication"
  ],
  "declared_skills": [
    {
      "name": "Excel",
      "level": 2
    },
    {
      "name": "Communication",
      "level": 3
    },
    {
      "name": "Team coordination",
      "level": 3
    },
    {
      "name": "Record management",
      "level": 3
    },
    {
      "name": "Presentation skills",
      "level": 2
    }
  ],
  "stated_goal_role_id": "R001",
  "preferences": {
    "interests": [],
    "weekly_hours": 6
  },
  "motivation": {
    "styles": [
      "progress",
      "encouragement"
    ],
    "check_in": "weekly"
  },
  "consent": true
}
```

Limits: `display_name` 1 to 60 chars. `current_role` optional. `work_examples`: 1 to 5 items, each 10 to 1000 chars. `declared_skills`: up to 30 items, `level` is 1, 2 or 3 (1 Beginner, 2 Intermediate, 3 Advanced). `stated_goal_role_id` optional, one of `R001` to `R008`. `preferences.interests`: up to 3 of `people`, `data`, `operations`, `planning`, `compliance`; `preferences.weekly_hours`: 1 to 40 or null. `motivation.styles`: 1 or 2 of `progress`, `goals`, `encouragement`, `accountability`, `challenge`; `motivation.check_in`: `daily`, `weekly` or `off`; `motivation.paused`: true or false. **`consent` must be `true`** (the checkbox).

To fill the form with a demo person: take one object from `api.demoPersonas()`, remove `persona_id`, rename nothing else, add `consent`, `preferences` and `motivation`.

**ConfirmRequest** (Screen 3 submit): exactly one decision per suggestion.

```json
{
  "decisions": [
    {
      "suggestion_id": "sg_SK-COMM",
      "action": "accept"
    },
    {
      "suggestion_id": "sg_SK-EXCEL",
      "action": "accept"
    },
    {
      "suggestion_id": "sg_SK-RECORDS",
      "action": "accept"
    },
    {
      "suggestion_id": "sg_SK-REPORT",
      "action": "accept"
    },
    {
      "suggestion_id": "sg_SK-SCHED",
      "action": "accept"
    }
  ],
  "added_skills": []
}
```
`action` is `accept`, `edit` (then `level` 1 to 3 is required) or `reject`. `added_skills` is a list of `{ "skill_id", "level" }` chosen from `api.skills()`.

**PlanRequest** (Screen 5): `{ "role_id": "R001", "weekly_hours": 6 }` (`weekly_hours` optional).
**ProgressUpdate** (Screen 6): `{ "step_order": 1, "percent": 40 }` (`percent` 0 to 100; `hours_logged` optional).
**MotivationPrefs** (Screen 6 settings): `{ "styles": ["progress", "goals"], "check_in": "weekly", "paused": false }`.
**ReviewRequest** (Screen 7): `{ "reviewer": "Name", "decision": "acknowledged" | "override" | "escalate", "note": "optional" }`.

## 6. Data shapes you receive (real output; long lists are shortened with "... n more")

**Profile** after create (keep only `profile_id`; see rule F8):
```json
{
  "profile_id": "prof_97d4982679",
  "display_name": "Anitha Raman",
  "current_role": "Administrative Coordinator",
  "work_examples": [
    "Coordinated calendars, maintained records, prepared reports, supported cross-team communication"
  ],
  "declared_skills": [
    {
      "name": "Excel",
      "level": 2
    },
    {
      "name": "Communication",
      "level": 3
    },
    {
      "name": "Team coordination",
      "level": 3
    },
    {
      "name": "Record management",
      "level": 3
    },
    {
      "name": "Presentation skills",
      "level": 2
    }
  ],
  "stated_goal_role_id": "R001",
  "preferences": {
    "interests": [],
    "weekly_hours": 6
  },
  "motivation": {
    "styles": [
      "progress",
      "encouragement"
    ],
    "check_in": "weekly",
    "paused": false
  },
  "created_at": "2026-11-01T12:19:25+00:00"
}
```

**Extract response** (Screen 3). `suggestions[]` has `suggestion_id`, `skill_id`, `name`, `suggested_level` (1 to 3), `source` (`declared`, `declared_alias`, `extracted`, `user_added`), `signal` (`declared_only`, `mentioned`, `performed`), `evidence[]` (`quote`, `work_example_index`), `explanation`. `unmatched_declared` is a list of names that could not be scored.
```json
{
  "profile_id": "prof_97d4982679",
  "suggestions": [
    {
      "suggestion_id": "sg_SK-COMM",
      "skill_id": "SK-COMM",
      "name": "Communication",
      "suggested_level": 3,
      "source": "declared",
      "signal": "performed",
      "evidence": [
        {
          "quote": "supported cross-team communication",
          "work_example_index": 0
        }
      ],
      "explanation": "You listed this skill; supported by your examples"
    },
    {
      "suggestion_id": "sg_SK-EXCEL",
      "skill_id": "SK-EXCEL",
      "name": "Excel",
      "suggested_level": 2,
      "source": "declared",
      "signal": "declared_only",
      "evidence": [],
      "explanation": "You listed this skill; no supporting example yet"
    },
    {
      "suggestion_id": "sg_SK-RECORDS",
      "skill_id": "SK-RECORDS",
      "name": "Record management",
      "suggested_level": 3,
      "source": "declared",
      "signal": "performed",
      "evidence": [
        {
          "quote": "maintained records",
          "work_example_index": 0
        }
      ],
      "explanation": "You listed this skill; supported by your examples"
    },
    "... 2 more"
  ],
  "unmatched_declared": [
    "Team coordination",
    "Presentation skills"
  ],
  "extraction_mode": "rules",
  "warnings": [
    "Suggestions come from keyword rules. Please check every one."
  ]
}
```

**Recommendations** (Screen 4). `recommendations` is the ranked list; `goal` is the worker's own stated goal with the same fields (or `null` if none was set). `blocking_gaps` holds **skill ids**: get the names from the `gaps` array (same `skill_id`).
```json
{
  "profile_id": "prof_97d4982679",
  "recommendations": [
    {
      "rank": 1,
      "role_id": "R001",
      "title": "HR Coordinator",
      "score": 0.7877,
      "band": "bridgeable",
      "feature_scores": {
        "skill_coverage": 0.7826,
        "preference_fit": null,
        "learnability": 0.8
      },
      "weights_used": {
        "skill_coverage": 0.7059,
        "learnability": 0.2941
      },
      "blocking_gaps": [
        "SK-CONF"
      ],
      "matched": [
        {
          "skill_id": "SK-EXCEL",
          "name": "Excel",
          "user_level": 2,
          "required_level": 2,
          "coverage": 1.0,
          "evidence_quotes": []
        },
        "... 3 more"
      ],
      "gaps": [
        {
          "skill_id": "SK-CONF",
          "name": "Confidentiality",
          "required_level": 2,
          "user_level": 0,
          "gap_levels": 2,
          "mandatory": true,
          "importance": 5,
          "est_hours": 24.0,
          "priority": 15.0
        }
      ],
      "est_gap_hours": 24.0,
      "openness_flags": [],
      "explanation": "HR Coordinator: skill coverage 78%. Strongest matches: Excel, Communication, Record management. Biggest gaps: Confidentiality (~24 h estimated). Band: bridgeable. Weights are provisional.",
      "provisional_weights": true
    },
    "... 7 more"
  ],
  "goal": {
    "rank": 1,
    "role_id": "R001",
    "title": "HR Coordinator",
    "score": 0.7877,
    "band": "bridgeable",
    "feature_scores": {
      "skill_coverage": 0.7826,
      "preference_fit": null,
      "learnability": 0.8
    },
    "weights_used": {
      "skill_coverage": 0.7059,
      "learnability": 0.2941
    },
    "blocking_gaps": [
      "SK-CONF"
    ],
    "matched": [
      {
        "skill_id": "SK-EXCEL",
        "name": "Excel",
        "user_level": 2,
        "required_level": 2,
        "coverage": 1.0,
        "evidence_quotes": []
      },
      "... 3 more"
    ],
    "gaps": [
      {
        "skill_id": "SK-CONF",
        "name": "Confidentiality",
        "required_level": 2,
        "user_level": 0,
        "gap_levels": 2,
        "mandatory": true,
        "importance": 5,
        "est_hours": 24.0,
        "priority": 15.0
      }
    ],
    "est_gap_hours": 24.0,
    "openness_flags": [],
    "explanation": "HR Coordinator: skill coverage 78%. Strongest matches: Excel, Communication, Record management. Biggest gaps: Confidentiality (~24 h estimated). Band: bridgeable. Weights are provisional.",
    "provisional_weights": true
  },
  "disclaimer": "Scores are provisional and explain skill coverage. They are not a hiring probability or a guarantee of employment."
}
```

**Plan** (Screen 5). A step has `status` `resource_found` (then `resource` is an object) or `no_verified_resource` (then `resource` is `null`). `resource.verification_status` is `verified`, `seed_unverified` or `sample_placeholder`.
```json
{
  "plan_id": "plan_230fe857f6",
  "profile_id": "prof_97d4982679",
  "role_id": "R001",
  "role_title": "HR Coordinator",
  "total_est_hours": 24.0,
  "weekly_hours": 6,
  "weeks_at_pace": 4,
  "steps": [
    {
      "order": 1,
      "skill_id": "SK-CONF",
      "skill_name": "Confidentiality",
      "status": "no_verified_resource",
      "resource": null,
      "est_hours": 24.0,
      "rationale": "Moves Confidentiality from level 0 to 2 (target 2) - mandatory",
      "builds_on": []
    }
  ],
  "unresolved_skill_ids": [
    "SK-CONF"
  ],
  "includes_unverified_resources": false,
  "disclaimer": "Courses marked unverified or sample have not been confirmed by a person. Check the course page before enrolling."
}
```

**Progress** (Screen 6). `next_message` is `null` when no message applies.
```json
{
  "profile_id": "prof_97d4982679",
  "plan_id": "plan_230fe857f6",
  "percent": 40,
  "hours_done": 10.0,
  "hours_total": 24.0,
  "steps_done": 0,
  "steps_total": 1,
  "steps": [
    {
      "order": 1,
      "skill_name": "Confidentiality",
      "est_hours": 24.0,
      "percent": 40
    }
  ],
  "last_activity_at": "2026-11-01T12:19:25+00:00",
  "next_message": {
    "message_id": "msg_39040e0266",
    "style": "progress",
    "event": "start",
    "text": "You have begun. Your plan has 1 step and about 24 hours in all. 40% done so far.",
    "suggested_action": "none"
  }
}
```

**Audit** (Screen 7). Each variant has six `metrics` and a `flags` list (empty when fine).
```json
{
  "audit_id": "aud_34c369a1",
  "profile_id": "prof_97d4982679",
  "status": "flagged",
  "canary": true,
  "variants": [
    {
      "variant_id": "A29",
      "cue": "age_statement",
      "metrics": {
        "skills_jaccard": 1.0,
        "top3_overlap": 3,
        "kendall_tau": 1.0,
        "max_abs_score_delta": 0.0,
        "plan_hours_delta": 0.0,
        "lexicon_hits": 0
      },
      "flags": []
    },
    {
      "variant_id": "A42",
      "cue": "age_statement",
      "metrics": {
        "skills_jaccard": 1.0,
        "top3_overlap": 3,
        "kendall_tau": 1.0,
        "max_abs_score_delta": 0.0,
        "plan_hours_delta": 0.0,
        "lexicon_hits": 0
      },
      "flags": []
    },
    "... 5 more"
  ],
  "thresholds": {
    "skills_jaccard_min": 0.9,
    "top3_overlap_min": 3.0,
    "kendall_tau_min": 0.9,
    "max_abs_score_delta_max": 0.03,
    "plan_hours_delta_max": 10.0,
    "lexicon_hits_max": 0.0
  },
  "limitations": [
    "Tests only the variants listed; it cannot prove the system is free of bias.",
    "Variants add a statement about age or years of experience to the worker's own text.",
    "... 1 more"
  ],
  "review": null,
  "created_at": "2026-11-01T12:19:25+00:00"
}
```

**Job advert check** (side page):
```json
{
  "status": "flagged",
  "flags": [
    {
      "rule_id": "experience_cap",
      "matched_text": "Up to 3 years",
      "why": "Caps experience, which can screen out experienced workers",
      "suggestion": "Describe the skills needed instead of limiting years"
    },
    {
      "rule_id": "fresher_wording",
      "matched_text": "Freshers",
      "why": "Targets new graduates",
      "suggestion": "Say 'entry-level role' and list the skills required"
    },
    {
      "rule_id": "age_coded_wording",
      "matched_text": "Energetic",
      "why": "Age-coded wording",
      "suggestion": "Describe the behaviour or skill you need"
    }
  ],
  "skills_first": false,
  "limitations": [
    "Keyword rules only: a clean result does not prove a role is fair.",
    "A person decides what to change."
  ]
}
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
