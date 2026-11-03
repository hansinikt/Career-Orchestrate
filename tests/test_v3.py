import os, sys, json, pathlib, uuid, base64
os.environ["DB_PATH"] = f"/tmp/co_test3_{uuid.uuid4().hex}.db"; os.environ["APP_MODE"] = "replay"; os.environ["RATE_LIMIT_PER_MIN"] = "100000"
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import llm, agents as A
from engine import core as E, market as MK
c = TestClient(app); SK, ROLES, RES = E.load("v2"); PER = json.loads((ROOT / "data/v2/personas.json").read_text())

def make(uid="U001"):
    p = PER[uid]; body = dict(display_name=p["name"], current_role=p["current_role"], work_examples=[p["work_text"]], declared_skills=p["declared_skills"], stated_goal_role_id=p["stated_goal_role_id"],
                              preferences=dict(interests=[], weekly_hours=6), motivation=dict(styles=["progress", "encouragement"], check_in="weekly"), consent=True)
    r = c.post("/api/v1/profiles", json=body); assert r.status_code == 201, r.text; return r.json()["profile_id"], p
def confirm(pid):
    e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    assert c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]])).status_code == 200
    return e
def journey(uid="U001", role="R001"):
    pid, p = make(uid); confirm(pid); c.get(f"/api/v1/profiles/{pid}/recommendations"); r = c.post(f"/api/v1/profiles/{pid}/plan", json=dict(role_id=role)); assert r.status_code == 200, r.text; return pid, p, r.json()

def test_trace_after_full_journey_is_in_order():
    pid, p, plan = journey(); c.post(f"/api/v1/profiles/{pid}/audit"); steps = c.get(f"/api/v1/profiles/{pid}/trace").json()["steps"]
    assert [(s["agent"], s["stopped_at_gate"]) for s in steps] == [("skills_discovery", False), ("human_in_the_loop", True), ("inclusive_matching", False), ("human_in_the_loop", True), ("learning_pathway", False), ("bias_audit", False)]
    assert [s["step"] for s in steps] == list(range(1, 7))
def test_trace_never_contains_worker_text_or_name():
    pid, p, _ = journey(); blob = json.dumps(c.get(f"/api/v1/profiles/{pid}/trace").json()).lower()
    assert p["name"].lower() not in blob and p["work_text"][:25].lower() not in blob
def test_trace_unknown_profile_404():
    r = c.get("/api/v1/profiles/prof_nope/trace"); assert r.status_code == 404 and r.json()["error"]["code"] == "NOT_FOUND"
def test_delete_profile_deletes_trace():
    from backend.app.main import db
    pid, _, _ = journey(); assert db.one("SELECT COUNT(*) n FROM agent_trace WHERE profile_id=?", (pid,))["n"] > 0
    assert c.delete(f"/api/v1/profiles/{pid}").status_code == 204; assert db.one("SELECT COUNT(*) n FROM agent_trace WHERE profile_id=?", (pid,))["n"] == 0
def test_repeated_recommendations_do_not_duplicate_trace():
    pid, _ = make(); confirm(pid)
    for _ in range(3): c.get(f"/api/v1/profiles/{pid}/recommendations")
    assert sum(1 for s in c.get(f"/api/v1/profiles/{pid}/trace").json()["steps"] if s["agent"] == "inclusive_matching") == 1

# ---- Skills Discovery agent: the model's answer is checked in code ----
def fake(monkeypatch, payload): monkeypatch.setattr(llm, "ask_json", lambda task, system, user: (payload, "live") if payload is not None else (None, None))
def test_discovery_keeps_only_grounded_quotes_and_catalogue_ids(monkeypatch):
    text = PER["U001"]["work_text"]; quote = text[:20]; sid = next(iter(k for k, v in SK.items() if v["scored"]))
    fake(monkeypatch, dict(skills=[dict(skill_id=sid, level=2, quote=quote), dict(skill_id=sid, level=2, quote="words the worker never wrote"), dict(skill_id="SK-INVENTED", level=2, quote=quote)]))
    got = A.skills_discovery([text], SK); assert [g["skill_id"] for g in got] == [sid] and got[0]["quote"] in text
def test_discovery_falls_back_when_model_unavailable(monkeypatch):
    fake(monkeypatch, None); pid, _ = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json(); assert e["extraction_mode"] == "rules" and e["suggestions"]
def test_discovery_adds_agent_findings_and_marks_mode(monkeypatch):
    pid, p = make(); texts = p["work_text"]; sid = "SK-PRESENT" if "SK-PRESENT" in SK else None
    base = c.post(f"/api/v1/profiles/{pid}/extract").json(); have = {s["skill_id"] for s in base["suggestions"]}
    new = next(k for k, v in SK.items() if v["scored"] and k not in have)
    fake(monkeypatch, dict(skills=[dict(skill_id=new, level=2, quote=texts[:15])])); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    assert e["extraction_mode"] == "llm+rules" and any(s["skill_id"] == new and s["evidence"][0]["quote"] in texts for s in e["suggestions"])
    assert all(e_["quote"] in texts for s in e["suggestions"] for e_ in s["evidence"])
def test_discovery_ignores_prompt_injection_shape(monkeypatch):
    fake(monkeypatch, "not a dict"); assert A.skills_discovery(["I coordinated schedules"], SK) is None
    fake(monkeypatch, dict(skills="oops")); assert A.skills_discovery(["I coordinated schedules"], SK) is None

# ---- Market Intelligence ----
def test_market_counts_come_from_catalogue():
    pid, _, _ = journey(); m = c.get(f"/api/v1/profiles/{pid}/market").json()
    assert m["roles_in_catalogue"] == len(ROLES) and m["held"] and "not live job-market data" in m["source_note"]
    for row in m["held"] + m["next_skills"]: assert row["roles_asking"] == sum(1 for r in ROLES if any(q["skill_id"] == row["skill_id"] for q in r["requirements"]))
    held = {r["skill_id"] for r in m["held"]}; assert not held & {r["skill_id"] for r in m["next_skills"]}
def test_market_needs_confirmed_skills():
    pid, _ = make(); r = c.get(f"/api/v1/profiles/{pid}/market"); assert r.status_code == 409 and r.json()["error"]["code"] == "SKILLS_NOT_CONFIRMED"

# ---- Course Scout ----
def test_scout_rules_picks_only_catalogue_courses():
    pid, _, plan = journey(); s = c.post(f"/api/v1/profiles/{pid}/scout").json(); ids = {r["resource_id"] for r in RES}
    assert s["steps"] and all((x["pick_resource_id"] in ids) or x["pick_resource_id"] is None for x in s["steps"])
    for x in s["steps"]: assert all(cand["skill_ids"] and x["skill_id"] in cand["skill_ids"] for cand in x["candidates"])
def test_scout_rejects_invented_course_and_invented_numbers(monkeypatch):
    pid, _, plan = journey(); st = plan["steps"][0]
    fake(monkeypatch, dict(picks=[dict(order=st["order"], resource_id="C999", reason="great"), ])); s = c.post(f"/api/v1/profiles/{pid}/scout").json()
    assert s["steps"][0]["pick_resource_id"] != "C999" and s["steps"][0]["decided_by"] == "rules"
    cand = s["steps"][0]["candidates"]
    if cand:
        fake(monkeypatch, dict(picks=[dict(order=st["order"], resource_id=cand[0]["resource_id"], reason="Takes 777 hours and is loved by 98% of learners")])); s2 = c.post(f"/api/v1/profiles/{pid}/scout").json()
        assert s2["steps"][0]["decided_by"] == "rules"
        fake(monkeypatch, dict(picks=[dict(order=st["order"], resource_id=cand[0]["resource_id"], reason="Matches this skill and level.")])); s3 = c.post(f"/api/v1/profiles/{pid}/scout").json()
        assert s3["steps"][0]["decided_by"] == "agent" and s3["mode"] == "agent"
def test_scout_approve_changes_plan_and_checks_skill():
    for rid in [r["role_id"] for r in ROLES]:
        pid, _, plan = journey("U001", rid); s = c.post(f"/api/v1/profiles/{pid}/scout").json(); x = next((x for x in s["steps"] if x["candidates"]), None)
        if x: break
    assert x, "no catalogue role has a step with a candidate course"
    ok = c.post(f"/api/v1/profiles/{pid}/scout/approve", json=dict(choices=[dict(order=x["order"], resource_id=x["candidates"][0]["resource_id"])]))
    assert ok.status_code == 200 and next(st for st in ok.json()["steps"] if st["order"] == x["order"])["resource"]["resource_id"] == x["candidates"][0]["resource_id"]
    assert c.get(f"/api/v1/profiles/{pid}/plan").json()["steps"][x["order"] - 1]["resource"]["resource_id"] == x["candidates"][0]["resource_id"]
    other = next(r for r in RES if x["skill_id"] not in r["skill_ids"])
    bad = c.post(f"/api/v1/profiles/{pid}/scout/approve", json=dict(choices=[dict(order=x["order"], resource_id=other["resource_id"])])); assert bad.status_code == 422
    assert any(t["agent"] == "human_in_the_loop" and t["mode"] == "gate_3_approve_courses" for t in c.get(f"/api/v1/profiles/{pid}/trace").json()["steps"])

# ---- Missions and proof ----
def test_missions_and_proof_flow():
    pid, _, plan = journey(); m = c.get(f"/api/v1/profiles/{pid}/missions").json(); assert m["missions"] and m["today_mission_id"] == m["missions"][0]["mission_id"]
    mid = m["today_mission_id"]; body = dict(file_name="note.txt", content_base64=base64.b64encode(b"my paragraph").decode())
    r = c.post(f"/api/v1/profiles/{pid}/missions/{mid}/proof", json=body); assert r.status_code == 200
    got = next(x for x in r.json()["missions"] if x["mission_id"] == mid); assert got["status"] == "done" and got["proof_name"] == "note.txt"
    assert c.post(f"/api/v1/profiles/{pid}/missions/{mid}/proof", json=dict(file_name="x.exe", content_base64="QQ==")).status_code == 422
    assert c.post(f"/api/v1/profiles/{pid}/missions/{mid}/proof", json=dict(file_name="x.txt", content_base64="***")).status_code == 422
    assert c.post(f"/api/v1/profiles/{pid}/missions/m99/proof", json=body).status_code == 404
def test_proof_filename_path_is_stripped():
    pid, _, _ = journey(); mid = c.get(f"/api/v1/profiles/{pid}/missions").json()["today_mission_id"]
    r = c.post(f"/api/v1/profiles/{pid}/missions/{mid}/proof", json=dict(file_name="../../etc/passwd.txt", content_base64="QQ==")); assert r.status_code == 200
    assert next(x for x in r.json()["missions"] if x["mission_id"] == mid)["proof_name"] == "passwd.txt"

# ---- Security basics and locked numbers ----
def test_security_headers_present():
    h = c.get("/api/v1/health").headers; assert h["x-content-type-options"] == "nosniff" and "frame-ancestors 'none'" in h["content-security-policy"] and h["cache-control"] == "no-store"
def test_oversize_body_rejected():
    r = c.post("/api/v1/readiness/check", content=b"x" * 10, headers={"content-length": "9000000", "content-type": "application/json"}); assert r.status_code == 413
def test_anitha_numbers_unchanged():
    pid, p, plan = journey("U001", "R001"); top = c.get(f"/api/v1/profiles/{pid}/recommendations").json()["recommendations"][0]
    assert top["score"] == pytest.approx(0.7877, abs=1e-4) and plan["total_est_hours"] == 24
def test_rate_limit_on_model_endpoints(monkeypatch):
    from backend.app import main as M
    monkeypatch.setenv("RATE_LIMIT_PER_MIN", "2"); M._hits.clear(); pid, _ = make()
    codes = [c.post(f"/api/v1/profiles/{pid}/extract").status_code for _ in range(4)]; assert codes[:2] == [200, 200] and codes[2:] == [429, 429]; M._hits.clear()

# ---- Encouragement: the model may only re-word a template; every fact must stay ----
ORIG = "Well done on finishing 'Confidentiality'. Your plan is 50% done, with about 12 hours to go."
def test_polish_accepts_safe_rewrite(monkeypatch):
    fake(monkeypatch, dict(text="Lovely work finishing 'Confidentiality'! You are 50% of the way, with about 12 hours to go.")); assert A.polish(ORIG, "encouragement").startswith("Lovely work")
def test_polish_rejects_invented_number(monkeypatch):
    fake(monkeypatch, dict(text="Lovely work finishing 'Confidentiality'! You are 99% done.")); assert A.polish(ORIG, "encouragement") == ORIG
def test_polish_rejects_promises(monkeypatch):
    for w in ("You will get hired soon", "A job is guaranteed", "Your chance is high", "The probability is good"):
        fake(monkeypatch, dict(text=f"Great work on 'Confidentiality'. {w}. 50% and 12 hours.")); assert A.polish(ORIG, "encouragement") == ORIG, w
def test_polish_rejects_lost_quoted_name_and_bad_shapes(monkeypatch):
    fake(monkeypatch, dict(text="Great work finishing the course. 50% done, about 12 hours to go.")); assert A.polish(ORIG, "encouragement") == ORIG
    for bad in (123, dict(text=5), dict(other="x"), "text", dict(text="")):
        fake(monkeypatch, bad); assert A.polish(ORIG, "encouragement") == ORIG
def test_polish_is_used_by_the_progress_message(monkeypatch):
    pid, _, _ = journey(); fake(monkeypatch, dict(text="Wonderful: your plan is complete, all 1 step done and about 24 hours of learning to be proud of."))
    assert c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=1, percent=100)).json()["next_message"]["text"].startswith("Wonderful: your plan is complete")
    pid2, _, _ = journey(); fake(monkeypatch, dict(text="Wonderful: all 3 steps done and about 99 hours!"))
    assert c.post(f"/api/v1/profiles/{pid2}/progress", json=dict(step_order=1, percent=100)).json()["next_message"]["text"].startswith("Plan complete: all 1 step done")
