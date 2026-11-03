"""Reference backend. Run: make run  (rules mode, no keys needed). Business rules live in engine/; this file only validates, stores and wires."""
import re, json, os, uuid, pathlib, base64, binascii, time, datetime as dt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as HTTPEx
from engine import core as E, extract_rules as X, readiness as R, motivation as M
from contracts.v2 import models as C
from .db import DB
from . import orchestrator as O, agents as A, llm
from engine import market as MK, missions as MS, chapters as CH, cv as CV, paths as PT, cvfile as CF

APP_VERSION, CONTRACT_VERSION = "0.2.0", "2.0"
SK, ROLES, RES = E.load("v2"); ROLE = {r["role_id"]: r for r in ROLES}
CURR = json.loads((E.DATA / "v2" / "curriculum.json").read_text())["curriculum"]
PERSONAS = json.loads((E.DATA / "v2" / "personas.json").read_text())
PATHS = json.loads((E.DATA / "v2" / "role_courses.json").read_text())
FORBIDDEN = (E.FORBIDDEN_FEATURES - {"name"}) | {"dob", "date_of_birth", "birthdate", "sex", "caste", "religion"}
ALLOW_UNVERIFIED = os.environ.get("ALLOW_UNVERIFIED_RESOURCES", "true").lower() == "true"
ALLOW_SAMPLE = os.environ.get("ALLOW_SAMPLE_RESOURCES", "true").lower() == "true"
DISCLAIMER = "Scores are provisional and explain skill coverage. They are not a hiring probability or a guarantee of employment."
PLAN_NOTE = "Courses marked unverified or sample have not been confirmed by a person. Check the course page before enrolling."
db = DB(); O.bind(db); app = FastAPI(title="Career Orchestrator API", version=CONTRACT_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=[o for o in os.environ.get("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",") if o], allow_methods=["*"], allow_headers=["*"])
MAX_BODY = 4_000_000
_hits = {}
@app.middleware("http")
async def _guard(request: Request, call_next):
    if int(request.headers.get("content-length") or 0) > MAX_BODY:
        return JSONResponse(status_code=413, content={"error": {"code": "VALIDATION_ERROR", "message": "Request is too large.", "details": None}})
    if len(_hits) > 1000: _hits.clear()   # shortcut: forgets all counters at once, fine for a demo; use a TTL cache if exposed
    if request.method == "POST" and request.url.path.endswith(("/extract", "/scout", "/cv/parse", "/cv/file", "/decline")):   # these may call the language model
        k = (request.client.host if request.client else "?"); t = time.time(); _hits[k] = [x for x in _hits.get(k, []) if t - x < 60]
        if len(_hits[k]) >= int(os.environ.get("RATE_LIMIT_PER_MIN", "40")): return JSONResponse(status_code=429, content={"error": {"code": "INTERNAL", "message": "Too many requests. Wait a minute and try again.", "details": None}})
        _hits[k].append(t)
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"; resp.headers["X-Frame-Options"] = "DENY"; resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if request.url.path.startswith("/api/"): resp.headers["Cache-Control"] = "no-store"
    return resp
def now() -> dt.datetime: return dt.datetime.now(dt.timezone.utc)
def iso(t=None) -> str: return (t or now()).replace(microsecond=0).isoformat()
class Err(Exception):
    def __init__(self, status, code, msg, details=None): self.status, self.code, self.msg, self.details = status, code, msg, details
@app.exception_handler(Err)
async def _err(_, e: Err): return JSONResponse(status_code=e.status, content={"error": {"code": e.code, "message": e.msg, "details": e.details}})
@app.exception_handler(RequestValidationError)
async def _val(_, e: RequestValidationError):
    errs = e.errors(); bad = [x for x in errs if x["type"] == "extra_forbidden"]
    names = {str(x["loc"][-1]).lower() for x in bad}
    if names & FORBIDDEN:
        return JSONResponse(status_code=422, content={"error": {"code": "FORBIDDEN_FIELD", "message": "This system never accepts age, date of birth, gender or similar fields.", "details": {"fields": sorted(names & FORBIDDEN)}}})
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": "Request does not match the contract.", "details": {"errors": [{"loc": list(map(str, x["loc"])), "msg": x["msg"]} for x in errs]}}})
@app.exception_handler(HTTPEx)
async def _http(_, e: HTTPEx):
    return JSONResponse(status_code=e.status_code, content={"error": {"code": "NOT_FOUND" if e.status_code == 404 else "INTERNAL", "message": str(e.detail), "details": None}})
@app.exception_handler(Exception)
async def _any(_, e: Exception): return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL", "message": "Unexpected error. Nothing was lost; try again.", "details": None}})

def jl(s): return json.loads(s) if s else None
def get_profile(pid: str) -> dict:
    r = db.one("SELECT * FROM profiles WHERE profile_id=?", (pid,))
    if not r: raise Err(404, "NOT_FOUND", f"Profile {pid} not found")
    return dict(profile_id=r["profile_id"], display_name=r["display_name"], current_role=r["current_role"], work_examples=jl(r["work_examples"]), declared_skills=jl(r["declared_skills"]),
                stated_goal_role_id=r["stated_goal_role_id"], preferences=jl(r["preferences"]), motivation=jl(r["motivation"]), created_at=r["created_at"])
def confirmed_of(pid: str) -> dict:
    r = db.one("SELECT payload FROM confirmations WHERE profile_id=?", (pid,))
    if not r: raise Err(409, "SKILLS_NOT_CONFIRMED", "Confirm your skills first (POST /profiles/{id}/confirm).")
    return jl(r["payload"])
def levels_and_evidence(conf: dict):
    lv = {c["skill_id"]: c["level"] for c in conf["confirmed_skills"]}
    ev = {c["skill_id"]: [e["quote"] for e in c["evidence"]] for c in conf["confirmed_skills"]}
    return lv, ev
def fix_rec(rec: dict) -> dict:
    for m in rec["matched"]: m["evidence_quotes"] = m.pop("evidence_ids")
    return rec
def rank_for(profile: dict, lv: dict, ev: dict):
    prefs = (profile["preferences"] or {}).get("interests", [])
    return [fix_rec(r) for r in E.rank(lv, ROLES, prefs, SK, ev)]

@app.get("/api/v1/health")
def health(): return {"status": "ok", "time": iso()}
@app.get("/api/v1/meta", response_model=C.Meta)
def meta():
    return dict(app_version=APP_VERSION, contract_version=CONTRACT_VERSION, mode=os.environ.get("APP_MODE", "replay"), extraction_mode="llm+rules" if llm.live_ready() else "rules", weights=E.WEIGHTS, weights_are_provisional=True,
                catalog=dict(skills=sum(1 for s in SK.values() if s["scored"]), roles=len(ROLES), resources=len(RES)), resource_policy=dict(allow_unverified=ALLOW_UNVERIFIED, allow_sample=ALLOW_SAMPLE),
                disclaimers=[DISCLAIMER, "Demo data is synthetic and illustrative.", "Fairness checks do not prove a system is free of bias."])
@app.get("/api/v1/roles")
def roles(): return {"roles": [dict(role_id=r["role_id"], title=r["title"], summary=r["summary"], family=r["family"], tags=r["tags"], data_note=r["data_note"],
                                    requirements=[dict(skill_id=q["skill_id"], name=SK[q["skill_id"]]["name"], required_level=q["required_level"], mandatory=q["mandatory"]) for q in r["requirements"]]) for r in ROLES]}
@app.get("/api/v1/skills")
def skills(): return {"skills": [dict(skill_id=s["skill_id"], name=s["name"], category=s["category"]) for s in SK.values() if s["scored"]]}
@app.get("/api/v1/demo/personas")
def demo_personas():
    return {"synthetic": True, "personas": [dict(persona_id=p["user_id"], display_name=p["name"], current_role=p["current_role"], work_examples=[p["work_text"]], declared_skills=p["declared_skills"],
            stated_goal_role_id=p["stated_goal_role_id"]) for p in PERSONAS.values()]}

@app.post("/api/v1/profiles", response_model=C.Profile, status_code=201)
def create_profile(body: C.ProfileCreate):
    if not body.consent: raise Err(400, "CONSENT_REQUIRED", "Consent is required before any text is processed.")
    if body.stated_goal_role_id and body.stated_goal_role_id not in ROLE: raise Err(422, "VALIDATION_ERROR", "Unknown stated_goal_role_id", {"role_ids": sorted(ROLE)})
    for t in body.work_examples:
        if not 10 <= len(t) <= 1000: raise Err(422, "VALIDATION_ERROR", "Each work example must be 10 to 1000 characters.")
    pid = "prof_" + uuid.uuid4().hex[:10]; t = iso()
    db.run("INSERT INTO profiles VALUES (?,?,?,?,?,?,?,?,?,?)", (pid, body.display_name, body.current_role, json.dumps(body.work_examples), json.dumps([d.model_dump() for d in body.declared_skills]),
           body.stated_goal_role_id, body.preferences and body.preferences.model_dump_json(), body.motivation and body.motivation.model_dump_json(), t, t))
    db.log(t, "worker", "profile_created", pid); return get_profile(pid)
@app.get("/api/v1/profiles/{pid}", response_model=C.Profile)
def read_profile(pid: str): return get_profile(pid)
@app.delete("/api/v1/profiles/{pid}", status_code=204)
def delete_profile(pid: str):
    get_profile(pid); db.run("DELETE FROM profiles WHERE profile_id=?", (pid,)); db.log(iso(), "worker", "profile_deleted", pid)

@app.post("/api/v1/profiles/{pid}/extract", response_model=C.ExtractResponse)
def extract(pid: str):
    p = get_profile(pid); sug, uns = X.suggest(p["declared_skills"], p["work_examples"], SK)
    found = A.skills_discovery(p["work_examples"], SK); mode = "rules"
    if found is not None: sug = A.merge_findings(sug, found, SK); mode = "llm+rules"
    for s in sug: s["suggestion_id"] = "sg_" + s["skill_id"]
    warn = ["Suggestions come from the Skills Discovery agent (a language model) and keyword rules. Please check every one." if mode == "llm+rules" else "Suggestions come from keyword rules. Please check every one."]
    out = dict(profile_id=pid, suggestions=sug, unmatched_declared=uns, extraction_mode=mode, warnings=warn + (["No skills found. Add examples or declare skills."] if not sug else []))
    db.run("INSERT OR REPLACE INTO extractions VALUES (?,?,?)", (pid, json.dumps(out), iso())); db.log(iso(), "system", "skills_suggested", pid, {"n": len(sug), "mode": mode})
    O.record(pid, "skills_discovery", mode, f"{len(p['work_examples'])} work examples, {len(p['declared_skills'])} declared skills", f"{len(sug)} skills suggested with evidence"); return out
@app.post("/api/v1/profiles/{pid}/confirm", response_model=C.ConfirmResponse)
def confirm(pid: str, body: C.ConfirmRequest):
    get_profile(pid); r = db.one("SELECT payload FROM extractions WHERE profile_id=?", (pid,))
    if not r: raise Err(409, "SKILLS_NOT_CONFIRMED", "Run extract first.")
    sug = {s["suggestion_id"]: s for s in jl(r["payload"])["suggestions"]}; seen = set(); conf = []; rej = []
    for d in body.decisions:
        if d.suggestion_id not in sug: raise Err(422, "VALIDATION_ERROR", f"Unknown suggestion_id {d.suggestion_id}")
        if d.suggestion_id in seen: raise Err(422, "VALIDATION_ERROR", f"Duplicate decision for {d.suggestion_id}")
        seen.add(d.suggestion_id); s = sug[d.suggestion_id]
        if d.action == "reject": rej.append(s["skill_id"]); continue
        if d.action == "edit" and d.level is None: raise Err(422, "VALIDATION_ERROR", "edit needs a level")
        conf.append(dict(skill_id=s["skill_id"], name=s["name"], level=d.level if d.action == "edit" else s["suggested_level"], source=s["source"], evidence=s["evidence"]))
    if seen != set(sug): raise Err(422, "VALIDATION_ERROR", "Every suggestion needs a decision.", {"missing": sorted(set(sug) - seen)})
    for a in body.added_skills:
        if a.skill_id not in SK or not SK[a.skill_id]["scored"]: raise Err(422, "VALIDATION_ERROR", f"Unknown skill_id {a.skill_id}")
        if any(c["skill_id"] == a.skill_id for c in conf): raise Err(422, "VALIDATION_ERROR", f"{a.skill_id} is already confirmed")
        conf.append(dict(skill_id=a.skill_id, name=SK[a.skill_id]["name"], level=a.level, source="user_added", evidence=[]))
    conf.sort(key=lambda c: c["name"]); out = dict(profile_id=pid, confirmed_skills=conf, rejected_skill_ids=sorted(rej))
    db.run("INSERT OR REPLACE INTO confirmations VALUES (?,?,?)", (pid, json.dumps(out), iso())); db.run("UPDATE plans SET active=0 WHERE profile_id=?", (pid,))
    db.log(iso(), "worker", "skills_confirmed", pid, {"confirmed": len(conf), "rejected": len(rej)})
    ed = sum(1 for d in body.decisions if d.action == "edit"); ac = sum(1 for d in body.decisions if d.action == "accept")
    O.record(pid, "human_in_the_loop", "gate_1_confirm_skills", f"{len(sug)} suggestions shown", f"{ac} accepted, {ed} edited, {len(rej)} rejected, {len(body.added_skills)} added by the worker", stopped_at_gate=True); return out

@app.get("/api/v1/profiles/{pid}/recommendations", response_model=C.RecommendationsResponse)
def recommendations(pid: str):
    p = get_profile(pid); lv, ev = levels_and_evidence(confirmed_of(pid)); recs = rank_for(p, lv, ev)
    for r in recs:
        pth = PT.build_path(r["role_id"], PATHS, lv)
        r["build_skills"] = [x["name"] for x in pth["requirements"] if not x["have"]]; r["course_count"] = len(pth["courses"]); r["course_hours"] = round(sum(c["hours"] or 0 for c in pth["courses"]), 1)
    goal = next((r for r in recs if r["role_id"] == p["stated_goal_role_id"]), None)
    db.log(iso(), "system", "recommendations_shown", pid, {"top": [r["role_id"] for r in recs[:3]]})
    O.record(pid, "inclusive_matching", "rules", f"{len(lv)} confirmed skills (no age, gender or years used)", f"{len(recs)} roles ranked; top {recs[0]['role_id']}", dedupe=True); return dict(profile_id=pid, recommendations=recs, goal=goal, disclaimer=DISCLAIMER)

@app.get("/api/v1/profiles/{pid}/paths/{role_id}", response_model=C.RolePathResponse)
def role_path(pid: str, role_id: str):
    """Job options: the courses for one role, simplest first. Which courses and their order come from engine/paths.py; the agent only writes each reason."""
    p = get_profile(pid); lv, _ = levels_and_evidence(confirmed_of(pid))
    if role_id not in ROLE: raise Err(404, "NOT_FOUND", f"Role {role_id} not found")
    path = PT.build_path(role_id, PATHS, lv)
    why, mode = A.path_reasons(ROLE[role_id]["title"], path["courses"], path["requirements"])
    courses = [dict(resource_id=c["course_id"], title=c["title"], provider=c["provider"], url=c["url"], level=c["level"] if c["level"] in PT.LEVEL_RANK else None, level_basis=c["level_basis"], est_hours=c["hours"],
                    duration_text=c["duration_text"], cost=c["cost"], rating=c["rating"], rating_count=c["rating_count"], certificate=c["certificate"], prerequisites=c["prerequisites"],
                    covers=c["covers"], why=why[c["course_id"]][0], decided_by=why[c["course_id"]][1], verification_status=c["verification_status"], units=c.get("units") or [], topics=c.get("topics") or []) for c in path["courses"]]
    O.record(pid, "learning_pathway", mode if courses else "rules", f"requirements for {role_id} checked against {len(PATHS['courses'])} catalogue courses", f"{len(courses)} courses shown, simplest first", dedupe=True)
    return dict(profile_id=pid, role_id=role_id, role_title=ROLE[role_id]["title"], requirements=path["requirements"], courses=courses, mode=mode,
                source_note=PATHS["note"] if courses else "No courses have been checked for this role yet.")
def plan_payload(pid, p, role_id, weekly):
    lv, ev = levels_and_evidence(confirmed_of(pid)); rec = next(r for r in rank_for(p, lv, ev) if r["role_id"] == role_id)
    plan = E.build_plan(rec, lv, SK, RES, weekly, allow_unverified=ALLOW_UNVERIFIED, allow_sample=ALLOW_SAMPLE)
    for s in plan["steps"]:
        if s["resource"]: s["resource"] = {k: s["resource"][k] for k in C.Resource.model_fields}
    return plan, rec
@app.post("/api/v1/profiles/{pid}/plan", response_model=C.PlanResponse)
def make_plan(pid: str, body: C.PlanRequest):
    p = get_profile(pid)
    if body.role_id not in ROLE: raise Err(422, "VALIDATION_ERROR", "Unknown role_id", {"role_ids": sorted(ROLE)})
    weekly = body.weekly_hours or (p["preferences"] or {}).get("weekly_hours"); plan, _ = plan_payload(pid, p, body.role_id, weekly)
    pl_id = "plan_" + uuid.uuid4().hex[:10]; db.run("UPDATE plans SET active=0 WHERE profile_id=?", (pid,))
    out = dict(plan_id=pl_id, profile_id=pid, role_id=body.role_id, role_title=ROLE[body.role_id]["title"], total_est_hours=plan["total_est_hours"], weekly_hours=weekly, weeks_at_pace=plan["weeks_at_pace"], steps=plan["steps"],
               unresolved_skill_ids=plan["unresolved_skill_ids"], includes_unverified_resources=any(s["resource"] and s["resource"]["verification_status"] != "verified" for s in plan["steps"]), disclaimer=PLAN_NOTE)
    db.run("INSERT INTO plans VALUES (?,?,?,?,1,?)", (pl_id, pid, body.role_id, json.dumps(out), iso())); db.log(iso(), "worker", "plan_accepted", pid, {"role_id": body.role_id, "plan_id": pl_id})
    O.record(pid, "human_in_the_loop", "gate_2_choose_role", "roles ranked and shown", f"worker chose {body.role_id}", stopped_at_gate=True)
    O.record(pid, "learning_pathway", "rules", f"{len(plan['steps'])} skill gaps for {body.role_id}", f"{len(plan['steps'])} step{'s' if len(plan['steps']) != 1 else ''}, {plan['total_est_hours']:g} hours, {len(plan['unresolved_skill_ids'])} without a course"); return out
def active_plan(pid):
    get_profile(pid); r = db.one("SELECT payload FROM plans WHERE profile_id=? AND active=1 ORDER BY created_at DESC LIMIT 1", (pid,))
    if not r: raise Err(409, "NO_ACTIVE_PLAN", "Create a plan first (POST /profiles/{id}/plan).")
    return jl(r["payload"])
@app.get("/api/v1/profiles/{pid}/plan", response_model=C.PlanResponse)
def read_plan(pid: str): return active_plan(pid)

@app.put("/api/v1/profiles/{pid}/motivation", response_model=C.MotivationPrefs)
def set_motivation(pid: str, body: C.MotivationPrefs):
    get_profile(pid); db.run("UPDATE profiles SET motivation=? WHERE profile_id=?", (body.model_dump_json(), pid)); db.log(iso(), "worker", "motivation_set", pid, body.model_dump()); return body
def progress_map(plan_id): return {r["step_order"]: r["percent"] for r in db.all("SELECT step_order, percent FROM progress WHERE plan_id=?", (plan_id,))}
def active_styles(pid, prefs):
    styles = list(prefs["styles"])
    if len(styles) > 1:
        for st in styles[:]:
            last = db.all("SELECT helpful FROM messages WHERE profile_id=? AND style=? ORDER BY created_at DESC, rowid DESC LIMIT 3", (pid, st))
            if len(last) == 3 and all(x["helpful"] == 0 for x in last): styles.remove(st)
    return styles or list(prefs["styles"])
def course_steps(pid):
    """When the chosen role has course data, progress is counted per course: the share of that course's missions that have proof. Returns (steps, percent map) or None."""
    try:
        plan = active_plan(pid)
        if db.one("SELECT 1 x FROM progress WHERE plan_id=?", (plan["plan_id"],)): return None   # percentages typed in by hand: keep the older step-by-step counting
        steps, _ = mission_steps(pid, plan)
        if not (steps and steps[0].get("course")): return None
        lv, _ = levels_and_evidence(confirmed_of(pid)); courses = PT.build_path(plan["role_id"], PATHS, lv)["courses"]
        ms = missions_view(pid)["missions"]; tally = {}
        for m in ms:
            mt = re.match(r"Course (\d+):", m.get("source") or "")
            if mt: t = tally.setdefault(int(mt.group(1)), [0, 0]); t[1] += 1; t[0] += 1 if m["status"] == "done" else 0
        out = [dict(order=i, skill_name=c["title"], est_hours=float(c["hours"] or 1)) for i, c in enumerate(courses, 1)]
        return out, {o: (round(100 * tally[o][0] / tally[o][1]) if o in tally and tally[o][1] else 0) for o in range(1, len(out) + 1)}
    except Exception: return None
def plan_nums(pid, steps, pm, weekly, matched=0):
    """The numbers the encouragement templates use. When the role has course data, steps and progress are the courses (not the older skill steps)."""
    cs = course_steps(pid)
    if cs: steps, pm = cs
    n = M.plan_numbers(steps, pm, weekly, matched)
    if cs: n["next_step"] = next((s["skill_name"] for s in steps if pm.get(s["order"], 0) < 100), ""); n["last_step"] = next((s["skill_name"] for s in reversed(steps) if pm.get(s["order"], 0) >= 100), "")
    return n
def progress_view(pid, plan, msg=None):
    pm = progress_map(plan["plan_id"]); n = plan_nums(pid, plan["steps"], pm, plan.get("weekly_hours")); last = db.one("SELECT MAX(updated_at) m FROM progress WHERE plan_id=?", (plan["plan_id"],))["m"]
    if msg is None:
        row = db.one("SELECT * FROM messages WHERE profile_id=? AND plan_id=? ORDER BY created_at DESC, rowid DESC LIMIT 1", (pid, plan["plan_id"]))
        msg = row and dict(message_id=row["message_id"], style=row["style"], event=row["event"], text=row["text"], suggested_action=row["suggested_action"])
        pr = get_profile(pid)["motivation"]
        if last and pr and not pr["paused"] and pr["check_in"] != "off" and (now() - dt.datetime.fromisoformat(last)).days >= 7 and not (msg and msg["event"] == "behind"):
            msg = new_message(pid, plan, pr, "behind", dict(n, matched_count=0))
    cs = course_steps(pid); st, pmap = cs if cs else (plan["steps"], pm); tot_h = round(sum(s["est_hours"] for s in st), 1) if cs else plan["total_est_hours"]
    return dict(profile_id=pid, plan_id=plan["plan_id"], percent=n["percent"], hours_done=round(tot_h - n["hours_left"], 1), hours_total=tot_h, steps_done=n["done"], steps_total=n["total"],
                steps=[dict(order=s["order"], skill_name=s["skill_name"], est_hours=s["est_hours"], percent=pmap.get(s["order"], 0)) for s in st], last_activity_at=last, next_message=msg)
def get_background(pid) -> dict:
    r = db.one("SELECT payload FROM background WHERE profile_id=?", (pid,)); return jl(r["payload"]) if r else C.Background().model_dump()
def new_message(pid, plan, prefs, event, nums):
    shown = db.one("SELECT COUNT(*) c FROM messages WHERE profile_id=?", (pid,))["c"]; st, text, act = M.select(active_styles(pid, prefs), event, nums, shown)
    bg = get_background(pid); ctx = {k: v for k, v in (("situation", bg.get("situation")), ("situations", bg.get("situations")), ("barriers", bg.get("barriers"))) if v}
    text = A.polish(text, st, ctx)       # the model may only re-word the template; any failed check keeps the template
    mid = "msg_" + uuid.uuid4().hex[:10]; db.run("INSERT INTO messages VALUES (?,?,?,?,?,?,?,NULL,?)", (mid, pid, plan["plan_id"], st, event, text, act, iso()))
    return dict(message_id=mid, style=st, event=event, text=text, suggested_action=act)
@app.get("/api/v1/profiles/{pid}/progress", response_model=C.ProgressResponse)
def read_progress(pid: str): return progress_view(pid, active_plan(pid))
@app.post("/api/v1/profiles/{pid}/progress", response_model=C.ProgressResponse)
def update_progress(pid: str, body: C.ProgressUpdate):
    p = get_profile(pid); plan = active_plan(pid); matched = sum(1 for c in confirmed_of(pid)["confirmed_skills"] if c["evidence"])
    if body.step_order not in {s["order"] for s in plan["steps"]}: raise Err(422, "VALIDATION_ERROR", "Unknown step_order for the active plan")
    before_map = progress_map(plan["plan_id"]); before = plan_nums(pid, plan["steps"], before_map, plan.get("weekly_hours")); prev = db.one("SELECT MAX(updated_at) m FROM progress WHERE plan_id=?", (plan["plan_id"],))["m"]
    days = None if not prev else (now() - dt.datetime.fromisoformat(prev)).days
    db.run("INSERT OR REPLACE INTO progress VALUES (?,?,?,?,?)", (plan["plan_id"], body.step_order, body.percent, body.hours_logged, iso()))
    after = plan_nums(pid, plan["steps"], progress_map(plan["plan_id"]), plan.get("weekly_hours"), matched); db.log(iso(), "worker", "progress_updated", pid, {"step": body.step_order, "percent": body.percent})
    ev = M.detect_event(before["percent"], after["percent"], before["done"], after["done"], after["total"], days, prev is None); msg = None
    pr = p["motivation"]
    if ev and pr and not pr["paused"] and pr["check_in"] != "off":
        msg = new_message(pid, plan, pr, ev, after)
    v = progress_view(pid, plan, msg=msg if msg else False)
    if not msg: v["next_message"] = None
    return v
@app.post("/api/v1/profiles/{pid}/messages/{mid}/feedback", status_code=204)
def feedback(pid: str, mid: str, body: C.MessageFeedback):
    get_profile(pid)
    if not db.one("SELECT 1 FROM messages WHERE message_id=? AND profile_id=?", (mid, pid)): raise Err(404, "NOT_FOUND", "Message not found")
    db.run("UPDATE messages SET helpful=? WHERE message_id=?", (1 if body.helpful else 0, mid))

# ---------- v3: trace, market intelligence, course scout, missions ----------
@app.get("/api/v1/profiles/{pid}/trace", response_model=C.TraceResponse)
def read_trace(pid: str): get_profile(pid); return dict(profile_id=pid, steps=O.trace(pid))
@app.get("/api/v1/profiles/{pid}/market", response_model=C.MarketResponse)
def market(pid: str):
    p = get_profile(pid); lv, ev = levels_and_evidence(confirmed_of(pid)); top = [r["role_id"] for r in rank_for(p, lv, ev)[:3]]
    out = dict(profile_id=pid, **MK.market_view(lv, ROLES, SK, top))
    O.record(pid, "market_intelligence", "catalogue", f"{len(lv)} confirmed skills, {len(ROLES)} catalogue roles", f"{len(out['held'])} held skills counted, {len(out['next_skills'])} next skills", dedupe=True); return out
RES_FIELDS = list(C.Resource.model_fields)
def as_resource(r): return {k: r[k] for k in RES_FIELDS}
@app.post("/api/v1/profiles/{pid}/scout", response_model=C.ScoutResponse)
def scout(pid: str):
    plan = active_plan(pid); done_titles = {c["name"].strip().lower() for c in get_background(pid)["certifications"]}
    steps, mode = A.scout(plan, RES, RES_FIELDS, ALLOW_UNVERIFIED, ALLOW_SAMPLE, done_titles)
    O.record(pid, "learning_pathway", "course_scout_" + mode, f"{len(steps)} plan steps, {len(RES)} catalogue courses", f"{sum(1 for x in steps if x['pick_resource_id'])} picks proposed for the worker to approve")
    return dict(profile_id=pid, plan_id=plan["plan_id"], mode=mode, steps=steps, note="Picks come only from the course catalogue. Nothing changes until you approve. Check the course page before you enrol.")
@app.post("/api/v1/profiles/{pid}/scout/approve", response_model=C.PlanResponse)
def scout_approve(pid: str, body: C.ScoutApproveRequest):
    plan = active_plan(pid); by_order = {s["order"]: s for s in plan["steps"]}; res = {r["resource_id"]: r for r in RES}
    for ch in body.choices:
        st, r = by_order.get(ch.order), res.get(ch.resource_id)
        if st is None: raise Err(422, "VALIDATION_ERROR", f"Unknown step {ch.order}")
        if r is None or st["skill_id"] not in r["skill_ids"]: raise Err(422, "VALIDATION_ERROR", f"Course {ch.resource_id} does not cover {st['skill_name']}")
        if not A._eligible(r, ALLOW_UNVERIFIED, ALLOW_SAMPLE): raise Err(422, "VALIDATION_ERROR", f"Course {ch.resource_id} is not allowed by the course policy")
        st["resource"] = as_resource(r); st["status"] = "resource_found"
    plan["unresolved_skill_ids"] = [s["skill_id"] for s in plan["steps"] if s["status"] != "resource_found"]
    plan["includes_unverified_resources"] = any(s["resource"] and s["resource"]["verification_status"] != "verified" for s in plan["steps"])
    db.run("UPDATE plans SET payload=? WHERE plan_id=?", (json.dumps(plan), plan["plan_id"])); db.log(iso(), "worker", "scout_approved", pid, {"n": len(body.choices)})
    O.record(pid, "human_in_the_loop", "gate_3_approve_courses", "course picks shown", f"worker approved {len(body.choices)} course choices", stopped_at_gate=True); return plan
def chapters_of(step) -> list:
    rid = (step.get("resource") or {}).get("resource_id"); return (CURR.get(rid) or {}).get("chapters", []) if rid else []
def mission_steps(pid, plan):
    """Missions follow the courses of the chosen role (the same simplest-first list the person saw). Roles with no course data fall back to the plan's steps."""
    try:
        lv, _ = levels_and_evidence(confirmed_of(pid)); courses = PT.build_path(plan["role_id"], PATHS, lv)["courses"]
    except Exception: courses = []
    if courses: return [dict(order=i, skill_name=c["title"], course=True, units=c.get("units") or []) for i, c in enumerate(courses, 1)], {}
    return plan["steps"], {x["order"]: chapters_of(x) for x in plan["steps"] if chapters_of(x)}
def missions_view(pid):
    plan = active_plan(pid); done = {r["mission_id"]: r["file_name"] for r in db.all("SELECT mission_id, file_name FROM proofs WHERE profile_id=?", (pid,))}
    st = {r["mission_id"]: r["state"] for r in db.all("SELECT mission_id, state FROM mission_state WHERE profile_id=?", (pid,))}
    steps, chapters = mission_steps(pid, plan)
    ms = MS.build(steps, set(done), {m for m, v in st.items() if v == "started"}, {m for m, v in st.items() if v == "declined"}, chapters)
    for m in ms: m["proof_name"] = done.get(m["mission_id"])
    today = next((m["mission_id"] for m in ms if m["status"] == "open"), None)
    return dict(profile_id=pid, missions=ms, today_mission_id=today)
@app.get("/api/v1/profiles/{pid}/missions", response_model=C.MissionsResponse)
def read_missions(pid: str): return missions_view(pid)
def mission_or_404(pid, mid):
    m = next((x for x in missions_view(pid)["missions"] if x["mission_id"] == mid), None)
    if m is None: raise Err(404, "NOT_FOUND", "Mission not found")
    return m
@app.post("/api/v1/profiles/{pid}/missions/{mid}/start", response_model=C.MissionsResponse)
def start_mission(pid: str, mid: str):
    m = mission_or_404(pid, mid)
    if m["status"] in ("open", "declined"): db.run("INSERT OR REPLACE INTO mission_state VALUES (?,?,?,?)", (pid, mid, "started", iso())); db.log(iso(), "worker", "mission_started", pid, {"mission": mid})
    return missions_view(pid)
@app.post("/api/v1/profiles/{pid}/missions/{mid}/reopen", response_model=C.MissionsResponse)
def reopen_mission(pid: str, mid: str):
    mission_or_404(pid, mid); db.run("DELETE FROM mission_state WHERE profile_id=? AND mission_id=? AND state='declined'", (pid, mid)); return missions_view(pid)
@app.post("/api/v1/profiles/{pid}/missions/{mid}/decline", response_model=C.MissionDeclineResponse)
def decline_mission(pid: str, mid: str):
    m = mission_or_404(pid, mid)
    if m["status"] == "done": raise Err(422, "VALIDATION_ERROR", "This mission is already done.")
    db.run("INSERT OR REPLACE INTO mission_state VALUES (?,?,?,?)", (pid, mid, "declined", iso())); db.log(iso(), "worker", "mission_declined", pid, {"mission": mid})
    p = get_profile(pid); plan = active_plan(pid); pr = p["motivation"]; msg = None
    if pr and not pr["paused"]:
        matched = sum(1 for c in confirmed_of(pid)["confirmed_skills"] if c["evidence"]); msg = new_message(pid, plan, pr, "behind", plan_nums(pid, plan["steps"], progress_map(plan["plan_id"]), plan.get("weekly_hours"), matched))
    O.record(pid, "human_in_the_loop", "mission_declined", "worker chose not to do a mission now", "mission set aside, encouragement " + ("shown" if msg else "paused"))
    return dict(missions=missions_view(pid), message=msg)
PROOF_EXT = (".pdf", ".png", ".jpg", ".jpeg", ".txt", ".doc", ".docx")
@app.post("/api/v1/profiles/{pid}/missions/{mid}/proof", response_model=C.MissionsResponse)
def upload_proof(pid: str, mid: str, body: C.ProofRequest):
    mission_or_404(pid, mid)
    name = pathlib.PurePath(body.file_name).name
    if not name.lower().endswith(PROOF_EXT): raise Err(422, "VALIDATION_ERROR", "Proof must be a PDF, image, text or Word file.")
    try: raw = base64.b64decode(body.content_base64, validate=True)
    except (binascii.Error, ValueError): raise Err(422, "VALIDATION_ERROR", "File content is not valid.")
    if not raw or len(raw) > 2_000_000: raise Err(422, "VALIDATION_ERROR", "Proof must be between 1 byte and 2 MB.")
    db.run("INSERT OR REPLACE INTO proofs VALUES (?,?,?,?,?,?,?)", (pid, mid, name, len(raw), body.note, raw, iso())); db.log(iso(), "worker", "proof_uploaded", pid, {"mission": mid, "bytes": len(raw)}); return missions_view(pid)

# ---------- chapters: progress from ticked chapters ----------
def chapters_view(pid, order, msg=None):
    plan = active_plan(pid); st = next((x for x in plan["steps"] if x["order"] == order), None)
    if st is None: raise Err(422, "VALIDATION_ERROR", "Unknown step_order for the active plan")
    chs = chapters_of(st); rid = (st.get("resource") or {}).get("resource_id")
    done = {r["chapter_id"] for r in db.all("SELECT chapter_id FROM chapter_done WHERE profile_id=? AND resource_id=?", (pid, rid))} if rid else set()
    pct = CH.percent(chs, done) if chs else progress_map(plan["plan_id"]).get(order, 0)
    return dict(profile_id=pid, step_order=order, resource_id=rid, chapters=[dict(chapter_id=c["chapter_id"], title=c["title"], est_hours=c.get("est_hours"), done=c["chapter_id"] in done) for c in chs],
                percent=pct, source="chapters" if chs else "manual", next_message=msg)
@app.get("/api/v1/profiles/{pid}/steps/{order}/chapters", response_model=C.ChaptersResponse)
def read_chapters(pid: str, order: int): return chapters_view(pid, order)
@app.post("/api/v1/profiles/{pid}/steps/{order}/chapters", response_model=C.ChaptersResponse)
def tick_chapter(pid: str, order: int, body: C.ChapterTick):
    plan = active_plan(pid); st = next((x for x in plan["steps"] if x["order"] == order), None)
    if st is None: raise Err(422, "VALIDATION_ERROR", "Unknown step_order for the active plan")
    chs = chapters_of(st); rid = (st.get("resource") or {}).get("resource_id")
    if not chs or body.chapter_id not in {c["chapter_id"] for c in chs}: raise Err(422, "VALIDATION_ERROR", "This course has no such chapter.")
    if body.done: db.run("INSERT OR REPLACE INTO chapter_done VALUES (?,?,?,?)", (pid, rid, body.chapter_id, iso()))
    else: db.run("DELETE FROM chapter_done WHERE profile_id=? AND resource_id=? AND chapter_id=?", (pid, rid, body.chapter_id))
    pct = chapters_view(pid, order)["percent"]; prog = update_progress(pid, C.ProgressUpdate(step_order=order, percent=pct))
    return chapters_view(pid, order, prog.get("next_message"))

# ---------- background (education, certificates, barriers...) and the CV ----------
@app.put("/api/v1/profiles/{pid}/background", response_model=C.Background)
def put_background(pid: str, body: C.Background):
    get_profile(pid); db.run("INSERT OR REPLACE INTO background VALUES (?,?,?)", (pid, body.model_dump_json(), iso())); db.log(iso(), "worker", "background_saved", pid, {"education": len(body.education), "certifications": len(body.certifications)}); return body
@app.get("/api/v1/profiles/{pid}/background", response_model=C.Background)
def read_background(pid: str): get_profile(pid); return get_background(pid)
@app.post("/api/v1/cv/file", response_model=C.CVFileText)
def cv_file(body: C.CVFileRequest):
    """PDF or Word (.docx) CV to plain text. The text is shown to the person, who then reads it with POST /cv/parse. Nothing is stored."""
    try: raw = base64.b64decode(body.content_base64, validate=True)
    except (binascii.Error, ValueError): raise Err(422, "VALIDATION_ERROR", "The file could not be read. Try uploading it again.")
    try: return CF.extract_text(raw)
    except CF.CVFileError as e: raise Err(422, "VALIDATION_ERROR", str(e))
@app.post("/api/v1/cv/parse", response_model=C.CVParseResponse)
def cv_parse(body: C.CVParseRequest):
    out, mode, ignored = A.cv_parse(body.text, SK)
    return dict(out, mode=mode, ignored_lines=ignored, warnings=["Check every box before you continue. Nothing is used until you confirm.", "Lines about age, gender and years worked are ignored and never used."]
                + ([] if (out["work_examples"] or out["skills"]) else ["We could not find work tasks or skills. Check that the CV has headings such as Experience and Skills."]))
@app.get("/api/v1/profiles/{pid}/cv", response_model=C.CVDocument)
def generate_cv(pid: str):
    p = get_profile(pid); conf = confirmed_of(pid); bg = get_background(pid); goal = None; completed = []; tasks = []
    try:
        plan = active_plan(pid); goal = plan["role_title"]; pm = progress_map(plan["plan_id"])
        completed = [f"{s['resource']['title']} ({s['resource']['provider']})" for s in plan["steps"] if s["status"] == "resource_found" and pm.get(s["order"], 0) >= 100]
        tasks = [m["chapter_title"] or m["title"] for m in missions_view(pid)["missions"] if m["status"] == "done"]
    except Err:
        if p["stated_goal_role_id"] in ROLE: goal = ROLE[p["stated_goal_role_id"]]["title"]
    skills = [c["name"] for c in sorted(conf["confirmed_skills"], key=lambda c: (-c["level"], c["name"]))]
    ex = [x for x in (CV.scrub(e) for e in p["work_examples"]) if len(x) >= 10]
    text, secs = CV.render(p["display_name"], p["current_role"], goal, skills, ex, bg["education"], bg["certifications"], bg["languages"], bg["tools"], completed, tasks)
    safe = "".join(ch if ch.isalnum() else "_" for ch in p["display_name"]).strip("_") or "My"
    db.log(iso(), "worker", "cv_generated", pid, {"sections": len(secs)}); return dict(profile_id=pid, file_name=f"{safe}_updated_CV.txt", text=text, sections=secs)

@app.post("/api/v1/readiness/check", response_model=C.ReadinessResult)
def readiness(body: C.ReadinessRequest): return R.check(body.text)

CUES = [("A29", "age_statement", "I am 29 years old."), ("A42", "age_statement", "I am 42 years old."), ("A50", "age_statement", "I am 50 years old."), ("A58", "age_statement", "I am 58 years old."),
        ("P5", "experience_proxy", "I have 5 years of experience."), ("P25", "experience_proxy", "I have 25 years of experience.")]
def audit_run(p: dict, canary: bool):
    def pipeline(texts, bias=False):
        sug, _ = X.suggest(p["declared_skills"], texts, SK); lv = {s["skill_id"]: s["suggested_level"] for s in sug}
        if bias: lv = {k: (max(1, v - 1) if v >= 2 else v) for k, v in lv.items()}
        prefs = (p["preferences"] or {}).get("interests", []); recs = E.rank(lv, ROLES, prefs, SK)
        gid = p["stated_goal_role_id"] or recs[0]["role_id"]; hrs = next(r for r in recs if r["role_id"] == gid)["est_gap_hours"]; return dict(skills=lv, recs=recs, plan_hours=hrs)
    base = pipeline(p["work_examples"]); variants = []
    cases = [(vid, cue, text, False) for vid, cue, text in CUES] + ([("CANARY", "deliberately_biased_scorer", CUES[3][2], True)] if canary else [])
    for vid, cue, text, bias in cases:
        texts = p["work_examples"] + [text]; v = pipeline(texts, bias); v["text"] = " ".join(texts if not bias else texts + ["Seasoned administrator, may struggle to adapt to new technology."])
        b = dict(base, text=" ".join(p["work_examples"])); m = E.compare(b, v)
        variants.append(dict(variant_id=vid, cue=cue, metrics=m, flags=E.flags_for(vid, m)))
    return variants
@app.post("/api/v1/profiles/{pid}/audit", response_model=C.AuditResult)
def start_audit(pid: str, body: C.AuditRequest = C.AuditRequest()):
    p = get_profile(pid); variants = audit_run(p, body.canary); aid = "aud_" + uuid.uuid4().hex[:8]
    out = dict(audit_id=aid, profile_id=pid, status="flagged" if any(v["flags"] for v in variants) else "pass", canary=body.canary, variants=variants, thresholds=E.THRESH,
               limitations=["Tests only the variants listed; it cannot prove the system is free of bias.", "Variants add a statement about age or years of experience to the worker's own text.",
                            "In rules mode the extractor ignores such statements by construction, so the audit is a regression guard until a language model is used."], review=None, created_at=iso())
    db.run("INSERT INTO audits VALUES (?,?,?,?)", (aid, pid, json.dumps(out), iso())); db.log(iso(), "system", "audit_run", pid, {"status": out["status"], "canary": body.canary})
    O.record(pid, "bias_audit", "canary" if body.canary else "variants", f"{len(variants)} variants tested", f"status {out['status']}, {sum(len(v['flags']) for v in variants)} flags for a human reviewer"); return out
@app.get("/api/v1/audits/{aid}", response_model=C.AuditResult)
def read_audit(aid: str):
    r = db.one("SELECT payload FROM audits WHERE audit_id=?", (aid,))
    if not r: raise Err(404, "NOT_FOUND", "Audit not found")
    return jl(r["payload"])
@app.post("/api/v1/audits/{aid}/review", response_model=C.AuditResult)
def review_audit(aid: str, body: C.ReviewRequest):
    a = read_audit(aid); a["review"] = dict(reviewer=body.reviewer, decision=body.decision, note=body.note, reviewed_at=iso())
    db.run("UPDATE audits SET payload=? WHERE audit_id=?", (json.dumps(a), aid)); db.log(iso(), body.reviewer, "audit_reviewed", a["profile_id"], {"decision": body.decision}); return a

# Serves the frontend from the same process (one URL, no CORS): frontend_dist/ if it exists (final build), otherwise frontend/ if it has index.html.
_root = pathlib.Path(__file__).resolve().parents[2]
_site = next((d for d in (_root / "frontend_dist", _root / "frontend") if (d / "index.html").is_file()), None)
if _site: app.mount("/", StaticFiles(directory=str(_site), html=True), name="frontend")
