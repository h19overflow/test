# generate_rubric

Uses `BaseAgent[Rubric]` and `RUBRIC_PROMPT` to create exactly six weighted
criteria. It stores only `draft_rubric`, sets `stage = RUBRIC_GENERATED`, and logs
the LLM call without candidate names.
