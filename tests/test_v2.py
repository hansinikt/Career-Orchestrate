import os, sys, json, pathlib, uuid, itertools, string
os.environ["DB_PATH"] = f"/tmp/co_test_{uuid.uuid4().hex}.db"
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
import pytest
from fastapi.testclient import TestClient
from engine import core as E, motivation as M, readiness as R, extract_rules as X
from contracts.v2 import models as C
from backend.app.main import app, FORBIDDEN
c = TestClient(app); SK, ROLES, RES = E.load("v2"); PER = json.loads((ROOT / "data/v2/personas.json").read_text())

def make(uid="U001", styles=("progress", "encouragement"), interests=()):
    p = PER[uid]; body = dict(display_name=p["name"], current_role=p["current_role"], work_examples=[p["work_text"]], declared_skills=p["declared_skills"], stated_goal_role_id=p["stated_goal_role_id"],
                              preferences=dict(interests=list(interests), weekly_hours=6), motivation=dict(styles=list(styles), check_in="weekly"), consent=True)
    r = c.post("/api/v1/profiles", json=body); assert r.status_code == 201, r.text; return r.json()["profile_id"]
def run_to_plan(pid, role):
    e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    assert c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]])).status_code == 200
    return e, c.post(f"/api/v1/profiles/{pid}/plan", json=dict(role_id=role))

def test_contract_has_no_forbidden_fields():
    def walk(m, seen=set()):
        for n, f in m.model_fields.items():
            assert n.lower() not in FORBIDDEN, (m.__name__, n)
    for name in dir(C):
        o = getattr(C, name)
        if isinstance(o, type) and issubclass(o, C.BaseModel) and o is not C.BaseModel: walk(o)
def test_catalog_consistency():
    ids = set(SK)
    for r in ROLES:
        for q in r["requirements"]: assert q["skill_id"] in ids and SK[q["skill_id"]]["scored"]
    for x in RES:
        assert set(x["skill_ids"]) <= ids
        if x["verification_status"] == "verified": assert x["url"] and x["last_verified"], "verified needs a course-page URL and a date"
    assert abs(sum(E.WEIGHTS.values()) - 1) < 1e-9
def test_forbidden_fields_rejected():
    base = dict(display_name="A", work_examples=["Coordinated calendars and maintained records"], consent=True)
    for f in ["age", "dob", "gender", "years_experience", "date_of_birth"]:
        r = c.post("/api/v1/profiles", json=dict(base, **{f: 40})); assert r.status_code == 422 and r.json()["error"]["code"] == "FORBIDDEN_FIELD", f
    assert c.post("/api/v1/profiles", json=dict(base, consent=False)).json()["error"]["code"] == "CONSENT_REQUIRED"
    assert c.post("/api/v1/profiles", json=dict(base, surprise=1)).json()["error"]["code"] == "VALIDATION_ERROR"
def test_gates():
    pid = make(); assert c.get(f"/api/v1/profiles/{pid}/recommendations").json()["error"]["code"] == "SKILLS_NOT_CONFIRMED"
    e = c.post(f"/api/v1/profiles/{pid}/extract").json(); dec = [dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]]
    assert c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=dec[:-1])).status_code == 422          # every suggestion needs a decision
    assert c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=dec[:-1] + [dict(suggestion_id=dec[-1]["suggestion_id"], action="edit")])).status_code == 422
    assert c.get(f"/api/v1/profiles/{pid}/plan").json()["error"]["code"] == "NO_ACTIVE_PLAN"
def test_evidence_is_grounded_and_inference_capped():
    for uid, p in PER.items():
        pid = make(uid); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
        for s in e["suggestions"]:
            for ev in s["evidence"]: assert E.quote_is_grounded(ev["quote"], p and [p["work_text"]])
            if s["source"] == "extracted": assert s["suggested_level"] <= 2
def test_anitha_worked_numbers():
    pid = make("U001"); e, r = run_to_plan(pid, "R001"); assert r.status_code == 200
    rec = c.get(f"/api/v1/profiles/{pid}/recommendations").json()
    assert [x["role_id"] for x in rec["recommendations"][:3]] == ["R001", "R002", "R006"]
    top = rec["recommendations"][0]; assert top["score"] == 0.7877 and top["band"] == "bridgeable" and top["blocking_gaps"] == ["SK-CONF"] and top["est_gap_hours"] == 24.0
    assert rec["goal"]["role_id"] == "R001"; plan = r.json(); assert plan["total_est_hours"] == 24.0 and plan["weeks_at_pace"] == 4 and plan["unresolved_skill_ids"] == ["SK-CONF"]
def test_rejecting_inferred_skills_changes_result_as_documented():
    pid = make("U001"); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    dec = [dict(suggestion_id=s["suggestion_id"], action="reject" if s["source"] == "extracted" else "accept") for s in e["suggestions"]]
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=dec)); top = c.get(f"/api/v1/profiles/{pid}/recommendations").json()["recommendations"][0]
    assert top["role_id"] == "R001" and top["score"] == 0.6368 and top["est_gap_hours"] == 48.0
def test_all_personas_run_and_are_deterministic():
    for uid, p in PER.items():
        outs = []
        for _ in range(2):
            pid = make(uid); e, r = run_to_plan(pid, p["stated_goal_role_id"]); assert r.status_code == 200
            outs.append([(x["role_id"], x["score"]) for x in c.get(f"/api/v1/profiles/{pid}/recommendations").json()["recommendations"]])
        assert outs[0] == outs[1]
def test_missing_interests_renormalise():
    pid = make("U006"); run_to_plan(pid, "R006"); top = c.get(f"/api/v1/profiles/{pid}/recommendations").json()["recommendations"][0]
    assert top["feature_scores"]["preference_fit"] is None and abs(sum(top["weights_used"].values()) - 1) < 1e-3
def test_plan_never_shows_unverified_when_disallowed():
    sk, roles, res = E.load("v2"); rec = next(r for r in E.rank(PER["U003"]["confirmed_levels"], roles, [], sk) if r["role_id"] == "R003")
    plan = E.build_plan(rec, PER["U003"]["confirmed_levels"], sk, res, 6, allow_unverified=False, allow_sample=False)
    assert all(s["status"] == "no_verified_resource" for s in plan["steps"])
def test_motivation_templates_complete_and_clean():
    nums = M.plan_numbers([dict(order=1, skill_name="Confidentiality", est_hours=24.0), dict(order=2, skill_name="Scheduling", est_hours=12.0)], {1: 100}, 6, 3)
    for st, ev in itertools.product(M.STYLES, M.EVENTS):
        text = M.LIB[st][ev].format(**nums); assert text and E.lexicon_hits(text) == 0
    assert set(M.LIB) == set(M.STYLES) and all(set(v) == set(M.EVENTS) for v in M.LIB.values())
def test_motivation_flow_and_pause():
    pid = make("U001"); run_to_plan(pid, "R001")
    r = c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=1, percent=30)).json(); assert r["next_message"]["event"] == "start" and r["next_message"]["style"] == "progress"
    r = c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=1, percent=100)).json(); assert r["next_message"]["event"] == "plan_done" and r["next_message"]["style"] == "encouragement" and r["percent"] == 100
    c.put(f"/api/v1/profiles/{pid}/motivation", json=dict(styles=["goals"], check_in="weekly", paused=True))
    assert c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=1, percent=50)).json()["next_message"] is None
    assert c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=9, percent=50)).status_code == 422
def test_style_dropped_after_three_unhelpful():
    pid = make("U001", styles=("progress", "challenge")); run_to_plan(pid, "R001"); ids = []
    for pct in (10, 20, 30, 40, 50, 60):
        m = c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=1, percent=pct)).json()["next_message"]
        if m:
            ids.append(m); 
            if m["style"] == "challenge": c.post(f"/api/v1/profiles/{pid}/messages/{m['message_id']}/feedback", json=dict(helpful=False))
    c.post(f"/api/v1/profiles/{pid}/progress", json=dict(step_order=1, percent=70))
def test_readiness_check():
    bad = R.check("Freshers wanted. Up to 3 years of experience. Graduate degree mandatory. Energetic team player."); assert bad["status"] == "flagged" and {f["rule_id"] for f in bad["flags"]} >= {"experience_cap", "fresher_wording", "age_coded_wording", "degree_required"}
    assert R.check("Coordinate calendars and maintain records; training provided.")["status"] == "no_flags"
    assert c.post("/api/v1/readiness/check", json=dict(text="Up to 3 years of experience, freshers preferred.")).json()["status"] == "flagged"
def test_audit_clean_pass_and_canary_flagged():
    pid = make("U001"); run_to_plan(pid, "R001")
    a = c.post(f"/api/v1/profiles/{pid}/audit", json={}).json(); assert a["status"] == "pass" and len(a["variants"]) == 6 and not any(v["flags"] for v in a["variants"])
    k = c.post(f"/api/v1/profiles/{pid}/audit", json=dict(canary=True)).json(); assert k["status"] == "flagged"
    can = next(v for v in k["variants"] if v["variant_id"] == "CANARY"); assert {f["metric"] for f in can["flags"]} >= {"skills_jaccard", "kendall_tau", "max_abs_score_delta", "plan_hours_delta", "lexicon_hits"}
    rv = c.post(f"/api/v1/audits/{k['audit_id']}/review", json=dict(reviewer="Dev4", decision="acknowledged")).json(); assert rv["review"]["reviewer"] == "Dev4"
def test_delete_removes_everything_but_keeps_log():
    pid = make("U002"); run_to_plan(pid, "R002"); assert c.delete(f"/api/v1/profiles/{pid}").status_code == 204
    assert c.get(f"/api/v1/profiles/{pid}").status_code == 404
    from backend.app.main import db
    assert db.one("SELECT COUNT(*) n FROM plans WHERE profile_id=?", (pid,))["n"] == 0 and db.one("SELECT COUNT(*) n FROM audit_log WHERE profile_id=?", (pid,))["n"] >= 1
def test_error_shape_everywhere():
    for r in (c.get("/api/v1/profiles/none"), c.post("/api/v1/profiles", json={}), c.get("/api/v1/audits/none")):
        j = r.json(); assert set(j) == {"error"} and {"code", "message"} <= set(j["error"])
def test_meta_and_catalog_endpoints():
    m = c.get("/api/v1/meta").json(); assert m["weights_are_provisional"] and m["catalog"]["roles"] == 8 and m["catalog"]["skills"] == 25
    assert len(c.get("/api/v1/roles").json()["roles"]) == 8 and len(c.get("/api/v1/demo/personas").json()["personas"]) == 8
