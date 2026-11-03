import json, yaml, pathlib
from mock_api.app import app
from contracts import models as M
out = pathlib.Path("contracts"); (out/"schemas").mkdir(exist_ok=True)
spec = app.openapi(); (out/"openapi.json").write_text(json.dumps(spec, indent=1)); (out/"openapi.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))
names = ["CareerProfile","SkillEvidence","NormalizedSkill","SkillExtractionResult","RoleProfile","RoleRecommendation","SkillGap","LearningResource","LearningPlan","EmployerReadinessResult","BiasAuditResult","WorkflowState","WorkflowResults","APIError","APIErrorResponse"]
for n in names: (out/"schemas"/f"{n}.schema.json").write_text(json.dumps(getattr(M, n).model_json_schema(), indent=1))
print(len(spec["paths"]), "paths;", len(names), "schemas")
