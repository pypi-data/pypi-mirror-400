import json
from pathlib import Path


def write_json_plan(plan, path=None):
    data = {"actions": plan.serialize()}
    output = json.dumps(data, indent=2)

    if path:
        Path(path).write_text(output)
    else:
        print(output)
