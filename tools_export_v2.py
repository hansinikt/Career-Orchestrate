"""Regenerates contracts/v2/openapi.json|yaml and schemas/*.schema.json from the code. Run: make contracts"""
import os, json, pathlib, sys, yaml
os.environ.setdefault("DB_PATH", "/tmp/co_export.db"); ROOT = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT))
from backend.app.main import app
from contracts.v2 import models as M
out = ROOT / "contracts" / "v2"; (out / "schemas").mkdir(exist_ok=True)
spec = app.openapi(); (out / "openapi.json").write_text(json.dumps(spec, indent=2, sort_keys=True)); (out / "openapi.yaml").write_text(yaml.safe_dump(spec, sort_keys=True, allow_unicode=True))
n = 0
for name in dir(M):
    o = getattr(M, name)
    if isinstance(o, type) and issubclass(o, M.BaseModel) and o not in (M.BaseModel, M.S):
        (out / "schemas" / f"{name}.schema.json").write_text(json.dumps(o.model_json_schema(), indent=2, sort_keys=True)); n += 1
print("paths", len(spec["paths"]), "operations", sum(len(v) for v in spec["paths"].values()), "schemas", n)
