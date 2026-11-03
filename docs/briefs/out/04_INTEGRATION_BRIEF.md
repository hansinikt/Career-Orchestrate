# Career Orchestrator: INTEGRATION BRIEF (Dev 4)

=== INSTRUCTIONS FOR THE AI ASSISTANT (read this first, follow it exactly) ===
You are helping ONE developer on the INTEGRATION part of "Career Orchestrator", a hackathon prototype built by four first-time collaborators.
This brief is your ONLY source of truth. Rules:
1. Use only what is written in this brief and in files the developer pastes into the chat. If something is not specified, reply "Not specified in the brief" and ask the developer. Never guess.
2. Never invent: API endpoints, field names, status codes, library or package names, file names, course names, web links, statistics, or job adverts.
3. Never add or use age, date of birth, gender, graduation year, or years of experience, anywhere (code, data, screens, prompts, tests).
4. Allowed technology: Git and GitHub, shell commands, Python 3.11+, the Makefile. No new libraries without asking.
5. Files you may create or change: tests/*, .github/*, docs/*, data/v2/resources.json (a human enters verified courses only; you must never invent one). Never change any other file.
6. Work on ONE task at a time. The developer will name a task id. Your FIRST reply must be a PLAN only (files to change, with bullet points). Wait for the developer to say "go" before writing code.
7. After writing code, give the exact command(s) to test it and list every assumption you made. Do not say "done" unless the tests pass.
8. If this brief contradicts itself or the request would break a rule, STOP and say so.
=== END OF INSTRUCTIONS ===

Paste this whole brief into your AI assistant at the start of each chat, then one task id (I1 to I10, section 9).

## 1. Your mission

You are the glue and the gatekeeper. You own the repository, the tests, the automatic checks, the course catalogue (`data/v2/resources.json`), the documents and the final demo. You make sure the frontend, backend, engine and data fit together, that nothing biased, invented or untested reaches the stage, and that the demo works offline on Wednesday.

You own: `tests/`, `.github/`, `docs/`, `Makefile`, `data/v2/resources.json`, `data/v2/fixtures/` (generated). Others own their folders (see brief 00, section 3). You review every pull request.

## 2. First 3 hours (Sunday)

1. **Set up and test.** `make setup`, `make test` (expect 41 passed), `make run`, open `http://localhost:8000/docs`.
2. **Create the GitHub repository** (private), then in the project folder:
```
git init
git add .
git commit -m "Career Orchestrator v2 baseline"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```
Check `.env` is not committed (`git ls-files | grep .env` must show only `.env.example`).
3. **Invite the other three** as collaborators. Edit `.github/CODEOWNERS`: replace the `@DEV` placeholders with their GitHub usernames.
4. **Turn on protection**: GitHub, Settings, Branches, add a rule for `main`: require a pull request and one review, require the CI check `test` to pass.
5. **Confirm CI runs**: push a tiny change on a branch and open a pull request; the `test` check must go green.
6. **Post the contract-freeze message** in the group chat:
> "`contracts/v2/models.py` is frozen from now. If you need a field changed, message me with: the field, the screen or function that needs it, and what breaks without it. I will ask all four. After Monday 22:00 no contract change is allowed."
7. **Send everyone** brief 00 plus their own brief, and ask the four gate questions (brief 00, section 6).

## 3. SAP check (30 minutes, each of the three people with SAP access)

Menu tiles do not prove working access. Each person writes down for each item **worked / did not work / not tried**, with the date:
1. Log in to the SAP BTP trial or the organiser-provided account; note which subaccount and region.
2. Find AI Launchpad (or Generative AI Hub). Can you open it?
3. Can you create a service key for an AI service and see a model list? (Do not paste the key anywhere.)
4. Is Joule Studio visible? (It was not in the screenshot menu.)

What we may say on stage: only what someone actually did. "Tested" means a person ran it. Otherwise: "Designed to run on SAP AI Core and Generative AI Hub; not yet connected." Whether the free trial allows Generative AI Hub is **unverified**; do not claim it.

## 4. Course verification (you are the only person who edits `resources.json`)

A course may be `verified` only if **a human opened the course page, today or later**, and all of this is true: the URL is the course page itself (not a homepage); the title matches the page; the page says which skill it teaches; the provider is real; the date opened is recorded. Otherwise it stays `seed_unverified` or `sample_placeholder`. Never mark `verified` from an AI's memory.

Record template (change the existing record's fields; keep every key name exactly as in the example below):
```json
{
  "resource_id": "C0xx",
  "title": "<title exactly as on the page>",
  "provider": "<provider>",
  "url": "<course page URL, not a homepage>",
  "skill_ids": ["SK-..."],
  "level_from": 0,
  "level_to": 2,
  "est_hours": null,
  "duration_text": "<as stated on the page, or null>",
  "cost": "free|paid|unknown",
  "verification_status": "verified",
  "last_verified": "2026-11-0x",
  "note": "<what the page says it covers; who opened it>"
}
```
Existing example (a homepage-only record, so it stays unverified):
```json
{
  "resource_id": "C001",
  "title": "Excel for Data Analysis",
  "provider": "Microsoft Learn",
  "url": "https://learn.microsoft.com/",
  "skill_ids": [
    "SK-EXCEL",
    "SK-REPORT"
  ],
  "level_from": 0,
  "level_to": 1,
  "est_hours": null,
  "duration_text": "2-4 weeks",
  "cost": "unknown",
  "verification_status": "seed_unverified",
  "last_verified": null,
  "note": "homepage only, not a course page"
}
```
After any edit: `make test`, `make fixtures`, `make test` again. If Anitha's plan changes (a verified Confidentiality course would turn her `no_verified_resource` step into a real one), update the expected values in the tests and in brief 01.

Search log (Dev 3 does the searching, you verify): keep their table in `docs/search_log.md`. Allowed claims: "Every course shown is labelled verified, unverified or sample." "We searched these sources on these dates." Not allowed: "best", "guaranteed", "recruiters prefer".

## 5. Pull request review checklist (for every PR)

1. One task id; the description lists what changed, assumptions, anything unfinished, how it was tested.
2. Only files the author owns changed: `git diff --name-only origin/main...HEAD`.
3. `make test` is green on your machine, not just CI.
4. Forbidden-term scan returns nothing new:
```
grep -rniE "\b(age|dob|birth|gender|years_experience|graduation)\b" frontend backend engine
```
(Some hits are legitimate, for example the audit text "age statements" or the forbidden-field list. Judge each one.)
5. No scores or rankings calculated outside `engine/` (look for `0.60`, `weights`, `sort(` in `frontend/`).
6. No secrets: `git diff origin/main...HEAD | grep -iE "api[_-]?key|secret|token"`.
7. No new library in `requirements.txt` or a CDN script in `frontend/`.
8. Visible text only in `frontend/strings.js`; no words "guarantee", "will get hired", "probability", "chance of".
9. Ask the author to explain the change in two plain sentences. If they cannot, do not merge.

## 6. Milestones

| Milestone | When | Pass condition |
|---|---|---|
| M1 Setup | Sunday evening | 4 people ran `make test` (41 passed); repo, CI, branch rule set; freeze message sent |
| M2 Screens 1 to 4 | Monday 20:30 call | Frontend does the journey through role selection against the real backend |
| M3 Screens 5 to 7 + data | Monday 22:00 freeze | Plan, progress, audit screens; D1 to D6 done; no open contract change |
| M4 Demo build | Tuesday 20:00 | `v2-demo` tag; offline rehearsal works; backup video recorded |

## 7. Build and demo procedure

```
make test                       # must be green
make fixtures                   # refresh the saved real examples
cp -r frontend frontend_dist    # only if the frontend has a build step; plain files need no copy
make demo                       # starts the app in replay mode on http://localhost:8000
```
The backend serves `frontend_dist/` if it has `index.html`, otherwise `frontend/`. Run `make demo` with the wifi switched off: it must work. Then:
```
git tag v2-demo
git push origin v2-demo
```
Do this **Tuesday at 20:00 and then change no code**. Copy the project folder to a USB stick and to a second laptop. Record a screen video of the full Anitha journey (backup).

## 8. Acceptance: the Anitha test (24 steps)

Do this in the browser on the real backend. All must pass.

1. Welcome shows the consent box and the disclaimer; "Start" is disabled until consent is ticked.
2. Choosing styles: one or two only; a third is blocked.
3. Screen 2: enter name Anitha Raman, current role Administrative Coordinator, her sentences, her three skills (Excel 2, Communication 3, Record management 3), goal HR Coordinator.
4. No age, date of birth, gender or experience field exists anywhere.
5. Extraction shows Scheduling and Reporting as "found in your words" with the exact quote.
6. Declared skills with no quote say "No supporting example yet".
7. Gate 1: the Continue button stays disabled until every suggestion has a decision.
8. Accept Scheduling and Reporting, then confirm.
9. Recommendations: HR Coordinator is first with score 0.7877 and band "bridgeable", and the box "Your goal" shows it.
10. Top three are HR Coordinator 0.7877, Project Coordinator 0.6662, Learning and Development Coordinator 0.5980.
11. Reasons and the blocking gap "Confidentiality" are visible; the weights note says provisional.
12. Gate 2: choose HR Coordinator.
13. Plan: 24 hours, 4 weeks at 6 hours a week, one step "Confidentiality" labelled "no verified course" (unless you added one).
14. A plan with unverified resources shows the unverified label on each step.
15. Progress screen starts at 0%.
16. Update the step to 25%: message "You have begun. Your plan has 1 step and about 24 hours in all. 25% done so far." (progress style). Other styles read differently.
17. Mark "not helpful" three times: the style rotates out (two-style profiles only).
18. Pause: no message appears; resume restores messages.
19. Fairness screen: six variants pass; canary is flagged on five metrics; record a review decision.
20. Job-advert page: paste "Recent graduate wanted, digital native, maximum 5 years experience" and see flags for fresher wording, age-coded wording and experience cap.
21. Delete my data: the profile is gone; reload gives NOT_FOUND handled gracefully.
22. Stop the backend: the frontend shows a plain "could not reach the server" message (NETWORK), no blank screen.
23. Re-run in a private window with a fresh profile and the second style combination: same numbers.
24. Switch the wifi off, restart with `make demo`, repeat steps 1 to 13.

Failure tests (each must show a clear message, not a crash):

| Action | Expected |
|---|---|
| Send `age` in a profile (use `/docs`) | HTTP 422, code `FORBIDDEN_FIELD` |
| Recommendations before confirming | HTTP 409, `SKILLS_NOT_CONFIRMED` |
| Plan before choosing a role | HTTP 409, `NO_ACTIVE_PLAN` |
| Profile without consent | HTTP 400, `CONSENT_REQUIRED` |
| Unknown profile id | HTTP 404, `NOT_FOUND` |
| Work example shorter than 10 characters | HTTP 422, `VALIDATION_ERROR` |

## 9. Tasks (one per AI chat)

| ID | Pri | Task | Done when |
|---|---|---|---|
| I1 | P0 | Section 2: repository, CI, branch rule, CODEOWNERS, freeze message | M1 passed |
| I2 | P0 | Gate questions and SAP check (section 3): collect each person's results into `docs/sap_check.md` | File has the three people's results |
| I3 | P0 | Verify courses for the skills Dev 3 finds (section 4) and add them to `resources.json` | At least Confidentiality and one more verified, tests updated, or an honest note that none was found |
| I4 | P0 | Review every PR with the checklist (section 5) | All merged work reviewed |
| I5 | P0 | Run the 24-step test against the frontend twice: Monday evening and Tuesday afternoon; file a numbered bug list | List sent to owners |
| I6 | P0 | Decision on OD1 (HR administration) with Dev 3, before Monday 22:00 | Decision in chat; docs and tests updated if yes |
| I7 | P0 | Demo build and tag (section 7) | `v2-demo` pushed; USB copy; offline test passed |
| I8 | P0 | Write the 5-minute demo script and the slide (section 10) | Both rehearsed twice |
| I9 | P1 | Record the backup video | File on USB and phone |
| I10 | P1 | Update the PRD and these briefs with anything that changed | `docs/` matches the final code |

## 10. Demo script (5 minutes) and one slide

1. (30 s) Problem: experienced administrative workers are filtered out by age-coded and credential-heavy adverts. We help them show what they can already do.
2. (60 s) Anitha writes what she does. The system suggests skills with her exact words; she decides. **Say: "A person decides every skill."**
3. (60 s) Roles ranked with reasons; her goal shown first; the blocking gap in plain words.
4. (45 s) Plan with hours and weeks. Where no verified course exists it says so.
5. (45 s) Progress in her chosen encouragement style; show a second style for contrast.
6. (45 s) Fairness: age statements change nothing; the canary is caught; a human reviews.
7. (15 s) Job-advert check (if built).

Three-column slide: **Working now** (all of the above, run live, rules mode) | **Designed next** (language-model extraction with the same checks; SAP AI Core and Generative AI Hub; verified course catalogue; job-advert sampling) | **Not claimed** (no job guarantee, no validated weights, no real user data).

Likely questions:
- *Does it use AI?* The prototype uses fixed rules; the same checks are designed to wrap a language model, which is where the fairness audit matters most.
- *Why trust the courses?* Every course is labelled; only human-verified ones carry the verified label; the search log lists what we checked and when.
- *Is the score a hiring chance?* No. It is a provisional skills-coverage figure used to explain the match.
- *Is it tested on SAP?* Say only what the SAP check recorded.
- *What about privacy?* Consent first, no age or gender fields, delete-my-data, data stored locally.

## 11. Risks and what to cut

| Risk | Plan |
|---|---|
| Frontend not ready | Cut in this order: job-advert page, fairness screen UI (API stays), feedback buttons, accountability and challenge styles, interests. Keep screens 1 to 6 |
| Two people edit one file | Enforce owners; merge small and often |
| AI tool rewrites many files | Reject the PR; ask for a smaller task |
| A teammate stuck | Message the group at 30 minutes |
| No verified course found | Say so on stage; that honesty is the point |
| Demo laptop fails | Second laptop, USB copy, backup video |

## 12. Never do

Never mark a course `verified` without opening its page. Never edit the contract alone. Never merge unread code. Never change a test to make it pass without telling the author and Dev 3. Never commit `.env` or keys. Never change code after the `v2-demo` tag. Never claim an SAP service as tested unless someone tested it.
