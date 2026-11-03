# Milestones (IST). Today = Sat 31 Oct 2026. Freeze = Tue 3 Nov 12:00.
| ID | Target | Done when (all must be true) |
|---|---|---|
| G0 | Sat 31 Oct 15:00 | Frontend inventory filled (PRD s33); SAP/LLM access checks run and answers recorded (PRD s54); repo created with this skeleton; roles assigned |
| M1 Contract + mock | Sat 31 Oct 22:00 | `make mock` serves all 16 paths; `make test` green in CI; frontend renders profile form -> skills screen from mock; contracts tagged v1.0 |
| M2 Real engine on fixtures | Sun 1 Nov 14:00 | Backend serves same paths with SQLite persistence; deterministic stages (match, plan) run from real code; contract tests pass against BOTH mock and real; frontend switched by env var only |
| M3 Real extraction | Sun 1 Nov 22:00 | LLMClient + Skills Discovery live and in replay; grounding validators enforced; skill-confirmation screen works end-to-end; first full run in staging |
| M4 Readiness + audit | Mon 2 Nov 14:00 | Employer Readiness and Bias Audit real (replay + live); audit screen incl. canary; failure-injection tests pass; P0 feature complete |
| M5 Hardened | Mon 2 Nov 20:00 | 10 consecutive full runs pass in replay; >=8/10 live; latency table recorded; catalog URLs verified (link check); P1 cut-off passed |
| FREEZE | Tue 3 Nov 12:00 | Tag `v1.0-demo`; only P0 bug fixes with 2 approvals after this point |
| M6 Demo ready | Tue 3 Nov 18:00 | 3 consecutive rehearsals (live + replay) under 10 min; backup video recorded; laptop dry-run with projector connector; README reproduces from clean clone |
