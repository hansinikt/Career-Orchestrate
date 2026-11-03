# Part D: Execution

## 13. Work packages

Each task has an id. One AI session handles one task. "P0" means the demo fails without it; "P1" means valuable; "P2" means only if time remains. Effort is a rough estimate in hours for a beginner using an AI assistant [J]. "Done" always includes: `make test` is green, a person has read the changes, and the change is merged to the main branch through a pull request.

### 13.1 Dev 1: Frontend (`frontend/`)

| ID | Pri | Task | Done when | Effort | Needs |
|---|---|---|---|---|---|
| F1 | P0 | Inventory: technology, pages, where data comes from, how to run it. Post it in the group chat (gate G0a) | A short written inventory | 0.5 | |
| F2 | P0 | The `api` file: one function per call in section 8.2, one error handler, base URL in one config value | Each call works against `make run`; errors show `error.message` | 2 | B1 |
| F3 | P0 | Screen 1 (consent, style) and Screen 2 (work form, demo person button, goal, interests, weekly hours) | Anitha can be created from the form; no age field exists | 3 | F2 |
| F4 | P0 | Screen 3 (evidence cards, Gate 1) | Every card shows quotes or "No supporting example yet"; Continue disabled until all decided | 3 | F3 |
| F5 | P0 | Screen 4 (your goal, ranked roles, why panels, Gate 2, disclaimer) | Anitha's HR Coordinator shows bridgeable and Confidentiality as blocking | 3 | F4 |
| F6 | P0 | Screen 5 (plan, badges, "No verified resource yet") | Anitha's plan shows 24 hours and 4 weeks | 2 | F5 |
| F7 | P0 | Screen 6 (progress, messages, feedback, settings) | Setting step 1 to 40 shows the "You have begun" message | 3 | F6 |
| F8 | P1 | Screen 7 (fairness check, review) and the openness page | Canary shows Flagged; clean shows Pass | 3 | F5 |
| F9 | P0 | Plain-words pass; check rules F1 to F11; build into `frontend_dist/` | Checklist in 15.3 passes in the browser | 2 | F7 |

### 13.2 Dev 2: Backend (`backend/app/`)

A working reference backend exists and passes its tests. Dev 2 now **owns** it: read every line, run it, break it on purpose, and make it reliable. This is real work, not busywork: the backend is the thing every other part depends on.

| ID | Pri | Task | Done when | Effort | Needs |
|---|---|---|---|---|---|
| B1 | P0 | Run `make setup`, `make test`, `make run`; try every endpoint at `/docs`; write down anything confusing or wrong (gate G0b) | Report posted; fixes proposed through pull requests | 2 | |
| B2 | P0 | Explain to the team, in plain words, what happens at each endpoint (section 7.4), then check for missing error paths and add two tests of your own choosing | Two new tests, both green | 3 | B1 |
| B3 | P0 | Start-up checks: the catalogue loads, every role requirement skill exists, a clear message if the database file cannot be opened; log one line per request (method, path, status, milliseconds) | Bad catalogue gives a readable error | 2 | B1 |
| B4 | P0 | `tools/seed_demo.py`: through the API, create Anitha, Meera and Kiran with consent, confirm all suggestions, and pick their goal roles; print the ids | Running it leaves three complete journeys | 2 | B2 |
| B5 | P0 | Demo mode: with `frontend_dist/` present, `make demo` serves pages and API from one process; test with the network off | Works offline | 1 | F9 |
| B6 | P1 | The LLM adapter (section 10) with a fake provider for tests and automatic fallback to rules | Failing provider still returns rule suggestions with `extraction_mode: rules` | 4 | gate G2 |
| B7 | P1 | Backup and restore of the database file as two `make` targets | Documented and tried | 1 | |

### 13.3 Dev 3: Data and AI (`engine/`, `data/v2/`)

| ID | Pri | Task | Done when | Effort | Needs |
|---|---|---|---|---|---|
| D1 | P0 | Review `aliases.json`. Run `python data/run_v2_examples.py`, read each suggestion for the eight personas, and list false matches (for example "resolved" meaning Problem solving). Propose fixes | A written list and a pull request; tests green | 3 | |
| D2 | P0 | Review the role interest tags and hours per level (6.2); propose changes only with a reason; keep a note of every change | Note posted; tests green | 2 | |
| D3 | P0 | Open decision OD1 (add "HR administration" to HR Coordinator?) with Dev 4; if yes, edit `data/build_seed_v2.py`, run `make seed fixtures`, update the worked numbers in tests with Dev 4 | Decision recorded; numbers consistent | 2 | |
| D4 | P0 | Read every cell of the message library (9.7). Fix tone or wording; keep placeholders valid | `test_motivation_templates_complete_and_clean` green | 2 | |
| D5 | P0 | Course search for the priority skills (11.6): fill the search log and give Dev 4 candidates with page links (you search; Dev 4 verifies) | Search log with at least 3 skills searched | 4 | |
| D6 | P0 | Job-advert check: 3 public adverts for each of HR Coordinator, L&D Coordinator and Operations Analyst; tally skills; write the date and count in `data_note` | Three notes written | 2 | |
| D7 | P1 | Record the model replies for replay (section 10) | `data/replay/cache.json` exists, made by real calls | 2 | B6, a key |
| D8 | P1 | Write 5 extra test sentences that paraphrase skills and record which the rules miss (shows limits honestly) | A table of hits and misses | 1 | |

### 13.4 Dev 4: Integration (repository, tests, courses, demo)

| ID | Pri | Task | Done when | Effort | When |
|---|---|---|---|---|---|
| I1 | P0 | Create the GitHub repository from the handoff folder; turn on CI; set CODEOWNERS (replace @DEV names); require a pull request and one review before merging | Green CI badge; protection on | 1 | Sunday |
| I2 | P0 | Freeze contract v2.0; send the team message (Appendix C); run gate G0 | Message sent; all gate answers collected | 1 | Sunday |
| I3 | P0 | SAP check (section 17) and Learning Hub sign-in; ask the other two to do their own SAP check | Written yes or no per person | 1 | Sunday |
| I4 | P0 | Verify course candidates from Dev 3 and record them in `resources.json` using the admission rule (11.2) | At least 3 verified by Tuesday 14:00, or a decision to ship "no verified resource" | 3 | Mon to Tue |
| I5 | P0 | Run the Monday 20:30 call; keep the cut list (3.5) | Cuts written down | 1 | Monday |
| I6 | P0 | Integration: run the whole journey in the browser; compare every network call with the generated documentation; log each mismatch as an issue; fix or assign | Checklist 15.3 passes | 4 | Tuesday day |
| I7 | P0 | Failure tests (15.4) | All rows pass or have a written decision | 2 | Tuesday day |
| I8 | P0 | Build `frontend_dist`, run `make demo` on the demo laptop, offline | Works with Wi-Fi off | 1 | Tuesday day |
| I9 | P0 | Demo script, three-column slide, three rehearsals, backup video (section 16) | Video saved in two places | 4 | Tue to Wed |
| I10 | P0 | Tag `v2-demo` at 20:00 Tuesday | Tag exists; the demo laptop uses exactly that tag | 0.5 | Tuesday |

### 13.5 How Dev 4 reviews AI-written work (the integration owner's checklist)

Review each pull request in this order, in ten minutes or less:

1. Which files changed? Only the task's files? (If other people's folders or `contracts/` changed, stop.)
2. `git diff contracts/v2/` must be empty unless a contract change was agreed.
3. New libraries? Look at `backend/requirements.txt` and the frontend's dependency file.
4. Search for forbidden words: `grep -rniE "\b(age|dob|birth|gender|years_experience)\b" frontend backend engine` (ignore matches in comments that say they are forbidden).
5. Search for invented content: new course names, URLs or numbers that are not in the data files.
6. `make test` is green on the reviewer's machine, not only the author's.
7. Run it. Click the thing that changed.
8. Read the pull request note: assumptions and anything incomplete are listed.



## 14. Working with AI coding assistants (free plans, first-time team)

### 14.1 What goes wrong and what stops it

| Problem | Why it happens | What we do |
|---|---|---|
| It builds everything at once, runs out of context, and drifts | The request is too big | One task id per session; a task fits in one screen of text; a new chat for each task |
| It invents a framework, a vector database, an age field, or renames API fields | It "improves" what it was not asked to touch | `AGENTS.md` rules pasted first; contract file pasted; CI fails on any contract change; review step 2 and 4 |
| It makes up courses, URLs, hours or statistics | A catalogue was requested and none was given | Only people edit `resources.json`; rule R5; test on verified courses |
| Its code looks finished but does not connect | Nothing forced it to match the contract | The assistant must run `make test`; the frontend is tried against the real backend the same day |
| It quietly changes behaviour you did not ask about | Large rewrites | Ask for a plan first, then the smallest change; read the diff |
| Free-tier limits stop work midway | Long chats and big pastes | Small tasks; paste only the needed files; commit after every working step; carry on in another assistant using the same prompt |

### 14.2 The prompt template (copy, fill the brackets)

```
You are helping on ONE task of a hackathon project. Follow these rules exactly:
[paste AGENTS.md]

The task: [ID and one-sentence description, copied from section 13]
It is done when: [copy the "Done when" text]
Files you may change: [list]
Files you must NOT change: everything else, especially contracts/v2/models.py and data/v2/resources.json
Here is the contract (do not change it): [paste only the models this task uses]
Here is the current code for the files to change: [paste]

First reply with ONLY a plan: the files you will change and what changes in each, in bullets.
Do not write code until I say "go".
After the change, tell me the exact command to run the tests, and list any assumption you made.
If anything is unclear or contradicts the rules, stop and ask me.
```

### 14.3 Session discipline

1. One task per chat. When the task is done, close the chat.
2. Paste the minimum: the rules, the task, the contract models the task uses, and the files to change. Never paste this whole document.
3. Commit after every working step so you can go back.
4. If the assistant starts changing files you did not mention, say "stop" and restart the chat with a stricter prompt.
5. Never type a password or key into an assistant. Never paste `.env`.
6. If two assistants disagree, the contract and the tests decide.
7. Learn as you go: ask the assistant to explain each file in plain words after it writes it. You must be able to explain your own part to the panel.

### 14.4 What each person should be able to explain by Wednesday

Dev 1: the seven screens and which call each makes. Dev 2: what each endpoint does and where data is stored. Dev 3: how a skill is suggested and how a score is calculated (use the worked example in 9.4). Dev 4: the whole journey, the two gates, the fairness check and the limits. Everyone: the three-column slide (16.2).



## 15. Testing and validation

### 15.1 Automated tests (run `make test`; expect 41 passed)

| Test | What it protects |
|---|---|
| `test_contract_has_no_forbidden_fields` | No age or similar field in any model (R1) |
| `test_catalog_consistency` | Every role and course refers to real skills; `verified` needs a URL and date; weights sum to 1 (R5) |
| `test_forbidden_fields_rejected` | `age`, `dob`, `gender`, `years_experience`, `date_of_birth` give `FORBIDDEN_FIELD`; no consent gives `CONSENT_REQUIRED`; unknown fields give `VALIDATION_ERROR` |
| `test_gates` | Recommendations need confirmation; every suggestion needs a decision; edit needs a level; plan needs to exist (R2) |
| `test_evidence_is_grounded_and_inference_capped` | For all 8 personas every quote is a verbatim substring; inferred level at most 2 (R3, R4) |
| `test_anitha_worked_numbers` | Top three R001, R002, R006; score 0.7877; band bridgeable; blocking Confidentiality; 24 hours; 4 weeks |
| `test_rejecting_inferred_skills_changes_result_as_documented` | Score 0.6368 and 48 hours when both inferred skills are rejected |
| `test_all_personas_run_and_are_deterministic` | All 8 complete the journey twice with identical rankings |
| `test_missing_interests_renormalise` | With no interests, F3 is null and weights sum to 1 |
| `test_plan_never_shows_unverified_when_disallowed` | With both flags off, no course appears |
| `test_motivation_templates_complete_and_clean` | All 30 messages fill from real data and contain no age-coded phrase |
| `test_motivation_flow_and_pause` | Event order, style rotation, pause gives no message, unknown step gives 422 |
| `test_style_dropped_after_three_unhelpful` | The feedback loop runs without error |
| `test_readiness_check` | Flags and no-flags examples |
| `test_audit_clean_pass_and_canary_flagged` | Six variants pass, canary flagged on five metrics, review stored |
| `test_delete_removes_everything_but_keeps_log` | Cascade delete (section 7.5) |
| `test_error_shape_everywhere` | Every error is `{"error": {...}}` |
| `test_meta_and_catalog_endpoints` | 8 roles, 25 skills, 8 demo personas |

The older `tests/test_all.py` (23 tests) checks the legacy v1 engine functions that v2 still uses.

### 15.2 What has and has not been validated

| Validated (by running code) [V] | Not validated |
|---|---|
| The whole journey for all eight personas through the real API | That any weight, threshold or hours-per-level is "right" |
| Anitha's numbers (9.4), the canary behaviour, determinism, error shapes | That the roles and skills match the real job market (adverts check is a task: D6) |
| Evidence quotes are verbatim | That courses are good or recognised by recruiters (policy in section 11) |
| The engine never receives forbidden fields | Behaviour with real users, real-world text lengths, or other languages |
| | SAP model access (gate G1), any language-model behaviour, the real frontend |

### 15.3 Manual checklist: Anitha's full journey (rehearse three times; rehearsal 3 offline)

| # | Step | Expected |
|---|---|---|
| 1 | Open the app; the disclaimers are visible | Text from `/meta` |
| 2 | Tick consent; choose Progress and Encouragement; Continue | Continue enabled only after both |
| 3 | Use the demo person "Anitha Raman"; Continue | Form filled; there is no age field |
| 4 | Screen 3 shows five suggestions | Communication 3, Excel 2, Record management 3 (you listed); Reporting 2 and Scheduling 2 (found in your work) |
| 5 | Excel card | "No supporting example yet" |
| 6 | Scheduling card | Quote "Coordinated calendars" |
| 7 | Try to continue with one card undecided | Blocked |
| 8 | Accept all; Continue | Screen 4 |
| 9 | Goal card | HR Coordinator, bridgeable, blocking gap Confidentiality, about 24 hours |
| 10 | Ranking | HR Coordinator 1, Project Coordinator 2, L&D Coordinator 3 |
| 11 | Open "Why" on HR Coordinator | Matched skills with quotes; Confidentiality as gap |
| 12 | Choose HR Coordinator | Screen 5 |
| 13 | Plan | 24 hours, 4 weeks at 6 hours a week; step shows "No verified resource yet" (or a verified course if D5/I4 added one) |
| 14 | Start my plan; set step 1 to 40 | 40 percent; message "You have begun. Your plan has 1 step and about 24 hours in all. 40% done so far." |
| 15 | Mark it Helpful | Accepted without error |
| 16 | Set step 1 to 100 | 100 percent; encouragement "You finished your plan..." |
| 17 | Change style to Challenge in settings; update again | Next message in the new style (after a change that triggers an event) |
| 18 | Run the fairness check | Pass; six variants identical |
| 19 | Run it with the canary | Flagged; the canary row shows five flagged metrics |
| 20 | Record a review | Reviewer name and decision are shown |
| 21 | Paste "Freshers wanted. Up to 3 years of experience. Energetic team player." in the openness check | Three flags |
| 22 | Reject both inferred skills in a second run | Score 0.6368, gap 48 hours; Scheduling now appears in the plan |
| 23 | Delete the profile | Everything gone; reloading starts fresh |

### 15.4 Failure tests (Dev 4, Tuesday)

| Case | How to cause it | Pass when |
|---|---|---|
| Backend not running | Stop it, click Continue | Message and Try again; no blank screen |
| Slow reply | Add a delay in a test copy | Spinner shows; no double-submit |
| 500 error | Temporarily raise an error in a test copy | "Something went wrong. Nothing was lost." |
| Unknown profile | Edit the stored `profile_id` | Returns to Screen 1 |
| Out-of-order call | Open Screen 5 first | Goes to the missing step with the message |
| Empty or too-long text | Submit 0 and 1001 characters | Field-level message |
| Browser refresh mid-journey | Refresh on Screen 4 | Resumes from the stored `profile_id` |
| Network off | Turn Wi-Fi off | Everything still works (rehearsal 3) |

### 15.5 Continuous integration

On every push GitHub runs `make test` and the contract check. A red mark blocks the merge. This is the "daytime integrator" while Dev 4 is in class.



## 16. Demo script and panel guide

### 16.1 Five-minute script (adjust to the slot length, which is not yet known [U])

| Time | Say | Show |
|---|---|---|
| 0:00 | "Anitha is an administrative coordinator who wants to become an HR Coordinator. Her skills are real but hard to show." | Screen 1: consent, her choice of encouragement style |
| 0:30 | "She tells us what she does in her own words." | Screen 2 |
| 1:00 | "We suggest skills and show the exact words that support each one. She decides on every one." | Screen 3: Scheduling with "Coordinated calendars" |
| 1:45 | "Two sentences she wrote lift her match from 0.64 to 0.79 and halve her gap from 48 to 24 hours. Nothing is hidden: you can see why." | Screen 4: goal card, Why panel |
| 2:30 | "She picks a role. We build a plan. Where we have no verified course we say so, instead of inventing one." | Screen 5 |
| 3:00 | "She tracks progress, and the encouragement matches the style she chose." | Screen 6: 40 percent message |
| 3:40 | "We also check ourselves for age bias. Here is a deliberately biased version, and our check catches it. And here is what it can and cannot prove." | Screen 7 |
| 4:30 | "Here is what works today, what we tested separately, and what we designed next." | The three-column slide |

### 16.2 The three-column slide (must be accurate on the day)

| Working in the demo | Tested separately (only if actually tested) | Designed next (not built) |
|---|---|---|
| Evidence-linked skill suggestions with human confirmation; role matching with reasons; learning plan with honest gaps; progress and style-based encouragement; fairness check with a canary; openness check for job adverts | SAP Generative AI Hub model call (only if gate G1 passed, with a screenshot) | SAP vector matching; approval workflows; practical proof task with rubric; reminders; real vacancy data; sign-in |

### 16.3 Designed next (what we can explain, though it is not in the code)

This is the team's research [S] and v1 PRD mapped to this product. Say "designed", never "implemented".

| Capability | What it would do for Career Orchestrator | Status |
|---|---|---|
| SAP Joule Studio | Orchestrate the modules as agents with tool calls | Not built; not in the tool list we can reach |
| SAP Generative AI Hub on AI Core | Governed model access for skill extraction and explanation (section 10) | Only if gate G1 passes |
| SAP HANA Cloud vector engine | Match worker skills to role requirements even when words differ ("Case documentation" and "Documentation") | Not built; HANA Cloud is in the screenshot |
| SAP Build Process Automation | Route confirmed skills and plans to a human reviewer for approval | Not built; Build Lobby is in the screenshot |
| SAP Business Rules | Express the "no forbidden feature" and openness rules as testable business rules | Not built; our rules are in code |
| SAP Audit Log service plus our audit table | Platform-level security events plus our own record of approvals and overrides | Our table is built; platform service not |
| SAP Cloud Identity services | Separate worker, reviewer and administrator permissions | Not built |
| SAP SuccessFactors Talent Intelligence Hub and Opportunity Marketplace | Enterprise skills and internal mobility; we differentiate through worker-led moves beyond one employer | Not built; enterprise product |
| Practical proof task | A small role-relevant assignment, a visible rubric, saved as evidence. A score is not proof of performance | Not built |
| Language-model suggestions and rewrite | Paraphrase-tolerant suggestions; inclusive rewrite of adverts | Spec in section 10 |
| Reminders | Email or messaging nudges in the chosen style | Not built |
| More languages | Hindi, Telugu and others (they appear in the data) | Not built; text is kept in one file for this |

### 16.4 Questions the panel may ask, with honest answers

| Question | Answer |
|---|---|
| Is this live AI? | The prototype's suggestions come from transparent rules so results are explainable and repeatable. A language-model adapter is specified; we say plainly which parts are not built |
| Does the AI decide anything? | No. The worker confirms every skill and chooses the role. Reviewers sign off fairness flags. The system never rejects anyone |
| How do you stop age bias? | Three layers: there is no age field anywhere and the system refuses one; a counterfactual test adds age statements and checks that nothing changes, including a deliberately biased case it must catch; a human reviews flags. We also say what the test cannot prove |
| What does the score mean? | Coverage of the listed skills for a role against our catalogue. It is provisional and is not a hiring probability |
| How do you make sure courses are accurate? | Only a team member who opened the course page can mark it verified, with the date. Unverified items are labelled and gaps with no course say so. We do not promise outcomes |
| Where is your data from? | A small illustrative catalogue written by the team (8 roles, 25 skills, 9 course entries) and 8 synthetic people. We checked skills against real adverts for the demo roles on dates we record, if D6 is done |
| Why only 8 roles? | A prototype of one complete journey. The structure accepts more roles from the same files |
| How is encouragement personalised? | The worker chooses a style and can change it; messages come from a tested template library filled with their real progress. We did not infer anything about them. The grouping into five styles is our heuristic, not a validated model |
| What if the suggested skills are wrong? | They are suggestions. The worker accepts, edits or rejects each, and we show the exact words behind each one |
| Why not use SAP product X? | Listed in 16.3. We built the core journey first and say what we tested |
| What would you do with three more months? | Language-model suggestions with replay tests, real vacancy data, the proof task, reviewer workflows, reminders, more languages, and user testing with the intended workers |
| What about privacy? | Consent first; synthetic data only; delete on request; no age or similar field; no real personal data in the hackathon |

### 16.5 If something breaks on the day

Restore tag `v2-demo` on the demo laptop. Run it offline. If the live demo fails, play the backup video and continue with the three-column slide. Keep the video on the laptop and on a phone or USB drive.



## 17. SAP: what we know, what we will test, what we may claim

### 17.1 Facts the team supplied [S]

- The organisers provided access. Three people now have it. The screenshot shows these tools: SAP AI Launchpad, SAP Build Work Zone, SAP HANA Cloud, SAP Business Application Studio, SAP Build Lobby. Joule Studio is not listed in that menu.
- The team's research PDF describes twelve SAP capabilities and how each might apply (mapped in 16.3). It states that Generative AI Hub is a capability associated with AI Core and AI Launchpad, that Talent Intelligence Hub is an enterprise capability and not a drop-in API, and that Business Rules do not prove a model is unbiased.
- Earlier research (v1 PRD) [V]: Generative AI Hub needs an AI Core service instance on a plan that supports it; trial eligibility was not stated in the sources we could read [U]; the trial Joule skills in SAP Build cannot be taken to production.

### 17.2 What an item in the menu does and does not prove

A tile in a menu shows the tool exists in the tenant. It does not prove that a model can be called, that quota exists, or that a key can be created. Each of the three people with access runs the check below and writes down the result.

### 17.3 The 30-minute check (each SAP user, Sunday)

1. Open SAP AI Launchpad from the Access menu.
2. Look for a section about generative AI or models, and any place to try a prompt. Menu names may differ from what we expect [U]; write down exactly what you see.
3. If a prompt playground exists, send: "Reply with the word OK." Note whether it answers, which model answered, and any limit or error text.
4. In the platform's administration area, check whether an AI Core service instance exists, and whether a service key can be created for it. If the option is missing or denied, write down the message.
5. Do not share a key in the group chat or commit it. If you create one, store it in your own `.env` only.
6. Post a message: "Person: ___. AI Launchpad opens: yes/no. Playground works: yes/no (model: ___). Service key possible: yes/no."
7. Take screenshots of any success. They are evidence for the slide.

### 17.4 Decision

| Result | Decision |
|---|---|
| Playground works and a key can be created | Dev 2 (or the SAP user) implements the SAP provider in the adapter (section 10, B6), runs it once, and the slide may say "model call tested" with the screenshot. Everything else stays in rules mode |
| Playground works but no key | Say "tested in the playground only" |
| Neither | Skip SAP. Say "designed for" in the slide |

### 17.5 Teammates without access

No task in section 13 requires SAP. The app runs fully without it. The two teammates who do not have access can ask the organisers for it, and may try creating their own free SAP trial account if the organisers confirm that is allowed [U].

## 18. Risks, open decisions and open questions

### 18.1 Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Not enough time | High | High | Cut-list (3.5); feature freeze Monday 22:00; reference backend already exists |
| 2 | Frontend integration is harder than expected | Medium | High | `api` file only; real backend from Sunday; Dev 4 Tuesday day |
| 3 | AI assistant drifts or breaks the contract | High | Medium | Section 14; CI; review checklist |
| 4 | No verified courses by Tuesday | Medium | Medium | Honest "no verified resource yet"; start search Sunday; D5 and I4 |
| 5 | Free-tier limits stop a teammate | High | Low | Small tasks; commit often; switch assistant |
| 6 | SAP access does not provide a model | Medium | Low | Not needed; "designed for" |
| 7 | Demo laptop or Wi-Fi fails | Medium | High | Offline demo mode; backup video; tag `v2-demo` |
| 8 | Panel challenges honesty of claims | Medium | High | Three-column slide; section 16.4; label provisional numbers |
| 9 | Data too thin to look impressive (2 to 4 skills per person) | High | Low | Focus on Anitha and the evidence story; do not oversell rankings |
| 10 | Dev 4 is in class and unavailable | Certain | Medium | CI as daytime checker; fixed 20:30 call; Tuesday day is free |

### 18.2 Open decisions

| ID | Decision | Options | Recommended | Owner |
|---|---|---|---|---|
| OD1 | Add "HR administration" as a requirement of HR Coordinator? Course C005 teaches it | Yes (importance 3, preferred) or No | Yes, as preferred, so C005 becomes relevant. Needs the team's agreement because it changes their role data | Dev 3 and Dev 4 |
| OD2 | Show the numeric score or only the band and reasons | Both / band only | Band and reasons first, score as "match score (provisional)" in a smaller place | Dev 1 |
| OD3 | Keep the existing frontend or replace | Keep / replace | Keep and adapt if it exists (4.8) | Dev 1 |
| OD4 | Does the demo use Anitha's real-looking CSV values or the longer v1 sample? | CSV (v2) / v1 | CSV, because it matches the deck and the data the team supplied | Done |
| OD5 | Language of the interface | English only / add Hindi | English for the demo; strings in one file | Dev 1 |

### 18.3 Open questions

1. What time on Wednesday is the finale, and how long is the slot?
2. Does a frontend already exist, and in what technology? (G0a)
3. Does anyone have a usable LLM key? (G2)
4. Who is Dev 1, Dev 2, Dev 3 and Dev 4 by name? (section 3.1)
5. Which course sites does the SAP access cover, including SAP Learning Hub student edition?

## 19. Glossary (plain words)

| Term | Meaning |
|---|---|
| API | A set of web addresses a program can call to ask the backend for something |
| Endpoint | One address in the API, for example "create a profile" |
| Request, response | What the frontend sends, and what the backend sends back |
| JSON | A simple text format for structured data |
| Contract | The agreed list of fields and their types for every request and response. `contracts/v2/models.py` |
| Schema | A machine-readable description of a data shape |
| OpenAPI | A standard file that lists every endpoint and shape; generated from the contract |
| Frontend | What the user sees and clicks |
| Backend | The program that checks requests, calculates and stores results |
| Engine | The calculation code with no network or storage |
| Database, SQLite | Where user data is stored; SQLite is a database in a single file |
| Catalogue | The roles, skills and courses, stored as files in Git |
| Fixture | A saved example of a real request or response |
| Mock | A fake version of the backend used before the real one exists. Here the real backend runs from day one, so we do not need one |
| LLM | Large language model, an AI that works with text |
| LLM key | A secret code that lets a program use an LLM service; keep it in `.env` |
| Adapter | A small piece of code that hides which provider is used behind one fixed interface |
| Rules mode | The app works using fixed rules and no AI |
| Replay mode | The app uses pre-recorded real AI answers instead of calling AI |
| Gate | A step where a person must decide before the system continues |
| Band | strong fit, bridgeable or stretch, from skill coverage and blocking gaps |
| Coverage | How much of a role's required level the person already has |
| Blocking gap | A mandatory skill where the person has less than half the required level |
| Evidence, grounding | The exact words from the person's text that support a skill, checked by code |
| Alias | A different name for the same skill |
| Canary | A deliberately biased case used to prove the fairness check can catch bias |
| Provisional | A number we chose and have not validated |
| CI | Automatic checks that run on every push |
| Pull request (PR) | A proposed change that someone reviews before it joins the main code |
| Commit, branch, tag | A saved step in history; a line of work; a named, fixed version (`v2-demo`) |
| CORS | A browser rule about which web addresses may call the backend |
| Environment variable, `.env` | A setting kept outside the code; `.env` is a private file of settings |
