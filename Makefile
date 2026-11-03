.PHONY: setup test contracts contracts-check run seed fixtures demo
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
setup:           ; $(PYTHON) -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt
test:            ; $(PYTHON) -m pytest -q tests
seed:            ; $(PYTHON) data/build_seed_v2.py
fixtures:        ; $(PYTHON) data/build_fixtures_v2.py
contracts:       ; $(PYTHON) tools_export_v2.py
contracts-check: ; $(PYTHON) tools_export_v2.py && git diff --exit-code contracts/v2/openapi.yaml contracts/v2/schemas
run:             ; uvicorn backend.app.main:app --port 8000 --reload
demo:            ; APP_MODE=replay uvicorn backend.app.main:app --port 8000
