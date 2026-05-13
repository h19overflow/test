from __future__ import annotations

import json
from uuid import uuid4

from langgraph.types import Command

from risk_auditor.graph import compile_graph


def main() -> None:
    graph = compile_graph()
    config = {"configurable": {"thread_id": str(uuid4())}}
    state = {"job_description_path": "data/job_description.json", "candidates_path": "data/candidates.json"}
    result = graph.invoke(state, config=config)
    while "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        print(json.dumps(payload, indent=2))
        action = input("approve/edit/regenerate: ").strip()
        edited = None
        if action == "edit":
            edited = json.loads(input("edited rubric JSON: "))
        result = graph.invoke(Command(resume={"action": action, "edited_rubric": edited}), config=config)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
