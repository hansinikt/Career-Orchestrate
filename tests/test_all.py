import json, pathlib, sys
import pytest
from fastapi.testclient import TestClient
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
from contracts import models as M
from engine import core as E
from mock_api.app import app
FX = ROOT / "data" / "fixtures"; c = TestClient(app); P = "/api/v1"
sk, roles, res = E.load(); user = json.loads((FX / "gold_user_levels.json").read_text())

# ---- contract tests: every golden fixture validates against canonical models ----
MODEL = {"career_profile": M.CareerProfile, "skill_extraction_result": M.SkillExtractionResult, "learning_plan": M.LearningPlan,
         "employer_readiness_result": M.EmployerReadinessResult, "bias_audit_result_pass": M.BiasAuditResult,
         "bias_audit_result_canary_flagged": M.BiasAuditResult, "workflow_state_awaiting_confirmation": M.WorkflowState,
         "workflow_state_completed": M.WorkflowState, "workflow_results": M.WorkflowResults, "api_error": M.APIErrorResponse}
@pytest.mark.parametrize("name", MODEL)
def test_fixture_matches_contract(name): MODEL[name].model_validate_json((FX / f"{name}.json").read_text())
def test_recommendations_fixture():
    for r in json.loads((FX / "role_recommendations.json").read_text()): M.RoleRecommendation.model_validate(r)
def test_no_age_fields_in_contract():
    bad = {"age", "dob", "date_of_birth", "birth_year", "gender", "graduation_year"}
    for m in (M.CareerProfileInput, M.WorkEntry, M.Preferences): assert not bad & set(m.model_fields)

# ---- mock API walk-through (same sequence the real backend must support) ----
def test_full_flow_on_mock():
    pid = c.post(f"{P}/profiles", json=json.loads((FX / "career_profile.json").read_text()) | {}).json()
    body = json.loads((FX / "career_profile.json").read_text())
    for k in ("profile_id", "created_at", "updated_at", "is_synthetic"): body.pop(k)
    r = c.post(f"{P}/profiles", json=body); assert r.status_code == 201; pid = r.json()["profile_id"]
    w = c.post(f"{P}/workflows", json={"profile_id": pid}); assert w.status_code == 202; wid = w.json()["workflow_id"]
    assert c.get(f"{P}/workflows/{wid}").json()["status"] == "AWAITING_USER"
    assert c.post(f"{P}/workflows/{wid}/role-selection", json={"role_ids": ["R-001"]}).status_code == 409   # wrong state
    conf = json.loads((FX / "skill_confirmation_request.json").read_text()); assert c.post(f"{P}/workflows/{wid}/skills/confirmation", json=conf).status_code == 202
    assert c.get(f"{P}/workflows/{wid}").json()["current_stage"] == "select_role"
    assert c.post(f"{P}/workflows/{wid}/role-selection", json={"role_ids": ["R-001"]}).status_code == 202
    c.get(f"{P}/workflows/{wid}"); M.WorkflowResults.model_validate(c.get(f"{P}/workflows/{wid}/results").json())
def test_consent_required_and_error_shape():
    body = json.loads((FX / "career_profile.json").read_text()); [body.pop(k) for k in ("profile_id", "created_at", "updated_at", "is_synthetic")]
    body["consent"]["given"] = False; r = c.post(f"{P}/profiles", json=body); assert r.status_code == 400
    M.APIErrorResponse.model_validate(r.json()); assert r.json()["error"]["code"] == "CONSENT_REQUIRED"
def test_unknown_profile_404(): assert c.post(f"{P}/workflows", json={"profile_id": "nope"}).status_code == 404

# ---- engine unit tests ----
def test_ranking_deterministic():
    a = E.rank(user, roles, ["data", "operations", "planning"], sk); b = E.rank(user, roles, ["data", "operations", "planning"], sk)
    assert [(r["role_id"], r["score"]) for r in a] == [(r["role_id"], r["score"]) for r in b]
def test_missing_preferences_renormalise_not_zero():
    r = E.score_role(user, roles[0], [], sk); assert r["feature_scores"]["preference_fit"] is None; assert abs(sum(r["weights_used"].values()) - 1) < 1e-3
def test_forbidden_features_not_in_scoring_signature():
    import inspect; params = set(inspect.signature(E.score_role).parameters)
    assert not (E.FORBIDDEN_FEATURES & params)
def test_unconfirmed_skills_never_count():
    assert E.score_role({}, roles[0], [], sk)["feature_scores"]["skill_coverage"] == 0
def test_grounding_validators():
    src = ["a team of 12 and 3% growth"]
    assert E.quote_is_grounded("team  of 12", src) and not E.quote_is_grounded("team of 15", src)
    assert E.ungrounded_numbers("Led a team of 12.", src) == [] and E.ungrounded_numbers("Saved 40%", src) == ["40%"]
def test_plan_marks_unresolved_instead_of_inventing():
    rec = next(r for r in E.rank(user, roles, [], sk) if r["role_id"] == "R-001"); p = E.build_plan(rec, user, sk, res, 6)
    assert "SK-SQL" in p["unresolved_skill_ids"] and all(s["resource"] is None for s in p["steps"] if s["status"] == "no_verified_resource")
def test_plan_orders_prerequisites_first():
    rec = next(r for r in E.rank(user, roles, [], sk) if r["role_id"] == "R-001"); order = [s["skill_id"] for s in E.build_plan(rec, user, sk, res, 6)["steps"]]
    assert order.index("SK-SQL") >= 0 and all(order.index(s) < order.index("SK-BI") for s in order if s == "SK-SPREADSHEET")
# ---- fairness: clean passes, canary (deliberately biased) MUST flag ----
def test_audit_clean_passes_and_canary_flags():
    assert M.BiasAuditResult.model_validate_json((FX / "bias_audit_result_pass.json").read_text()).verdict == "pass"
    can = M.BiasAuditResult.model_validate_json((FX / "bias_audit_result_canary_flagged.json").read_text())
    assert can.verdict == "flag" and {f.variant_id for f in can.flags} == {"A58"}
