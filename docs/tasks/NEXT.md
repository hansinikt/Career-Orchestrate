# NEXT TASK: V2 Orchestrator and agent trace (PRD v3, sections 3 and 6)

Brief: docs/briefs/out/02_BACKEND_BRIEF.md. Allowed files: `backend/app/*`, `backend/app/schema.sql`, `contracts/v2/models.py` (ADDITIVE ONLY: new models, no changed fields), `tests/test_v3.py`, `tools_export_v2.py` outputs via `make contracts`.

## Goal
Add an orchestrator that records which agent did what, and expose it so the frontend can show a "Which agents worked on this" panel.

## Build
1. New table `agent_trace` in `schema.sql` (id, profile_id, agent, mode, input_summary, output_summary, stopped_at_gate, created_at) with ON DELETE CASCADE from profiles, like the other tables.
2. New module `backend/app/orchestrator.py` with one function `record(profile_id, agent, mode, input_summary, output_summary, stopped_at_gate=False)`. Agent names are exactly: `skills_discovery`, `inclusive_matching`, `learning_pathway`, `bias_audit`, `human_in_the_loop`. (There is no `market_intelligence` yet; do not record it.)
3. Call `record` from the existing routes, only where that work really happened: extract -> skills_discovery (mode = the extraction_mode, `rules` today); confirm -> human_in_the_loop (summary: how many accepted, edited, rejected); recommendations -> inclusive_matching; plan -> human_in_the_loop (role chosen) then learning_pathway; audit -> bias_audit. Summaries are one short line built from numbers already in the response. Never put the worker's text or name in a summary.
4. New contract models (additive): `AgentStep` and `TraceResponse` (profile_id, steps in time order). New route `GET /api/v1/profiles/{profile_id}/trace`. Unknown profile -> NOT_FOUND as usual.
5. `make contracts` to regenerate OpenAPI. Do not edit generated files by hand.

## Done when
- `make test` passes (the existing 41 plus new tests in `tests/test_v3.py`: a full Anitha journey leaves exactly the expected steps in order; trace for unknown profile is 404 NOT_FOUND; deleting the profile deletes its trace; no step text contains the worker's name).
- Anitha's locked numbers are unchanged (0.7877, 24 hours).
- You list every assumption.

## Not in this task
No frontend changes, no language-model calls, no new libraries. Tell the person if the contract change needs agreement from the other developers (it is additive, but the contract is frozen until all four agree).
