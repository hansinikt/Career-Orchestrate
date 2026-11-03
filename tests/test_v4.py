import os, sys, json, pathlib, uuid, base64
os.environ["DB_PATH"] = f"/tmp/co_test4_{uuid.uuid4().hex}.db"; os.environ["APP_MODE"] = "replay"; os.environ["RATE_LIMIT_PER_MIN"] = "100000"
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
import pytest
from fastapi.testclient import TestClient
from backend.app import main as M, llm
from engine import core as E, cv as CV, chapters as CH, missions as MS
c = TestClient(M.app); SK, ROLES, RES = E.load("v2"); PER = json.loads((ROOT / "data/v2/personas.json").read_text())

def make(uid="U001", motivation=True):
    p = PER[uid]; body = dict(display_name=p["name"], current_role=p["current_role"], work_examples=[p["work_text"]], declared_skills=p["declared_skills"], stated_goal_role_id=p["stated_goal_role_id"],
                              preferences=dict(interests=[], weekly_hours=6), consent=True)
    if motivation: body["motivation"] = dict(styles=["encouragement", "challenge"], check_in="weekly")
    r = c.post("/api/v1/profiles", json=body); assert r.status_code == 201, r.text; return r.json()["profile_id"], p
def journey_with_course(monkeypatch, chapters=3, with_hours=False):
    """A plan whose first step has a catalogue course, with a chapter list for that course."""
    for rid in [r["role_id"] for r in ROLES]:
        pid, p = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
        c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]]))
        plan = c.post(f"/api/v1/profiles/{pid}/plan", json=dict(role_id=rid)).json(); st = next((s for s in plan["steps"] if s["resource"]), None)
        if st: break
    assert st, "no role gives a step with a course"
    monkeypatch.setitem(M.CURR, st["resource"]["resource_id"], dict(chapters=[dict(chapter_id=f"c{i}", title=f"Chapter {i} title", est_hours=(i if with_hours else None)) for i in range(1, chapters + 1)]))
    return pid, plan, st

# ---- chapters drive progress ----
def test_chapter_percent_math():
    chs = [dict(chapter_id="a", est_hours=None), dict(chapter_id="b", est_hours=None), dict(chapter_id="c", est_hours=None), dict(chapter_id="d", est_hours=None)]
    assert CH.percent(chs, {"a"}) == 25 and CH.percent(chs, {"a", "b", "c", "d"}) == 100 and CH.percent([], set()) == 0
    hs = [dict(chapter_id="a", est_hours=1.0), dict(chapter_id="b", est_hours=3.0)]; assert CH.percent(hs, {"b"}) == 75
def test_ticking_chapters_moves_step_progress(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch, 4); o = st["order"]
    r = c.get(f"/api/v1/profiles/{pid}/steps/{o}/chapters").json(); assert r["source"] == "chapters" and len(r["chapters"]) == 4 and r["percent"] == 0
    r = c.post(f"/api/v1/profiles/{pid}/steps/{o}/chapters", json=dict(chapter_id="c1", done=True)).json(); assert r["percent"] == 25 and r["chapters"][0]["done"]
    assert next(s for s in c.get(f"/api/v1/profiles/{pid}/progress").json()["steps"] if s["order"] == o)["percent"] == 25
    r = c.post(f"/api/v1/profiles/{pid}/steps/{o}/chapters", json=dict(chapter_id="c1", done=False)).json(); assert r["percent"] == 0
    assert c.post(f"/api/v1/profiles/{pid}/steps/{o}/chapters", json=dict(chapter_id="zzz", done=True)).status_code == 422
def test_step_without_chapters_stays_manual():
    pid, p = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]])); c.post(f"/api/v1/profiles/{pid}/plan", json=dict(role_id="R001"))
    r = c.get(f"/api/v1/profiles/{pid}/steps/1/chapters").json(); assert r["source"] == "manual" and r["chapters"] == []
    assert c.post(f"/api/v1/profiles/{pid}/steps/1/chapters", json=dict(chapter_id="c1", done=True)).status_code == 422
def test_chapter_ticks_deleted_with_profile(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch); c.post(f"/api/v1/profiles/{pid}/steps/{st['order']}/chapters", json=dict(chapter_id="c1", done=True))
    assert M.db.one("SELECT COUNT(*) n FROM chapter_done WHERE profile_id=?", (pid,))["n"] == 1; c.delete(f"/api/v1/profiles/{pid}"); assert M.db.one("SELECT COUNT(*) n FROM chapter_done WHERE profile_id=?", (pid,))["n"] == 0

# ---- missions: tied to chapters, own progress, start, decline ----
def test_missions_follow_chapters(monkeypatch):
    monkeypatch.setitem(M.PATHS, "courses", [])   # a role with no role-course data keeps the chapter-based missions
    pid, plan, st = journey_with_course(monkeypatch, 3); ms = c.get(f"/api/v1/profiles/{pid}/missions").json()["missions"]
    assert [m["chapter_title"] for m in ms if m["chapter_title"]] == ["Chapter 1 title", "Chapter 2 title", "Chapter 3 title"] and all("Chapter" in m["title"] for m in ms if m["chapter_title"])
    assert [m["status"] for m in ms[:3]] == ["open", "open", "locked"] and all(m["percent"] == 0 for m in ms)
def test_mission_progress_stages(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch); mid = c.get(f"/api/v1/profiles/{pid}/missions").json()["today_mission_id"]
    got = lambda: next(m for m in c.get(f"/api/v1/profiles/{pid}/missions").json()["missions"] if m["mission_id"] == mid)
    assert got()["percent"] == 0; c.post(f"/api/v1/profiles/{pid}/missions/{mid}/start"); assert got()["percent"] == 50 and got()["status"] == "open"
    c.post(f"/api/v1/profiles/{pid}/missions/{mid}/proof", json=dict(file_name="a.txt", content_base64=base64.b64encode(b"hello world").decode())); assert got()["percent"] == 100 and got()["status"] == "done"
def test_decline_returns_encouragement_and_unlocks_next(monkeypatch):
    monkeypatch.setitem(M.PATHS, "courses", [])   # legacy plan-step missions (two open at a time)
    pid, plan, st = journey_with_course(monkeypatch); ms = c.get(f"/api/v1/profiles/{pid}/missions").json()["missions"]; mid = ms[0]["mission_id"]
    r = c.post(f"/api/v1/profiles/{pid}/missions/{mid}/decline"); assert r.status_code == 200; j = r.json()
    assert j["message"]["event"] == "behind" and j["message"]["text"] and next(m for m in j["missions"]["missions"] if m["mission_id"] == mid)["status"] == "declined"
    assert sum(1 for m in j["missions"]["missions"] if m["status"] == "open") == 2        # the declined one no longer holds a slot
    back = c.post(f"/api/v1/profiles/{pid}/missions/{mid}/reopen").json(); assert next(m for m in back["missions"] if m["mission_id"] == mid)["status"] in ("open", "locked")
    assert any(t["mode"] == "mission_declined" for t in c.get(f"/api/v1/profiles/{pid}/trace").json()["steps"])
def test_decline_respects_pause_and_missing_prefs(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch); c.put(f"/api/v1/profiles/{pid}/motivation", json=dict(styles=["progress"], check_in="weekly", paused=True))
    mid = c.get(f"/api/v1/profiles/{pid}/missions").json()["today_mission_id"]; assert c.post(f"/api/v1/profiles/{pid}/missions/{mid}/decline").json()["message"] is None
def test_decline_done_mission_rejected(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch); mid = c.get(f"/api/v1/profiles/{pid}/missions").json()["today_mission_id"]
    c.post(f"/api/v1/profiles/{pid}/missions/{mid}/proof", json=dict(file_name="a.txt", content_base64="QQ==")); assert c.post(f"/api/v1/profiles/{pid}/missions/{mid}/decline").status_code == 422
    assert c.post(f"/api/v1/profiles/{pid}/missions/m99/decline").status_code == 404

# ---- CV reader ----
CVTXT = """Anitha Raman
anitha@example.com | +91 98765 43210
Date of birth: 12 May 1984
Gender: Female
PROFESSIONAL EXPERIENCE
Records Clerk, Sunrise School Office, 2010 - 2022
- Maintained student records and kept confidential files secure for 12 years
- Scheduled parent meetings and sent emails to families
SKILLS
Record keeping, Scheduling, Microsoft Word, Tally
EDUCATION
B.Com in Commerce, Madras University, 2005
CERTIFICATIONS
Basic Computer Course - NIIT
LANGUAGES
Tamil (native), English (fluent)
"""
def test_cv_clean_removes_personal_and_age_signals():
    t, ign = CV.clean(CVTXT); low = t.lower()
    for bad in ("anitha", "@", "98765", "birth", "female", "12 years", "2010", "2022", "2005", "1984"): assert bad not in low, bad
    assert ign >= 3 and "Records Clerk" in t and "Madras University" in t
def test_cv_parse_rules_endpoint():
    r = c.post("/api/v1/cv/parse", json=dict(text=CVTXT)); assert r.status_code == 200, r.text; j = r.json()
    assert j["mode"] == "rules" and j["current_role"] == "Records Clerk" and len(j["work_examples"]) == 2 and j["ignored_lines"] >= 3
    assert "Record management" in j["skills"] and "Scheduling" in j["skills"] and "Tally" in j["tools"]
    assert j["certifications"] == [dict(name="Basic Computer Course", issuer="NIIT")] and j["education"][0]["level"] == "bachelor" and j["education"][0]["institution"] == "Madras University"
    assert j["languages"] == ["Tamil", "English"]
    blob = json.dumps(j).lower(); assert "12 years" not in blob and "2010" not in blob and "female" not in blob
def test_cv_parse_model_answer_is_grounded(monkeypatch):
    cleaned, _ = CV.clean(CVTXT)
    ans = dict(current_role="Records Clerk", work_examples=["Scheduled parent meetings and sent emails to families", "Won an award for excellence"], skills=["Scheduling", "Telepathy"], tools=["Tally", "Photoshop"],
               certifications=[dict(name="Basic Computer Course", issuer="NIIT"), dict(name="Invented Diploma", issuer="Nobody")], education=[dict(line="B.Com in Commerce, Madras University", level="bachelor", field="Commerce", institution="Madras University")], languages=["Tamil", "Klingon"])
    monkeypatch.setattr(llm, "ask_json", lambda task, system, user: (ans, "live")); j = c.post("/api/v1/cv/parse", json=dict(text=CVTXT)).json()
    assert j["mode"] == "llm+rules" and j["work_examples"] == ["Scheduled parent meetings and sent emails to families"] and "Photoshop" not in j["tools"] and "Telepathy" not in j["skills"]
    assert [x["name"] for x in j["certifications"]] == ["Basic Computer Course"] and j["languages"] == ["Tamil"]
def test_cv_parse_validation():
    assert c.post("/api/v1/cv/parse", json=dict(text="too short")).status_code == 422
    r = c.post("/api/v1/cv/parse", json=dict(text="Just a paragraph of words without any headings at all, nothing to find here really.")); assert r.status_code == 200 and r.json()["warnings"]

# ---- background and the generated CV ----
def test_background_roundtrip_and_validation():
    pid, _ = make(); bg = dict(education=[dict(level="bachelor", field="Commerce", institution="Madras University")], certifications=[dict(name="Basic Computer Course", issuer="NIIT")], languages=["Tamil"], tools=["Tally"], barriers=["time", "confidence"], situation="returning")
    assert c.put(f"/api/v1/profiles/{pid}/background", json=bg).status_code == 200 and c.get(f"/api/v1/profiles/{pid}/background").json()["barriers"] == ["time", "confidence"]
    assert c.put(f"/api/v1/profiles/{pid}/background", json=dict(age=40)).status_code == 422 and c.put(f"/api/v1/profiles/{pid}/background", json=dict(barriers=["a", "b"])).status_code == 422
    assert c.get("/api/v1/profiles/prof_nope/background").status_code == 404
def test_generated_cv_is_honest_and_age_free(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch, 2); o = st["order"]
    c.put(f"/api/v1/profiles/{pid}/background", json=dict(education=[dict(level="bachelor", field="Commerce", institution="Madras University")], certifications=[dict(name="Basic Computer Course", issuer="NIIT")], languages=["Tamil"], tools=["Tally"]))
    before = c.get(f"/api/v1/profiles/{pid}/cv").json(); assert "Completed:" not in before["text"] and before["file_name"].endswith("_updated_CV.txt")
    for cid in ("c1", "c2"): c.post(f"/api/v1/profiles/{pid}/steps/{o}/chapters", json=dict(chapter_id=cid, done=True))
    mid = c.get(f"/api/v1/profiles/{pid}/missions").json()["today_mission_id"]; c.post(f"/api/v1/profiles/{pid}/missions/{mid}/proof", json=dict(file_name="a.txt", content_base64="QQ=="))
    after = c.get(f"/api/v1/profiles/{pid}/cv").json(); t = after["text"]
    assert f"Completed: {st['resource']['title']}" in t and "Practical task completed:" in t and "Basic Computer Course, NIIT" in t and "Bachelor's degree, Commerce, Madras University" in t and "Tally" in t
    low = t.lower()
    for bad in ("year", "age", "female", "male", "born", "19", "20"): assert bad not in low.replace("language", "").replace("manage", "").replace("package", "").replace("message", "").replace("engage", "").replace("coordinat", ""), bad
    assert set(after["sections"]) >= {"SUMMARY", "SKILLS", "EXPERIENCE"}
def test_cv_requires_confirmed_skills():
    pid, _ = make(); r = c.get(f"/api/v1/profiles/{pid}/cv"); assert r.status_code == 409 and r.json()["error"]["code"] == "SKILLS_NOT_CONFIRMED"
def test_scout_skips_courses_the_person_already_did(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch); title = st["resource"]["title"]
    c.put(f"/api/v1/profiles/{pid}/background", json=dict(certifications=[dict(name=title.upper())]))
    s = c.post(f"/api/v1/profiles/{pid}/scout").json(); assert all(cand["title"] != title for x in s["steps"] for cand in x["candidates"])

# ---- audit fixes: course policy on approve, one cap on live model calls ----
def test_scout_approve_refuses_course_the_policy_disallows(monkeypatch):
    pid, plan, st = journey_with_course(monkeypatch); sid = st["skill_id"]; rid = st["resource"]["resource_id"]
    monkeypatch.setattr(M, "ALLOW_UNVERIFIED", False); monkeypatch.setattr(M, "ALLOW_SAMPLE", False)
    bad = next(r for r in RES if sid in r["skill_ids"] and r["verification_status"] != "verified")
    r = c.post(f"/api/v1/profiles/{pid}/scout/approve", json=dict(choices=[dict(order=st["order"], resource_id=bad["resource_id"])]))
    assert r.status_code == 422 and "policy" in r.json()["error"]["message"]
def test_live_model_calls_share_one_cap_and_pause_after_failure(monkeypatch):
    n = []; monkeypatch.setattr(llm, "live_ready", lambda: True); monkeypatch.setattr(llm, "_calls", []); monkeypatch.setattr(llm, "_down_until", 0.0)
    monkeypatch.setattr(llm, "_gemini", lambda s, u: n.append(1) or {"ok": 1}); monkeypatch.setenv("RATE_LIMIT_PER_MIN", "2")
    got = [llm.ask_json("t", "s", f"u{i}")[0] for i in range(4)]; assert len(n) == 2 and got == [{"ok": 1}, {"ok": 1}, None, None]
    monkeypatch.setattr(llm, "_calls", []); monkeypatch.setattr(llm, "_gemini", lambda s, u: 1 / 0)
    assert llm.ask_json("t", "s", "x")[0] is None and llm._down_until > 0 and llm.ask_json("t", "s", "y")[0] is None
