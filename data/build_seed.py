"""Builds seed data JSON. ALL DATA HERE IS SYNTHETIC / TEAM-DRAFTED SEED, provenance flagged. Must be reviewed by D3 (see PRD s22)."""
import json, pathlib
D = pathlib.Path(__file__).parent
S = lambda i,n,cat,al,h,pre=(): dict(skill_id=i,name=n,category=cat,aliases=al,hours_per_level=h,prerequisites=list(pre),onet_ref=None,esco_ref=None)
skills = [
 S("SK-SPREADSHEET","Spreadsheet analysis","data",["excel","pivot table","pivot tables","vlookup","google sheets","spreadsheet"],15),
 S("SK-REPORT","Report preparation","data",["mis report","monthly report","weekly report","management report","reports"],10),
 S("SK-DATAQUALITY","Data validation and quality checks","data",["data cleaning","reconcile","reconciliation","cross-check","validate data"],15),
 S("SK-BI","Dashboarding and BI tools","data",["power bi","tableau","sap analytics cloud","dashboard","dashboards"],25,["SK-SPREADSHEET"]),
 S("SK-SQL","Basic SQL querying","data",["sql","database query","queries"],25,["SK-SPREADSHEET"]),
 S("SK-SCHEDULING","Scheduling and calendar coordination","operations",["schedule","calendar","rota","appointments","itinerary"],10),
 S("SK-TEAMCOORD","Team and task coordination","operations",["coordinate team","task allocation","follow up","follow-up","delegation"],15),
 S("SK-PROCESSDOC","Process documentation","operations",["sop","standard operating procedure","process notes","checklist"],12),
 S("SK-PROCESSIMPROVE","Process improvement","operations",["streamline","automate manual","reduce errors","improve workflow"],20,["SK-PROCESSDOC"]),
 S("SK-STAKEHOLDER","Stakeholder communication","communication",["liaise","coordinate with departments","client communication","point of contact"],12),
 S("SK-BUSWRITING","Business writing","communication",["email drafting","correspondence","letters","drafting"],10),
 S("SK-MINUTES","Meeting coordination and minutes","communication",["minutes of meeting","mom","meeting notes","agenda"],8),
 S("SK-VENDOR","Vendor coordination","operations",["vendor","suppliers","vendor follow-up","service providers"],15),
 S("SK-PROCUREMENT","Procurement basics","operations",["purchase order","purchase requisition","quotation","rfq"],20,["SK-VENDOR"]),
 S("SK-BUDGET","Budget and expense tracking","finance",["expense tracking","budget","petty cash","expense reports"],15),
 S("SK-RECORDS","Records management","operations",["filing","document control","record keeping","records","archive"],10),
 S("SK-HRADMIN","HR policy and administration","people",["attendance","leave records","onboarding paperwork","hr policy"],20),
 S("SK-HRIS","HR information system usage","people",["successfactors","hris","hr software"],20,["SK-HRADMIN"]),
 S("SK-CONFIDENTIALITY","Confidentiality and privacy handling","people",["confidential","sensitive information","data privacy"],8),
 S("SK-PROJECTPLAN","Project planning","operations",["project plan","timeline","milestones","gantt"],20,["SK-SCHEDULING"]),
 S("SK-RISK","Risk and issue tracking","operations",["risk log","issue log","escalation"],10),
 S("SK-ERPBASIC","ERP transaction basics","data",["sap","erp","erp data entry","s/4hana"],20),
 S("SK-MASTERDATA","Master data management","data",["master data","vendor master","material master","data maintenance"],20,["SK-ERPBASIC","SK-DATAQUALITY"]),
]
R = lambda s,i,l,m: dict(skill_id=s,importance=i,required_level=l,mandatory=m)
roles = [
 dict(role_id="R-001",title="Reporting Analyst (MIS)",summary="Prepares recurring management reports and dashboards from operational data.",tags=["data","reporting"],
  requirements=[R("SK-SPREADSHEET",5,3,True),R("SK-REPORT",5,3,True),R("SK-DATAQUALITY",4,2,True),R("SK-BI",4,2,False),R("SK-SQL",3,1,False),R("SK-STAKEHOLDER",2,2,False),R("SK-BUSWRITING",2,2,False)],
  requires_degree=None,max_experience_years=None,proof_templates=["Rebuild one of your monthly reports as a dashboard and document the data checks you apply"]),
 dict(role_id="R-002",title="Operations Coordinator",summary="Keeps day-to-day operations on schedule across teams and vendors.",tags=["operations","people"],
  requirements=[R("SK-SCHEDULING",4,3,True),R("SK-TEAMCOORD",5,2,True),R("SK-PROCESSDOC",4,2,False),R("SK-VENDOR",3,2,False),R("SK-STAKEHOLDER",4,2,True),R("SK-REPORT",3,2,False),R("SK-PROCESSIMPROVE",4,2,False),R("SK-BUDGET",2,1,False)],
  requires_degree=None,max_experience_years=None,proof_templates=["Document one workflow end-to-end and propose two measurable improvements"]),
 dict(role_id="R-003",title="HR Operations Coordinator",summary="Runs HR administration, records and employee queries.",tags=["people","hr"],
  requirements=[R("SK-RECORDS",5,3,True),R("SK-HRADMIN",5,2,True),R("SK-HRIS",4,2,False),R("SK-STAKEHOLDER",3,2,False),R("SK-SCHEDULING",3,2,False),R("SK-CONFIDENTIALITY",3,2,False),R("SK-DATAQUALITY",3,2,False)],
  requires_degree=True,max_experience_years=None,proof_templates=["Prepare an anonymised onboarding checklist and leave-record audit"]),
 dict(role_id="R-004",title="Project Coordinator",summary="Supports project delivery: plans, schedules, minutes, status reports.",tags=["operations","planning"],
  requirements=[R("SK-PROJECTPLAN",5,2,True),R("SK-SCHEDULING",4,3,False),R("SK-TEAMCOORD",5,2,True),R("SK-MINUTES",3,2,False),R("SK-STAKEHOLDER",4,2,True),R("SK-REPORT",3,2,False),R("SK-BUDGET",3,2,False),R("SK-RISK",3,1,False)],
  requires_degree=None,max_experience_years=None,proof_templates=["Create a project plan, risk log and status report for a small real task"]),
 dict(role_id="R-005",title="Procurement and Vendor Coordinator",summary="Coordinates purchase requests, quotations and vendor follow-up.",tags=["operations","vendors"],
  requirements=[R("SK-VENDOR",5,3,True),R("SK-PROCUREMENT",5,2,True),R("SK-BUDGET",4,2,False),R("SK-RECORDS",3,2,False),R("SK-SPREADSHEET",3,2,False),R("SK-ERPBASIC",3,2,False)],
  requires_degree=None,max_experience_years=8,proof_templates=["Build a vendor comparison sheet from three quotations with a recommendation note"]),
 dict(role_id="R-006",title="ERP Master Data Associate",summary="Maintains accurate master data records in an ERP system.",tags=["data","erp"],
  requirements=[R("SK-ERPBASIC",5,2,True),R("SK-DATAQUALITY",5,3,True),R("SK-RECORDS",4,2,False),R("SK-SPREADSHEET",3,2,False),R("SK-MASTERDATA",4,2,False),R("SK-PROCESSDOC",2,1,False)],
  requires_degree=None,max_experience_years=None,proof_templates=["Clean a sample vendor list: duplicates, missing fields, naming rules; report error rate before/after"]),
]
for r in roles:
    r.update(onet_soc=None,provenance="team_curated_unverified",market_signals=[])
RS = lambda i,t,sk,f,to,cost="unknown": dict(resource_id=i,title=t,provider="SAP Learning Hub (student edition)",url=None,skill_ids=sk,level_from=f,level_to=to,est_hours=None,cost=cost,verification_status="seed_unverified",last_verified=None)
resources = [
 RS("RES-001","Exploring SAP Analytics Cloud",["SK-BI"],0,1),
 RS("RES-002","SAP Analytics Cloud: Story Design",["SK-BI"],1,2),
 RS("RES-003","Applying AI-powered Visualizations and Augmented Analytics to Business Data in SAP Analytics Cloud",["SK-BI"],1,2),
]
(D/"skills.json").write_text(json.dumps(dict(taxonomy_version="seed-0.1",skills=skills),indent=1))
(D/"roles.json").write_text(json.dumps(dict(dataset_version="seed-0.1",roles=roles),indent=1))
(D/"resources.json").write_text(json.dumps(dict(catalog_version="seed-0.1",note="Titles taken from the SAP Hackfest participant handbook 'Learning Assets' slide. URLs/durations NOT captured yet: D3/D4 must capture while logged in, then set verification_status=verified.",resources=resources),indent=1))
print(len(skills),"skills",len(roles),"roles",len(resources),"resources")
