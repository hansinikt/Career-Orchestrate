"""Builds data/v2/*.json from the team's CSVs in data/source/. Deterministic; re-run after editing the CSVs or the tables below.
Everything marked PROVISIONAL is a team judgement, not a fact."""
import csv, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
SRC, OUT = ROOT / "source", ROOT / "v2"; OUT.mkdir(exist_ok=True)
rd = lambda f: list(csv.DictReader(open(SRC / f, encoding="utf-8")))
LEVEL = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}          # dataset 3-point scale -> engine levels
IMPORTANCE = {"Required": 5, "Preferred": 3}                        # PROVISIONAL
MANDATORY = {"Required": True, "Preferred": False}

# canonical skills: name -> (id, category, hours_per_level PROVISIONAL)
CANON = {
 "Excel": ("SK-EXCEL", "data", 15), "Communication": ("SK-COMM", "people", 12), "Record management": ("SK-RECORDS", "operations", 12),
 "Scheduling": ("SK-SCHED", "operations", 12), "Confidentiality": ("SK-CONF", "compliance", 12), "Documentation": ("SK-DOC", "operations", 12),
 "Risk tracking": ("SK-RISK", "operations", 12), "Reporting": ("SK-REPORT", "data", 15), "SQL": ("SK-SQL", "data", 20),
 "Data cleaning": ("SK-DATACLEAN", "data", 15), "Statistics": ("SK-STATS", "data", 20), "Visualization": ("SK-VIZ", "data", 15),
 "Process analysis": ("SK-PROCANALYSIS", "analysis", 15), "Requirements gathering": ("SK-REQ", "analysis", 15),
 "Process improvement": ("SK-PROCIMPROVE", "analysis", 15), "Data analysis": ("SK-DATAANALYSIS", "data", 15),
 "Problem solving": ("SK-PROBLEM", "analysis", 12), "Training coordination": ("SK-TRAINCOORD", "people", 12),
 "Learning administration": ("SK-LEARNADMIN", "people", 12), "CRM tools": ("SK-CRM", "data", 12), "Data quality": ("SK-DATAQUALITY", "data", 12),
 "Dashboard basics": ("SK-DASH", "data", 15), "Document control": ("SK-DOCCONTROL", "compliance", 12),
 "Attention to detail": ("SK-DETAIL", "compliance", 12), "Compliance documentation": ("SK-COMPDOC", "compliance", 12)}
# names that appear only in user_skills.csv / courses. ALIAS = proposed synonym of a canonical skill (needs team + worker confirmation).
EXTRA = {"Stakeholder communication": ("SK-X-STAKEHOLDER", "Communication"), "Case documentation": ("SK-X-CASEDOC", "Documentation"),
         "Sales reporting": ("SK-X-SALESREP", "Reporting"), "Team coordination": ("SK-X-TEAMCOORD", None), "Presentation skills": ("SK-X-PRESENT", None),
         "Microsoft Office": ("SK-X-MSOFFICE", None), "Customer service": ("SK-X-CUSTSERV", None), "Process coordination": ("SK-X-PROCCOORD", None),
         "HR administration": ("SK-X-HRADMIN", None)}
# role tags used for the optional interest-fit feature (PROVISIONAL team judgement)
TAGS = {"R001": ["people", "operations"], "R002": ["planning", "operations"], "R003": ["data"], "R004": ["data", "planning"],
        "R005": ["operations", "data"], "R006": ["people", "planning"], "R007": ["data", "people"], "R008": ["compliance", "operations"]}

skills = []
for n, (i, cat, h) in CANON.items():
    skills.append(dict(skill_id=i, name=n, category=cat, aliases=[], hours_per_level=h, prerequisites=[], alias_of=None, alias_status=None, scored=True))
for n, (i, canon) in EXTRA.items():
    skills.append(dict(skill_id=i, name=n, category="extra", aliases=[], hours_per_level=12, prerequisites=[],
                       alias_of=CANON[canon][0] if canon else None, alias_status="proposed" if canon else None, scored=False))
SID = {s["name"]: s["skill_id"] for s in skills}
json.dump(dict(taxonomy_version="v2-csv-0.1", source="team CSVs (illustrative)", skills=skills), open(OUT / "skills.json", "w"), indent=1)

roles = []
for r in rd("career_roles.csv"):
    reqs = [dict(skill_id=SID[q["skill_name"]], importance=IMPORTANCE[q["requirement_type"]], required_level=LEVEL[q["target_proficiency"]],
                 mandatory=MANDATORY[q["requirement_type"]]) for q in rd("role_skill_requirements.csv") if q["role_id"] == r["role_id"]]
    roles.append(dict(role_id=r["role_id"], title=r["role_title"], summary=r["role_summary"], family=r["career_family"], tags=TAGS[r["role_id"]],
                      requirements=reqs, requires_degree=False, max_experience_years=None, data_note=r["data_note"]))
json.dump(dict(dataset_version="v2-csv-0.1", roles=roles), open(OUT / "roles.json", "w"), indent=1)

DUR = {"C001": "2-4 weeks", "C002": "2-3 weeks"}
resources = []
for c in rd("learning_resources.csv"):
    ids = [SID[s.strip()] for s in c["skills_covered_semicolon_separated"].split(";")]
    real_page = bool(c["resource_url"]) and c["resource_url"].rstrip("/").count("/") > 2
    status = "verified" if real_page else ("seed_unverified" if c["resource_url"] else "sample_placeholder")
    resources.append(dict(resource_id=c["course_id"], title=c["course_title"], provider=c["provider_or_source"], url=c["resource_url"] or None,
                          skill_ids=ids, level_from=0, level_to=1, est_hours=None, duration_text=c["estimated_duration"], cost="unknown",
                          verification_status=status, last_verified=None,
                          note="homepage only, not a course page" if status == "seed_unverified" else ("no provider or URL in source data" if status == "sample_placeholder" else "")))
json.dump(dict(catalog_version="v2-csv-0.1", note="Statuses: verified | seed_unverified (homepage only) | sample_placeholder (no provider/URL). Only a human sets 'verified'.", resources=resources),
          open(OUT / "resources.json", "w"), indent=1)

# personas: confirmed levels from user_skills.csv. alias-mapped skills are marked so the UI asks the worker to confirm them.
profiles = {p["user_id"]: p for p in rd("user_profiles.csv")}; exp = {e["user_id"]: e for e in rd("work_experience.csv")}
byid = {s["skill_id"]: s for s in skills}; personas = {}
for uid, p in profiles.items():
    conf, alias_used, unscored, declared = {}, [], [], []
    for s in rd("user_skills.csv"):
        if s["user_id"] != uid: continue
        meta = byid[SID[s["skill_name"]]]; lv = LEVEL[s["proficiency"]]; declared.append(dict(name=s["skill_name"], level=lv))
        if meta["scored"]: conf[meta["skill_id"]] = lv
        elif meta["alias_of"]:
            tgt = meta["alias_of"]; alias_used.append(dict(from_skill=s["skill_name"], to=byid[tgt]["name"], level=lv)); conf[tgt] = max(conf.get(tgt, 0), lv)
        else: unscored.append(s["skill_name"])
    personas[uid] = dict(user_id=uid, name=p["name"], current_role=p["current_role"], target_role_stated=p["target_role"], country=p["country"],
                         work_text=exp[uid]["responsibilities"], declared_skills=declared, stated_goal_role_id=next(r["role_id"] for r in roles if r["title"] == p["target_role"]), confirmed_levels=conf, alias_mapped=alias_used, unscored_skills=unscored)
json.dump(personas, open(OUT / "personas.json", "w"), indent=1)
print("skills", len(skills), "roles", len(roles), "resources", len(resources), "personas", len(personas))
