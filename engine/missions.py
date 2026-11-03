"""Missions: small tasks built from plan steps (or, when the course has a chapter list, from its chapters) with fixed templates. No model, no invented content."""
import re
def _unit(u): return re.sub(r"\s*\([^)]*\)\s*$", "", u).strip()   # "Project Planning (23 h)" -> "Project Planning"
def build(steps: list, done_ids: set, started_ids: set = frozenset(), declined_ids: set = frozenset(), chapters_by_step: dict | None = None, limit: int = 24, per_course: int = 3) -> list:
    chapters_by_step = chapters_by_step or {}; raw = []
    for s in steps:
        name = s["skill_name"]; chs = chapters_by_step.get(s["order"]) or []
        if s.get("course"):
            # a course from the chosen role's path: one mission per section, using the section names listed on the course page. Nothing is invented about the course.
            units = [_unit(u) for u in (s.get("units") or []) if _unit(u)][:per_course] or [None]; src = f"Course {s['order']}: {name}"
            for j, u in enumerate(units, 1):
                if u is None:
                    mid, title = f"m{s['order']}", (f"Start your first course: {name}" if s["order"] == 1 else f"Start: {name}")
                    brief = f"Open the course \"{name}\" and finish its first lesson. Then write 3 to 5 sentences about what you learned and how you could use it in your work. Upload it as your proof."
                else:
                    mid, title = f"m{s['order']}u{j}", f"{name}: {u}"
                    brief = f"Work through the section \"{u}\" of the course \"{name}\". Then write 3 to 5 sentences about one idea from it and how you could use it in your own work. Upload it as your proof."
                raw.append(dict(mission_id=mid, order=len(raw) + 1, chapter_title=None, title=title, brief=brief, source=src, course_order=s["order"]))
        elif chs:
            for i, ch in enumerate(chs, 1):
                raw.append(dict(mission_id=f"m{s['order']}c{i}", order=len(raw) + 1, chapter_title=ch["title"], title=f"Show what you learned: {ch['title']}",
                                brief=f"Write one short paragraph (3 to 5 sentences) about how you would use \"{ch['title']}\" in your own work. Upload it as your proof.", source=f"Step {s['order']} · {name}"))
        else:
            raw.append(dict(mission_id=f"m{s['order']}", order=len(raw) + 1, chapter_title=None, title=f"Show your {name} in practice",
                            brief=f"Write one short paragraph (3 to 5 sentences) about a real task where you used {name}. Upload it as your proof.", source=f"Step {s['order']}"))
    out = []
    by_course = {}
    for m in raw: by_course.setdefault(m.get("course_order"), []).append(m["mission_id"])
    open_left = 1 if any(k is not None for k in by_course) else 2   # course missions go one at a time
    def unlocked(co):   # a course's missions open only when every mission of the course before it is done
        if co is None or co <= 1: return True
        prev = [k for k in by_course if k is not None and k < co]
        return all(i in done_ids for k in prev for i in by_course[k])
    for m in raw[:limit]:
        mid = m["mission_id"]; m = {k: v for k, v in m.items() if k != "course_order"} | {"_co": m.get("course_order")}
        co = m.pop("_co")
        if mid in done_ids: status, pct = "done", 100
        elif not unlocked(co): status, pct = "locked", 0
        elif mid in declined_ids: status, pct = "declined", 0
        elif open_left > 0: status, pct = "open", (50 if mid in started_ids else 0); open_left -= 1
        else: status, pct = "locked", 0
        out.append(dict(m, status=status, percent=pct))
    return out
