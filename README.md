# Career Orchestrator 

An evidence-led career-transition assistant for experienced administrative workers. Read `docs/PRD_v2.pdf` first (sections 1 to 4, 13 and 14), then `AGENTS.md`.

## Run it in 5 minutes
```
make setup      # Python 3.11+; creates .venv and installs pinned requirements
make test       # expect: 41 passed
make run        # API on http://localhost:8000 ; try every endpoint at /docs
```
No keys, no internet and no SAP account are needed. `cp .env.example .env` is optional.

## Demo mode (one process, offline)
Build the frontend, copy the build to `frontend_dist/`, then `make demo` and open http://localhost:8000.

## Where things are
| Folder | What | Owner |
|---|---|---|
| `contracts/v2/models.py` | The contract (frozen). OpenAPI is generated from it | all four |
| `engine/` | Algorithms: suggestions, matching, plan, motivation, openness check | Dev 3 |
| `backend/app/` | Routes and SQLite | Dev 2 |
| `data/v2/` | Catalogue from the team's CSVs, fixtures | Dev 3 (`resources.json`: Dev 4) |
| `frontend/` | Plain HTML/CSS/JS app, served by the backend at http://localhost:8000/ | Dev 1 |
| `database/` | SQL scripts (run in numeric order) | |
| `tests/` | 41 tests | Dev 4 |

Files listed in `LEGACY_V1.md` are old and must be ignored.
