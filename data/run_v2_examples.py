"""Runs the reference engine on the v2 seed. Output = the verified worked examples quoted in the PRD."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from engine import core as E
V2 = pathlib.Path(__file__).resolve().parent / "v2"; FX = V2 / "fixtures"
sk, roles, res = E.load("v2"); P = json.loads((V2 / "personas.json").read_text())
title2id = {r["title"]: r["role_id"] for r in roles}
out = {"all_personas": {}}
for uid, p in P.items():
    recs = E.rank(p["confirmed_levels"], roles, [], sk)
    tid = title2id[p["target_role_stated"]]; tr = next(r for r in recs if r["role_id"] == tid)
    out["all_personas"][uid] = dict(name=p["name"], stated_target=p["target_role_stated"], target_rank=tr["rank"], target_band=tr["band"],
        target_score=tr["score"], target_gap_hours=tr["est_gap_hours"], target_blocking=tr["blocking_gaps"], top3=[(r["role_id"], r["title"], r["score"], r["band"]) for r in recs[:3]])
# Anitha U001 detail
A = P["U001"]; base = dict(A["confirmed_levels"])
inferred = {"SK-SCHED": 2, "SK-REPORT": 2}      # extracted from work text, pending worker confirmation (cap 2 for inferred)
after = {**base, **inferred}
ev = {"SK-SCHED": ["Coordinated calendars"], "SK-REPORT": ["prepared reports"], "SK-RECORDS": ["maintained records"], "SK-COMM": ["supported cross-team communication"]}
assert all(E.quote_is_grounded(q, [A["work_text"]]) for v in ev.values() for q in v)
def summ(recs): return [(r["rank"], r["role_id"], r["title"], r["score"], r["band"], r["feature_scores"], r["est_gap_hours"], r["blocking_gaps"]) for r in recs]
r0 = E.rank(base, roles, [], sk); r1 = E.rank(after, roles, [], sk); r2 = E.rank(after, roles, ["people", "operations"], sk)
out["anitha"] = dict(levels_before=base, levels_after=after, ranking_confirmed_only=summ(r0), ranking_after_inferred=summ(r1), ranking_with_prefs=summ(r2))
hr = next(r for r in r1 if r["role_id"] == "R001"); out["anitha"]["R001_detail"] = dict(matched=hr["matched"], gaps=hr["gaps"], explanation=hr["explanation"])
for label, kw in [("plan_strict", dict(allow_unverified=False, allow_sample=False)), ("plan_demo_with_samples", dict(allow_unverified=True, allow_sample=True))]:
    plan = E.build_plan(hr, after, sk, res, 6, **kw); out["anitha"][label] = dict(total=plan["total_est_hours"], weeks=plan["weeks_at_pace"], unresolved=plan["unresolved_skill_ids"],
        steps=[(s["order"], s["skill_name"], s["status"], (s["resource"] or {}).get("resource_id"), s["est_hours"]) for s in plan["steps"]])
# audit demo: clean variants vs a deliberately biased canary
basecase = dict(skills=after, recs=r1, plan_hours=hr["est_gap_hours"], text="Prepared reports and coordinated calendars.")
canary_levels = {k: max(1, v - 1) if v >= 2 else v for k, v in after.items()}
rc = E.rank(canary_levels, roles, [], sk); hrc = next(r for r in rc if r["role_id"] == "R001")
cm = E.compare(basecase, dict(skills=canary_levels, recs=rc, plan_hours=hrc["est_gap_hours"], text="Seasoned administrator, may struggle to adapt to new technology."))
out["audit"] = dict(clean=E.compare(basecase, basecase), canary=cm, canary_flags=[f["metric"] for f in E.flags_for("A58", cm)], thresholds=E.THRESH)
# stability of top-3 for Anitha under alternative weights (sensitivity)
sens = {}
for name, w in dict(default=(0.60, 0.15, 0.25), cov_heavy=(0.70, 0.10, 0.20), learn_heavy=(0.50, 0.15, 0.35), equal=(0.34, 0.33, 0.33)).items():
    E.WEIGHTS.update(skill_coverage=w[0], preference_fit=w[1], learnability=w[2]); rr = E.rank(after, roles, ["people", "operations"], sk); sens[name] = [r["role_id"] for r in rr[:3]]
E.WEIGHTS.update(skill_coverage=0.60, preference_fit=0.15, learnability=0.25); out["anitha"]["weight_sensitivity_top3"] = sens
json.dump(out, open(FX / "_worked_examples_v2.json", "w"), indent=1, default=list)
print(json.dumps(out, indent=1, default=list))
