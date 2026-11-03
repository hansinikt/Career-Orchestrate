import os, sys, json, pathlib, uuid
os.environ["DB_PATH"] = f"/tmp/co_test5_{uuid.uuid4().hex}.db"; os.environ["APP_MODE"] = "replay"; os.environ["RATE_LIMIT_PER_MIN"] = "100000"
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import llm
from engine import paths as PT
c = TestClient(app); DATA = json.loads((ROOT / "data/v2/role_courses.json").read_text()); PER = json.loads((ROOT / "data/v2/personas.json").read_text())

def journey():
    p = PER["U001"]; body = dict(display_name=p["name"], current_role=p["current_role"], work_examples=[p["work_text"]], declared_skills=p["declared_skills"], stated_goal_role_id=p["stated_goal_role_id"],
                                 preferences=dict(interests=[], weekly_hours=6), motivation=dict(styles=["progress"], check_in="weekly"), consent=True)
    pid = c.post("/api/v1/profiles", json=body).json()["profile_id"]; e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]])); return pid

def test_every_course_has_a_page_url_and_is_unverified():
    for x in DATA["courses"]:
        assert x["url"].startswith("https://") and x["verification_status"] == "seed_unverified" and x["roles"] and x["units"]
def test_path_is_simplest_first_and_has_at_most_five():
    for role in DATA["requirements"]:
        out = PT.build_path(role, DATA, {})
        ranks = [PT.LEVEL_RANK.get(x["level"], 1) for x in out["courses"]]
        assert 0 < len(out["courses"]) <= 5 and ranks == sorted(ranks)
def test_courses_that_cover_nothing_missing_are_left_out():
    out = PT.build_path("R005", DATA, {"SK-EXCEL": 3, "SK-SQL": 3, "SK-DATAANALYSIS": 3, "SK-PROCIMPROVE": 3})
    assert all(x["covers"] for x in out["courses"])
def test_sap_is_only_a_tie_break():
    out = PT.build_path("R001", DATA, {})
    assert any("SAP" in x["provider"] for x in out["courses"]) and sum("SAP" in x["provider"] for x in out["courses"]) < len(out["courses"])
def test_endpoint_returns_courses_in_contract_shape():
    pid = journey(); r = c.get(f"/api/v1/profiles/{pid}/paths/R001"); assert r.status_code == 200, r.text; j = r.json()
    assert j["role_id"] == "R001" and j["mode"] == "rules" and j["courses"] and j["requirements"]
    assert all(x["why"] and x["verification_status"] == "seed_unverified" and x["decided_by"] == "rules" for x in j["courses"])
def test_role_without_checked_courses_returns_empty_list():
    pid = journey(); j = c.get(f"/api/v1/profiles/{pid}/paths/R008").json(); assert j["courses"] == [] and "No courses" in j["source_note"]
def test_unknown_role_and_unconfirmed_profile():
    pid = journey(); assert c.get(f"/api/v1/profiles/{pid}/paths/R999").status_code == 404
    p = PER["U001"]; pid2 = c.post("/api/v1/profiles", json=dict(display_name="X", current_role="y", work_examples=[p["work_text"]], declared_skills=[], preferences=dict(interests=[], weekly_hours=6), motivation=dict(styles=["progress"], check_in="weekly"), consent=True)).json()["profile_id"]
    r = c.get(f"/api/v1/profiles/{pid2}/paths/R001"); assert r.status_code == 409 and r.json()["error"]["code"] == "SKILLS_NOT_CONFIRMED"
def _fake(monkeypatch, data): monkeypatch.setattr(llm, "ask_json", lambda task, system, user: (data, "live"))
def test_agent_reason_is_used_when_it_passes_checks(monkeypatch):
    from backend.app import agents as A; monkeypatch.setattr(A, "BLURBS", {})     # a course with no written summary falls back to the model, then to rules
    pid = journey(); first = c.get(f"/api/v1/profiles/{pid}/paths/R001").json()["courses"][0]
    _fake(monkeypatch, dict(reasons=[dict(resource_id=first["resource_id"], reason="Covers onboarding and payroll basics for HR work.")]))
    j = c.get(f"/api/v1/profiles/{pid}/paths/R001").json(); got = {x["resource_id"]: x for x in j["courses"]}
    assert got[first["resource_id"]]["decided_by"] == "agent" and j["mode"] == "agent" and all(x["decided_by"] == "rules" for k, x in got.items() if k != first["resource_id"])
def test_agent_cannot_add_reorder_or_invent_numbers(monkeypatch):
    from backend.app import agents as A; monkeypatch.setattr(A, "BLURBS", {})
    pid = journey(); base = c.get(f"/api/v1/profiles/{pid}/paths/R001").json(); ids = [x["resource_id"] for x in base["courses"]]
    _fake(monkeypatch, dict(reasons=[dict(resource_id="PC-INVENTED", reason="great"), dict(resource_id=ids[0], reason="Rated 4.99 by 88888 learners and takes 777 hours"), dict(resource_id=ids[1], reason="You will be hired for sure")]))
    j = c.get(f"/api/v1/profiles/{pid}/paths/R001").json()
    assert [x["resource_id"] for x in j["courses"]] == ids and all(x["decided_by"] == "rules" for x in j["courses"]) and j["mode"] == "rules"
