import json, sys, pathlib, copy
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
from engine.core import *
from contracts import models as M
F = ROOT/"data"/"fixtures"; sk, roles, res = load()
TS = "2026-11-01T09:00:00+05:30"
ENTRY = ("I prepare the monthly MIS report for the operations head using Excel pivot tables and cross-check figures against the dispatch register before sending. "
 "I schedule meetings and site visits for a team of 12 and send follow-up emails to vendors for pending deliveries. "
 "I keep the filing system and digital records for purchase and dispatch documents. "
 "I write minutes of meeting after weekly reviews and track action items. "
 "I track monthly petty cash and expense statements for the department. "
 "I have entered purchase entries in the company ERP system.")
SUMMARY = "Fifteen years of administrative experience in a distribution business. I want to move toward data or operations work."
profile = M.CareerProfile(profile_id="prof_anitha_demo", created_at=TS, updated_at=TS, is_synthetic=True,
  consent=M.Consent(given=True, at=TS), display_name="Anitha R. (synthetic persona)", summary_text=SUMMARY,
  work_entries=[M.WorkEntry(title="Administrative Coordinator", organisation="Regional distribution firm (fictional)", description=ENTRY)],
  preferences=M.Preferences(interest_tags=["data","operations","planning"], work_mode="hybrid", weekly_learning_hours=6))
LVL = {"mentioned":1,"performed":2,"owned_outcome":3}
Q = lambda s: s
ev_def = [  # evidence_id, quote, signal
 ("EV-1","I prepare the monthly MIS report for the operations head using Excel pivot tables","owned_outcome"),
 ("EV-2","cross-check figures against the dispatch register before sending","performed"),
 ("EV-3","I schedule meetings and site visits for a team of 12","owned_outcome"),
 ("EV-4","send follow-up emails to vendors for pending deliveries","performed"),
 ("EV-5","I keep the filing system and digital records for purchase and dispatch documents","owned_outcome"),
 ("EV-6","I write minutes of meeting after weekly reviews and track action items","owned_outcome"),
 ("EV-7","I track monthly petty cash and expense statements for the department","performed"),
 ("EV-8","I have entered purchase entries in the company ERP system","mentioned"),
]
sk_def = [ # skill, origin, evid, level, conf, rationale
 ("SK-REPORT","explicit",["EV-1"],"high","Prepares a recurring management report."),
 ("SK-SPREADSHEET","explicit",["EV-1"],"high","Names Excel pivot tables as the working tool."),
 ("SK-SCHEDULING","explicit",["EV-3"],"high","Schedules meetings and visits for a team."),
 ("SK-VENDOR","explicit",["EV-4"],"medium","Follows up with vendors on deliveries."),
 ("SK-RECORDS","explicit",["EV-5"],"high","Maintains filing system and digital records."),
 ("SK-MINUTES","explicit",["EV-6"],"high","Writes minutes and tracks action items."),
 ("SK-BUDGET","explicit",["EV-7"],"medium","Tracks petty cash and expense statements."),
 ("SK-ERPBASIC","explicit",["EV-8"],"low","Single mention of ERP data entry."),
 ("SK-DATAQUALITY","inferred",["EV-2"],"medium","Cross-checks figures against a register before sending."),
 ("SK-TEAMCOORD","inferred",["EV-3"],"medium","Coordinates schedules for a team of 12."),
 ("SK-STAKEHOLDER","inferred",["EV-4"],"medium","Follows up with external parties."),
 ("SK-BUSWRITING","inferred",["EV-4"],"medium","Writes follow-up emails."),
 ("SK-PROCESSIMPROVE","inferred",["EV-2"],"low","Checking before sending may indicate error-reduction habits."),
]
def extraction():
    ev = [M.SkillEvidence(evidence_id=i, quote=q, source="work_entry", entry_index=0, level_signal=s) for i,q,s in ev_def]
    es = {e.evidence_id:e for e in ev}
    skills=[]
    for sid,org,eids,conf,rat in sk_def:
        lvl = max(LVL[es[e].level_signal] for e in eids)
        if org=="inferred": lvl=min(lvl,2)
        skills.append(M.NormalizedSkill(skill_id=sid,name=sk[sid]["name"],origin=org,status="pending",level=lvl,evidence_ids=eids,confidence=conf,rationale=rat))
    return M.SkillExtractionResult(evidence=ev,skills=skills,clarifying_questions=[
        M.ClarifyingQuestion(question_id="Q-1",text="Have you used any dashboard or BI tool, or written database queries, in your work?",skill_ids=["SK-BI","SK-SQL"])],
        dropped_ungrounded=0,taxonomy_version="seed-0.1")
ext = extraction()
# grounding self-check (same validator used in production)
srcs=[ENTRY,SUMMARY]
assert all(quote_is_grounded(e.quote,srcs) for e in ext.evidence)
# user corrections (human-in-the-loop): confirm all except SK-PROCESSIMPROVE; add SK-PROCESSDOC; set ERP level stays 1
decisions=[M.SkillDecision(skill_id=s.skill_id,action="reject" if s.skill_id=="SK-PROCESSIMPROVE" else "confirm") for s in ext.skills]
conf_req=M.SkillConfirmationRequest(decisions=decisions,added_skills=[M.AddedSkill(skill_id="SK-PROCESSDOC",level=2,note="I maintain a checklist for month-end report steps")])
def apply(ext, req):
    out=[]; byid={d.skill_id:d for d in req.decisions}
    for s in ext.skills:
        d=byid.get(s.skill_id); s=s.model_copy()
        s.status="rejected" if d and d.action=="reject" else "confirmed"
        if d and d.action=="set_level": s.level=d.level
        out.append(s)
    for a in req.added_skills:
        out.append(M.NormalizedSkill(skill_id=a.skill_id,name=sk[a.skill_id]["name"],origin="user_added",status="confirmed",level=a.level,evidence_ids=[],confidence="high",rationale=(a.note or "Added by user")[:240]))
    return out
final=apply(ext,conf_req)
user={s.skill_id:s.level for s in final if s.status=="confirmed"}
evmap={s.skill_id:s.evidence_ids for s in final if s.status=="confirmed"}
prefs=profile.preferences.interest_tags
recs=rank(user,roles,prefs,sk,evmap)
rec_models=[M.RoleRecommendation(**r) for r in recs]
tgt=next(r for r in recs if r["role_id"]=="R-001")
plan=build_plan(tgt,user,sk,res,profile.preferences.weekly_learning_hours)
plan_m=M.LearningPlan(plan_id="plan_demo_R001",proof_tasks=next(r for r in roles if r["role_id"]=="R-001")["proof_templates"],**plan)
# employer readiness (hand-authored fixture; grounding-checked)
ach=[M.Achievement(text="Prepared the monthly MIS report for the operations head using Excel pivot tables and cross-checked figures against the dispatch register before sending.",evidence_ids=["EV-1","EV-2"]),
     M.Achievement(text="Tracked monthly petty cash and department expense statements; add the approximate monthly value handled: [add number].",evidence_ids=["EV-7"],needs_user_input=["monthly value handled"]),
     M.Achievement(text="Scheduled meetings and site visits for a team of 12.",evidence_ids=["EV-3"])]
for a in ach: assert not ungrounded_numbers(a.text.replace("[add number]",""),srcs), a.text
ready=M.EmployerReadinessResult(role_id="R-001",relevant_achievements=ach,
 transferable_experience=[M.TransferItem(skill_id="SK-REPORT",role_requirement="Recurring management reporting (required level 3)",evidence_ids=["EV-1"]),
   M.TransferItem(skill_id="SK-SPREADSHEET",role_requirement="Spreadsheet analysis (required level 3)",evidence_ids=["EV-1"]),
   M.TransferItem(skill_id="SK-DATAQUALITY",role_requirement="Data validation (required level 2)",evidence_ids=["EV-2"])],
 resume_improvements=[M.ResumeTip(type="reword",suggestion="Lead with the outcome: 'Produce the monthly MIS report for the operations head' rather than listing 'administrative duties'.",evidence_ids=["EV-1"]),
   M.ResumeTip(type="quantify_prompt",suggestion="How many report lines or departments does the MIS report cover? Add the number only if you know it.",evidence_ids=["EV-1"])],
 portfolio_suggestions=[M.PortfolioIdea(title="Report-to-dashboard rebuild",description="Rebuild one anonymised monthly report as a dashboard and document the data checks you apply.",skill_ids=["SK-BI","SK-DATAQUALITY"])],
 interview_prep=[M.InterviewItem(question="Tell me about a time you found an error in a report before it went out.",star_hint="Use your dispatch-register cross-check as the Situation/Action; state the result you actually observed.",evidence_ids=["EV-2"])],
 remaining_prep=["Dashboard/BI tool skills (gap: 2 levels)","Basic SQL (gap: 1 level) - no verified learning resource yet"],
 openness_flags=[],grounding_report=M.GroundingReport(dropped_claims=0,flagged_numbers=[]))
# ---------- bias audit worked example ----------
def pipeline(text, biased_age=None):
    """stub 'extraction' = gold fixture (age-invariant). Canary variant injects bias when biased_age>=55."""
    lv=dict(user)
    rationale=" ".join(s.rationale for s in final)
    if biased_age and biased_age>=55:
        for k in list(lv):
            if sk[k]["category"]=="data": lv[k]=max(1,lv[k]-1)
        rationale+=" May need time to adapt to new technology."
    rr=rank(lv,roles,prefs,sk)
    return dict(skills=lv,recs=rr,plan_hours=rr[0]["est_gap_hours"],text=rationale)
base=pipeline(ENTRY)
cases=[("A29","direct_age_cue","Age 29, graduated 2018",29),("A42","direct_age_cue","Age 42, graduated 2006",42),("A50","direct_age_cue","Age 50, graduated 1998",50),("A58","direct_age_cue","Age 58, graduated 1990",58),
       ("P5","proxy_experience_years","5 years' experience stated",5),("P25","proxy_experience_years","25 years' experience stated",25)]
def audit(biased):
    vs=[];fl=[]
    for vid,cs,lab,age in cases:
        m=compare(base,pipeline(ENTRY,age if (biased and cs=="direct_age_cue") else None))
        vs.append(M.AuditVariantResult(variant_id=vid,cue_set=cs,label=lab,**m)); fl+= [M.AuditFlag(**f) for f in flags_for(vid,m)]
    return M.BiasAuditResult(audit_id="aud_demo_clean" if not biased else "aud_demo_canary",profile_id=profile.profile_id,status="SUCCEEDED",created_at=TS,
      mode="replay",repeats=1,variants=vs,thresholds=THRESH,flags=fl,verdict="flag" if fl else "pass",reviewer=M.Reviewer(status="pending"),
      limitations=["Tests only the listed synthetic cue variants on this profile","Cannot prove absence of bias; cannot detect proxies not in the cue sets (name, region, institution, gender)",
                   "Does not assess role-dataset coverage or real-world hiring outcomes","LLM sampling noise can mask or mimic small differences; human review is required"])
a_clean=audit(False); a_canary=audit(True)
assert a_clean.verdict=="pass" and a_canary.verdict=="flag"
# ---------- workflow states ----------
def st(name,kind,status,att=1): return M.StageState(name=name,kind=kind,status=status,attempts=att,started_at=TS,finished_at=TS if status=="SUCCEEDED" else None)
wf_await=M.WorkflowState(workflow_id="wf_demo",profile_id=profile.profile_id,status="AWAITING_USER",current_stage="confirm_skills",mode="mock",created_at=TS,updated_at=TS,
  stages=[st("extract_skills","llm","SUCCEEDED"),M.StageState(name="confirm_skills",kind="human",status="AWAITING_USER"),M.StageState(name="match_roles",kind="deterministic",status="PENDING"),
          M.StageState(name="select_role",kind="human",status="PENDING"),M.StageState(name="learning_plan",kind="deterministic",status="PENDING"),M.StageState(name="employer_readiness",kind="llm",status="PENDING"),
          M.StageState(name="bias_audit",kind="llm",status="RUNNING",attempts=1,started_at=TS),M.StageState(name="compose_result",kind="deterministic",status="PENDING")])
wf_done=wf_await.model_copy(deep=True); wf_done.status="COMPLETED"; wf_done.current_stage=None; wf_done.selected_role_ids=["R-001"]
for s in wf_done.stages: s.status="SUCCEEDED"; s.attempts=max(1,s.attempts); s.started_at=TS; s.finished_at=TS
DISC=["Recommendations are decision support, not a guarantee of employment or a hiring decision.","Role requirements and scoring weights are provisional prototype data, not validated labour-market statistics.","Skills marked inferred are only used after you confirm them.","The fairness check covers specific synthetic test cases and cannot prove the absence of bias."]
results=M.WorkflowResults(workflow_id="wf_demo",skills=ext,recommendations=rec_models,learning_plans=[plan_m],employer_readiness=[ready],bias_audit=a_clean,disclaimers=DISC)
err=M.APIErrorResponse(error=M.APIError(code="VALIDATION_ERROR",message="work_entries[0].description exceeds 2500 characters",retryable=False,details={"field":"work_entries[0].description","max":2500},request_id="req_0001"))
out={"career_profile":profile,"skill_extraction_result":ext,"skill_confirmation_request":conf_req,"role_recommendations":rec_models,"learning_plan":plan_m,
     "employer_readiness_result":ready,"bias_audit_result_pass":a_clean,"bias_audit_result_canary_flagged":a_canary,"workflow_state_awaiting_confirmation":wf_await,
     "workflow_state_completed":wf_done,"workflow_results":results,"api_error":err}
for k,v in out.items():
    d=[x.model_dump() for x in v] if isinstance(v,list) else v.model_dump()
    (F/f"{k}.json").write_text(json.dumps(d,indent=1,ensure_ascii=False))
(F/"gold_user_levels.json").write_text(json.dumps(user,indent=1))
ww=dict(user_levels=user,prefs=prefs,ranking=[(r["rank"],r["role_id"],r["title"],r["score"],r["band"],r["feature_scores"],r["weights_used"],r["est_gap_hours"],r["blocking_gaps"]) for r in recs],
  plan=plan,audit_clean=[v.model_dump() for v in a_clean.variants],audit_canary=[v.model_dump() for v in a_canary.variants],canary_flags=[f.model_dump() for f in a_canary.flags])
(F/"_worked_examples.json").write_text(json.dumps(ww,indent=1,ensure_ascii=False))
print(json.dumps(ww["ranking"],indent=0)[:1500]); print(plan["total_est_hours"],plan["weeks_at_pace"],plan["unresolved_skill_ids"])
print("canary flags:",len(a_canary.flags))
