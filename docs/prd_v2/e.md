# Appendices

## Appendix A: The full contract

This is `contracts/v2/models.py`, the single definition of every request and response. The OpenAPI file is generated from it. Do not change it without the process in section 8.5.

```python
{{FILE:contracts/v2/models.py}}
```

## Appendix B: Sources and evidence

**Supplied by the team [S].** Research document "Career Orchestrator: Research Review: Existing Solutions, Gaps and Proposed Differentiation" (positioning against SAP SuccessFactors Opportunity Marketplace and Talent Intelligence Hub, Fuel50, Lightcast Career Pathways, Eightfold AI; four differentiators; recommended methodology; responsible-use limits). "Sap tools research.pdf" (twelve SAP capabilities). A screenshot of the SAP tools available (AI Launchpad, Build Work Zone, HANA Cloud, Business Application Studio, Build Lobby). Seven CSV files (roles, role skill requirements, learning resources, user profiles, user skills, work experience, learning progress). The competition handbook and concept deck from the v1 work.

**Verified by running code in this repository [V].** The worked numbers in 6.5, 9.4, 9.9 and 15.3; the 41 passing tests; the data findings in 6.4; the extractor coverage figures in 9.1; the sensitivity result in 9.3; the generated endpoint list and fixtures.

**Verified in v1 research and recorded there [V].** Generative AI Hub requires AI Core on a suitable plan; the SAP Build trial Joule skills cannot go to production; O\*NET is under a Creative Commons Attribution licence (not used in v2's data). The v1 PRD (section 55) lists its sources.

**Not verified [U]; named owner must check before relying on it.**

| Item | Owner |
|---|---|
| Whether a model can be called and a key created in the team's SAP tenant | Each SAP user (17.3) |
| Exact menu names and the SDK or package for Generative AI Hub | Whoever tests it |
| Whether a free SAP trial can be created by teammates without access | Dev 4 asks the organisers |
| Finale time and slot length | Dev 4 asks the organisers |
| Usage limits of the AI assistants on the team's plans | Each developer |
| Whether any course in the CSV is available, current or free | Dev 4 (verification, 11.2) |
| Whether the roles reflect current job adverts | Dev 3 (D6) |
| Any psychological validity of the five motivation styles | Not claimed |

## Appendix C: Message to send the team (copy and edit)

> Hi all. Here is our plan for the next three days. The full document is attached (PRD v2). Please read sections 1 to 4, 13 and 14 tonight; it is about 20 minutes. Deadline: Tuesday night. Finale: Wednesday.
>
> **Rules:** one task per AI chat; run `make test` after every change; never edit someone else's folder; never invent course names or links; no age or gender fields anywhere. The contract is frozen: if you think a field must change, tell me first.
>
> **Today, in the first two hours, please reply in the group with:**
> 1. Dev 1: does a frontend already exist? What technology? A list of its pages.
> 2. Dev 2: is Python 3.11 or newer installed? Did `make test` give 41 passed?
> 3. Everyone with SAP access: do the 30-minute check in section 17.3 and post your result.
> 4. Everyone: do you have any AI assistant (which one) and any API key?
> 5. Your class times for Monday and Tuesday.
>
> **Today after that:** Dev 1 builds Screens 1 to 3 against the running backend (`make run`). Dev 2 runs and reads the backend and posts what they learn. Dev 3 reviews the aliases and starts searching for courses for the skills in section 11.6. I will set up the repository and checks, and verify courses.
>
> **Monday:** merge your work after 17:00. We have a call at 20:30. Features freeze at 22:00. **Tuesday 20:00 is the deadline.**
>
> If you get stuck for more than 30 minutes, message the group. Nobody should struggle alone.

## Appendix D: GitHub issues and milestones

Create one issue per row of the tables in section 13 (title `ID: task`; labels: owner, priority). Create four milestones:

| Milestone | When | Contents |
|---|---|---|
| M1 | Sunday night | I1 to I3, B1, F1, F2, D1; gates G0 and G1 |
| M2 | Monday 22:00 (feature freeze) | F3 to F7, B2 to B4, D2 to D6 |
| M3 | Tuesday 14:00 | I4, I6, I7, F9, B5, gate G3 |
| M4 | Tuesday 20:00 (deadline) | I8, I10; F8, B6, B7, D7, D8 if time allows |

## Appendix E: File checklist for the repository

`AGENTS.md`, `LEGACY_V1.md`, `Makefile`, `.env.example`, `.gitignore`, `README.md`, `backend/requirements.txt`, `backend/app/{main.py,db.py,schema.sql}`, `engine/{core.py,extract_rules.py,motivation.py,readiness.py}`, `contracts/v2/{models.py,openapi.yaml,openapi.json,schemas/}`, `data/source/*.csv`, `data/v2/{skills,roles,resources,aliases,personas}.json`, `data/v2/fixtures/*.json`, `data/{build_seed_v2.py,build_fixtures_v2.py,run_v2_examples.py}`, `tests/test_v2.py`, `docs/PRD_v2.{pdf,docx,md}`, `.github/{workflows/ci.yml,CODEOWNERS}`.
