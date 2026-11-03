"""Runs Anitha's journey against the real reference backend and saves every request/response as a fixture (docs and frontend mocks use these)."""
import os, sys, json, pathlib
os.environ["DB_PATH"] = "/tmp/co_fixtures.db"; ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
if os.path.exists(os.environ["DB_PATH"]): os.remove(os.environ["DB_PATH"])
from fastapi.testclient import TestClient
from backend.app.main import app
FX = ROOT / "data/v2/fixtures"; c = TestClient(app); sv = lambda n, o: (FX / f"{n}.json").write_text(json.dumps(o, indent=2, ensure_ascii=False))
P = next(p for p in c.get("/api/v1/demo/personas").json()["personas"] if p["persona_id"] == "U001")
req = {k: v for k, v in P.items() if k != "persona_id"}; req.update(preferences=dict(interests=[], weekly_hours=6), motivation=dict(styles=["progress", "encouragement"], check_in="weekly"), consent=True)
sv("01_profile_create_request", req); prof = c.post("/api/v1/profiles", json=req).json(); sv("02_profile", prof); pid = prof["profile_id"]
ext = c.post(f"/api/v1/profiles/{pid}/extract").json(); sv("03_extract_response", ext)
cr = dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in ext["suggestions"]], added_skills=[]); sv("04_confirm_request", cr); sv("05_confirm_response", c.post(f"/api/v1/profiles/{pid}/confirm", json=cr).json())
rec = c.get(f"/api/v1/profiles/{pid}/recommendations").json(); sv("06_recommendations", rec)
pr = dict(role_id="R001"); sv("07_plan_request", pr); sv("08_plan_response", c.post(f"/api/v1/profiles/{pid}/plan", json=pr).json())
sv("09_progress_update_request", dict(step_order=1, percent=40)); sv("10_progress_response", c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=1, percent=40)).json())
sv("11_audit_clean", c.post(f"/api/v1/profiles/{pid}/audit", json={}).json()); sv("12_audit_canary", c.post(f"/api/v1/profiles/{pid}/audit", json=dict(canary=True)).json())
sv("13_readiness", c.post("/api/v1/readiness/check", json=dict(text="Freshers wanted. Up to 3 years of experience. Energetic team player.")).json())
bad = dict(req, age=45); sv("14_error_forbidden_field", c.post("/api/v1/profiles", json=bad).json()); sv("15_error_consent", c.post("/api/v1/profiles", json=dict(req, consent=False)).json())
sv("16_meta", c.get("/api/v1/meta").json()); print("fixtures", len(list(FX.glob("[0-9]*.json"))))
