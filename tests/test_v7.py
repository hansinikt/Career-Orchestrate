"""Missions follow the courses of the chosen role."""
import base64
from fastapi.testclient import TestClient
from backend.app import main as M
from tests.test_v4 import make
c = TestClient(M.app)

def test_missions_follow_the_chosen_roles_courses_one_at_a_time():
    pid, p = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]]))
    c.post(f"/api/v1/profiles/{pid}/plan", json=dict(role_id="R001"))
    path = c.get(f"/api/v1/profiles/{pid}/paths/R001").json()["courses"]; ms = c.get(f"/api/v1/profiles/{pid}/missions").json()["missions"]
    assert path and ms and ms[0]["source"] == f"Course 1: {path[0]['title']}" and path[0]["title"] in ms[0]["title"] and ms[0]["status"] == "open"
    assert sum(1 for m in ms if m["status"] == "open") == 1                          # one at a time
    assert all(m["status"] == "locked" for m in ms if not m["source"].startswith("Course 1:"))   # later courses stay locked
    assert len({m["title"] for m in ms}) == len(ms)                                   # no two missions are the same
def test_recommendations_list_skills_to_build_and_path_has_sections():
    pid, p = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]]))
    recs = c.get(f"/api/v1/profiles/{pid}/recommendations").json()["recommendations"]; hr = next(r for r in recs if r["role_id"] == "R001")
    assert len(hr["build_skills"]) >= 4 and "Onboarding" in hr["build_skills"] and hr["course_count"] >= 3 and hr["course_hours"] > 20
    first = c.get(f"/api/v1/profiles/{pid}/paths/R001").json()["courses"][0]; assert first["units"] and "topics" in first
def test_encouragement_names_a_course_not_a_skill():
    pid, p = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]]))
    c.post(f"/api/v1/profiles/{pid}/plan", json=dict(role_id="R001"))
    n = M.plan_nums(pid, M.active_plan(pid)["steps"], {}, 6); first = c.get(f"/api/v1/profiles/{pid}/paths/R001").json()["courses"][0]["title"]
    assert n["next_step"] == first

def test_contract_limits_lifted_and_education_levels():
    from contracts.v2 import models as C
    C.Preferences(interests=["people", "data", "operations", "planning", "compliance"], weekly_hours=6)
    C.MotivationPrefs(styles=["progress", "goals", "encouragement", "accountability", "challenge"], check_in="weekly")
    C.Background(education=[dict(level="grade10", field="Commerce"), dict(level="grade12", institution="School"), dict(level="bachelor"), dict(level="master")],
                 barriers=["time", "money", "confidence", "device_internet", "language", "caring_duties", "unsure_start"])

def test_profile_accepts_all_five_styles_and_interests():
    pid, p = make()
    body = c.get(f"/api/v1/profiles/{pid}").json()
    r = c.put(f"/api/v1/profiles/{pid}/motivation", json=dict(styles=["progress", "goals", "encouragement", "accountability", "challenge"], check_in="daily", paused=False)); assert r.status_code == 200
    r = c.put(f"/api/v1/profiles/{pid}/background", json=dict(education=[dict(level="grade10", field="Commerce", institution="School")], barriers=["time", "money", "confidence", "device_internet"])); assert r.status_code == 200

def test_background_keeps_several_situations():
    pid, p = make()
    r = c.put(f"/api/v1/profiles/{pid}/background", json=dict(situation="promotion", situations=["promotion", "returning", "other"])); assert r.status_code == 200
    assert c.get(f"/api/v1/profiles/{pid}/background").json()["situations"] == ["promotion", "returning", "other"]

def test_progress_follows_course_missions():
    pid, p = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]]))
    c.post(f"/api/v1/profiles/{pid}/plan", json=dict(role_id="R001"))
    ms = c.get(f"/api/v1/profiles/{pid}/missions").json()["missions"]
    assert c.get(f"/api/v1/profiles/{pid}/progress").json()["percent"] == 0
    m = next(x for x in ms if x["status"] == "open")
    c.post(f"/api/v1/profiles/{pid}/missions/{m['mission_id']}/proof", json=dict(file_name="a.txt", content_base64="aGVsbG8="))
    pr = c.get(f"/api/v1/profiles/{pid}/progress").json()
    assert pr["percent"] > 0 and pr["steps_total"] >= 3 and pr["steps"][0]["skill_name"] == ms[0]["source"].split(": ", 1)[1]

def test_every_course_has_its_own_two_sentence_summary():
    import json, re
    from backend.app import agents as A
    ids = {x["course_id"] for x in json.load(open("data/v2/role_courses.json"))["courses"]}
    assert ids == set(A.BLURBS)                                           # no course is missing a written summary
    assert len(set(A.BLURBS.values())) == len(ids)                         # every course reads differently
    for t in A.BLURBS.values():
        assert len(re.findall(r"[.!?](?:\s|$)", t)) == 2 and not re.search(r"\d", t.replace("S/4HANA", ""))   # two sentences, no numbers that could be wrong
    pid, p = make(); e = c.post(f"/api/v1/profiles/{pid}/extract").json()
    c.post(f"/api/v1/profiles/{pid}/confirm", json=dict(decisions=[dict(suggestion_id=s["suggestion_id"], action="accept") for s in e["suggestions"]]))
    why = [x["why"] for x in c.get(f"/api/v1/profiles/{pid}/paths/R001").json()["courses"]]
    assert len(set(why)) == len(why) >= 3
