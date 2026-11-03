"""Market Intelligence: deterministic, from OUR catalogue only. It counts how many catalogue roles ask for each skill. It is not live job-market data and never invents numbers."""
def market_view(levels: dict, roles: list, sk: dict, top_role_ids: list) -> dict:
    asking, mand = {}, {}
    for r in roles:
        for q in r["requirements"]:
            asking[q["skill_id"]] = asking.get(q["skill_id"], 0) + 1
            if q["mandatory"]: mand[q["skill_id"]] = mand.get(q["skill_id"], 0) + 1
    def row(sid): return dict(skill_id=sid, name=sk[sid]["name"], roles_asking=asking.get(sid, 0), mandatory_in=mand.get(sid, 0))
    held = sorted((row(s) for s in levels if s in sk), key=lambda x: (-x["roles_asking"], x["name"]))
    top = [r for r in roles if r["role_id"] in top_role_ids]
    wanted = {q["skill_id"] for r in top for q in r["requirements"] if q["skill_id"] not in levels}
    nxt = sorted((row(s) for s in wanted), key=lambda x: (-x["roles_asking"], -x["mandatory_in"], x["name"]))[:6]
    return dict(roles_in_catalogue=len(roles), top_role_ids=list(top_role_ids), held=held, next_skills=nxt,
                source_note=f"Counts come from the {len(roles)} roles in this app's catalogue. They are not live job-market data.")
