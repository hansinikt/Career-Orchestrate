"""MOCK API: serves golden fixtures through the SAME contract as the real backend. Frontend develops against this.
Run: uvicorn mock_api.app:app --port 8000   (progression is simulated: each GET /workflows/{id} advances one phase)"""
import json, pathlib, uuid, datetime
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contracts import models as M
FX = pathlib.Path(__file__).resolve().parent.parent / "data" / "fixtures"
DATA = FX.parent
load = lambda n: json.loads((FX / f"{n}.json").read_text())
app = FastAPI(title="Career Orchestrator API", version="1.0.0",
              description="Contract v1.0. Mock and real backend MUST expose identical paths, schemas and status codes.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
P = "/api/v1"
now = lambda: datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).isoformat(timespec="seconds")
PROFILES, WF, AUD = {}, {}, {}
class ApiErr(Exception):
    def __init__(s, status, code, msg, retry=False, details=None): s.status, s.code, s.msg, s.retry, s.details = status, code, msg, retry, details
@app.exception_handler(ApiErr)
async def _h(_: Request, e: ApiErr):
    return JSONResponse(status_code=e.status, content=M.APIErrorResponse(error=M.APIError(code=e.code, message=e.msg, retryable=e.retry, details=e.details, request_id="req_" + uuid.uuid4().hex[:8])).model_dump())
from fastapi.exceptions import RequestValidationError
@app.exception_handler(RequestValidationError)
async def _v(_: Request, e: RequestValidationError):
    errs = e.errors()
    if any("consent" in "/".join(map(str, x["loc"])) for x in errs):
        return await _h(_, ApiErr(400, "CONSENT_REQUIRED", "Consent must be given before a profile is stored"))
    return await _h(_, ApiErr(422, "VALIDATION_ERROR", errs[0]["msg"], details={"field": ".".join(map(str, errs[0]["loc"][1:]))}))
ERR = {400: {"model": M.APIErrorResponse}, 404: {"model": M.APIErrorResponse}, 409: {"model": M.APIErrorResponse}, 422: {"model": M.APIErrorResponse}}

@app.get(P + "/health", tags=["meta"])
def health(): return {"status": "ok", "mode": "mock"}
@app.get(P + "/meta", tags=["meta"])
def meta(): return {"api_version": "1.0.0", "mode": "mock", "taxonomy_version": "seed-0.1", "dataset_version": "seed-0.1", "llm_provider": "none"}

@app.post(P + "/profiles", status_code=201, response_model=M.CareerProfile, responses=ERR, tags=["profiles"])
def create_profile(body: M.CareerProfileInput):
    if not body.consent.given: raise ApiErr(400, "CONSENT_REQUIRED", "Consent must be given before a profile is stored")
    pid = "prof_" + uuid.uuid4().hex[:8]; p = M.CareerProfile(**body.model_dump(), profile_id=pid, created_at=now(), updated_at=now())
    PROFILES[pid] = p; return p
@app.get(P + "/profiles/{profile_id}", response_model=M.CareerProfile, responses=ERR, tags=["profiles"])
def get_profile(profile_id: str):
    if profile_id == "prof_anitha_demo": return load("career_profile")
    if profile_id not in PROFILES: raise ApiErr(404, "NOT_FOUND", "Profile not found")
    return PROFILES[profile_id]
@app.put(P + "/profiles/{profile_id}", response_model=M.CareerProfile, responses=ERR, tags=["profiles"])
def update_profile(profile_id: str, body: M.CareerProfileInput):
    if profile_id not in PROFILES: raise ApiErr(404, "NOT_FOUND", "Profile not found")
    p = M.CareerProfile(**body.model_dump(), profile_id=profile_id, created_at=PROFILES[profile_id].created_at, updated_at=now()); PROFILES[profile_id] = p; return p
@app.delete(P + "/profiles/{profile_id}", status_code=204, responses=ERR, tags=["profiles"])
def delete_profile(profile_id: str):
    PROFILES.pop(profile_id, None); return JSONResponse(status_code=204, content=None)

def _state(wid):
    w = WF[wid]; ph = w["phase"]; s = M.WorkflowState(**load("workflow_state_completed")); s.workflow_id = wid; s.profile_id = w["profile_id"]; s.updated_at = now()
    names = [x.name for x in s.stages]
    def setst(done, running=None, awaiting=None):
        for st in s.stages:
            st.status = "SUCCEEDED" if st.name in done else "RUNNING" if st.name == running else "AWAITING_USER" if st.name == awaiting else "PENDING"
    if ph <= 0: setst([], running="extract_skills"); s.status, s.current_stage = "RUNNING", "extract_skills"
    elif ph == 1: setst(["extract_skills"], awaiting="confirm_skills"); s.status, s.current_stage = "AWAITING_USER", "confirm_skills"
    elif ph == 2: setst(["extract_skills", "confirm_skills"], running="match_roles"); s.status, s.current_stage = "RUNNING", "match_roles"
    elif ph == 3: setst(["extract_skills", "confirm_skills", "match_roles"], awaiting="select_role"); s.status, s.current_stage = "AWAITING_USER", "select_role"
    elif ph == 4: setst(["extract_skills", "confirm_skills", "match_roles", "select_role"], running="learning_plan"); s.status, s.current_stage = "RUNNING", "learning_plan"
    else: setst(names); s.status, s.current_stage = "COMPLETED", None
    s.selected_role_ids = w["roles"]; return s
@app.post(P + "/workflows", status_code=202, response_model=M.WorkflowState, responses=ERR, tags=["workflows"])
def start(body: M.StartWorkflowRequest):
    if body.profile_id not in PROFILES and body.profile_id != "prof_anitha_demo": raise ApiErr(404, "NOT_FOUND", "Profile not found")
    wid = "wf_" + uuid.uuid4().hex[:8]; WF[wid] = dict(profile_id=body.profile_id, phase=0, roles=[]); return _state(wid)
@app.get(P + "/workflows/{workflow_id}", response_model=M.WorkflowState, responses=ERR, tags=["workflows"])
def get_wf(workflow_id: str):
    if workflow_id not in WF: raise ApiErr(404, "NOT_FOUND", "Workflow not found")
    w = WF[workflow_id]
    if w["phase"] in (0, 2, 4): w["phase"] += 1
    return _state(workflow_id)
@app.post(P + "/workflows/{workflow_id}/skills/confirmation", status_code=202, response_model=M.WorkflowState, responses=ERR, tags=["workflows"])
def confirm(workflow_id: str, body: M.SkillConfirmationRequest):
    if workflow_id not in WF: raise ApiErr(404, "NOT_FOUND", "Workflow not found")
    if WF[workflow_id]["phase"] != 1: raise ApiErr(409, "CONFLICT_STATE", "Workflow is not awaiting skill confirmation")
    WF[workflow_id]["phase"] = 2; return _state(workflow_id)
@app.post(P + "/workflows/{workflow_id}/role-selection", status_code=202, response_model=M.WorkflowState, responses=ERR, tags=["workflows"])
def select(workflow_id: str, body: M.RoleSelectionRequest):
    if workflow_id not in WF: raise ApiErr(404, "NOT_FOUND", "Workflow not found")
    if WF[workflow_id]["phase"] != 3: raise ApiErr(409, "CONFLICT_STATE", "Workflow is not awaiting role selection")
    WF[workflow_id].update(phase=4, roles=body.role_ids); return _state(workflow_id)
@app.post(P + "/workflows/{workflow_id}/stages/{stage}/retry", status_code=202, response_model=M.WorkflowState, responses=ERR, tags=["workflows"])
def retry(workflow_id: str, stage: M.StageName):
    if workflow_id not in WF: raise ApiErr(404, "NOT_FOUND", "Workflow not found")
    raise ApiErr(409, "CONFLICT_STATE", f"Stage {stage} is not in FAILED state")
@app.get(P + "/workflows/{workflow_id}/results", response_model=M.WorkflowResults, responses=ERR, tags=["workflows"])
def results(workflow_id: str):
    if workflow_id not in WF: raise ApiErr(404, "NOT_FOUND", "Workflow not found")
    ph = WF[workflow_id]["phase"]; full = load("workflow_results"); full["workflow_id"] = workflow_id
    if ph < 1: full.update(skills=None)
    if ph < 3: full.update(recommendations=None)
    if ph < 5: full.update(learning_plans=None, employer_readiness=None)
    if ph < 5: full.update(bias_audit=None)
    return full
@app.post(P + "/audits", status_code=202, response_model=M.BiasAuditResult, responses=ERR, tags=["audits"])
def run_audit(body: M.AuditRequest):
    a = load("bias_audit_result_pass"); a["audit_id"] = "aud_" + uuid.uuid4().hex[:8]; a["profile_id"] = body.profile_id; AUD[a["audit_id"]] = a; return a
@app.get(P + "/audits/{audit_id}", response_model=M.BiasAuditResult, responses=ERR, tags=["audits"])
def get_audit(audit_id: str):
    if audit_id == "aud_demo_canary": return load("bias_audit_result_canary_flagged")
    if audit_id not in AUD: raise ApiErr(404, "NOT_FOUND", "Audit not found")
    return AUD[audit_id]
@app.put(P + "/audits/{audit_id}/review", response_model=M.BiasAuditResult, responses=ERR, tags=["audits"])
def review(audit_id: str, body: M.ReviewRequest):
    if audit_id not in AUD: raise ApiErr(404, "NOT_FOUND", "Audit not found")
    AUD[audit_id]["reviewer"] = dict(status="reviewed", decision=body.decision, note=body.note, reviewed_at=now()); return AUD[audit_id]
@app.get(P + "/roles", response_model=list[M.RoleProfile], tags=["reference"])
def roles(): return json.loads((DATA / "roles.json").read_text())["roles"]
@app.get(P + "/roles/{role_id}", response_model=M.RoleProfile, responses=ERR, tags=["reference"])
def role(role_id: str):
    r = next((x for x in roles() if x["role_id"] == role_id), None)
    if not r: raise ApiErr(404, "NOT_FOUND", "Role not found")
    return r
@app.get(P + "/skills", tags=["reference"])
def skills(query: str = Query("", max_length=60)):
    ss = json.loads((DATA / "skills.json").read_text())["skills"]; q = query.lower()
    return [dict(skill_id=s["skill_id"], name=s["name"], category=s["category"]) for s in ss if not q or q in s["name"].lower() or any(q in a for a in s["aliases"])]
