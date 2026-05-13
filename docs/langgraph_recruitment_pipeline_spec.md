# LangGraph Recruitment Pipeline Specification

## Purpose

Build a replayable LangGraph pipeline that evaluates candidates from `data/candidates.json` against `data/job_description.json`, preserves intermediate artifacts, requires human approval of the rubric, blocks ranking until bias audit completion, and applies anonymized re-scoring when flagged bias exists.

The pipeline is a staged workflow. It is not a one-shot report generator.

## Reference Basis

This spec uses the LangChain MCP documentation for:

- LangGraph `interrupt()` behavior.
- LangGraph `Command` routing and resume behavior.
- LangGraph checkpointers, thread IDs, and persistence.
- LangChain structured output with Pydantic schemas.

Key technical points from the docs:

- `interrupt(payload)` pauses a graph node and surfaces a JSON-serializable payload to the caller.
- Interrupts require a compiled graph with a checkpointer and a stable `thread_id`.
- The graph resumes with `Command(resume=value)`.
- The value passed to `Command(resume=...)` becomes the return value of `interrupt()` inside the paused node.
- The interrupted node restarts from the beginning when resumed, so side effects before `interrupt()` must be idempotent or avoided.
- `Command(update=..., goto=...)` is returned from node functions when state updates and dynamic routing must happen together.
- `Command(resume=...)` is the only `Command` pattern intended as input to `graph.invoke()` or `graph.stream()` after an interrupt.
- Do not combine a static edge and a dynamic `Command(goto=...)` from the same node, because both routes can execute.

## Required Imports

Core LangGraph imports:

```python
from typing import Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
```

Schema and state imports:

```python
from pydantic import BaseModel, Field, model_validator

from risk_auditor.schemas import BiasAudit, Rubric, ScoringBatch
from risk_auditor.stages import PipelineStage, assert_at_least
from risk_auditor.state import PipelineState
```

LLM imports, subject to package verification:

```python
from langchain_openrouter import ChatOpenRouter
```

If the OpenRouter package exposes a different import path, implement a small adapter in `src/risk_auditor/llm.py` and keep the rest of the graph independent from provider details.

## External Interfaces

Inputs:

- `data/job_description.json`
- `data/candidates.json`

Generated artifacts:

- `scoring_rubric.json`
- `candidate_scores.json`
- `bias_audit.json`
- `hiring_summaries.md`
- `llm_calls.jsonl`

Planned commands:

- Run pipeline: `python -m risk_auditor.run`
- Validate artifacts: `python validate.py`

## Pipeline State

State keys:

```python
class PipelineState(TypedDict, total=False):
    stage: str
    job_description_path: str
    candidates_path: str
    job_description: dict
    candidates: list[dict]
    draft_rubric: dict
    approved_rubric: dict
    original_scores: dict
    bias_audit: dict
    flagged_criteria: list[str]
    corrected_scores: dict
    final_ranking: list[dict]
    summaries_markdown: str
    artifacts: dict[str, str]
```

Rules:

- `stage` is the source of truth for ordering.
- Every node must verify its required prior stage before doing work.
- Artifacts must be written only by the node that owns that artifact.
- Ranking must never read from raw candidate input directly; it must read from original or corrected score artifacts.
- Original scores must be immutable after `score_candidates`.

## Graph Shape

```text
START
  -> load_inputs
  -> generate_rubric
  -> approve_rubric
  -> score_candidates
  -> audit_bias
  -> maybe_rescore
  -> finalise_ranking
  -> generate_summaries
  -> END
```

Routing rules:

- Use normal edges for the fixed path.
- Use `Command(goto=...)` only inside `approve_rubric`, because it may route back to `generate_rubric`.
- If `approve_rubric` returns `Command(goto=...)`, do not also add a normal outgoing edge from that node in the final implementation.
- `maybe_rescore` can stay as a normal node that no-ops when no flagged findings exist.

## Runtime and Checkpointing

Compilation:

```python
checkpointer = InMemorySaver()
compiled_graph = graph.compile(checkpointer=checkpointer)
```

Invocation:

```python
config = {"configurable": {"thread_id": run_id}}
result = compiled_graph.invoke(initial_state, config=config)
```

Resume after interrupt:

```python
resumed = compiled_graph.invoke(Command(resume=payload), config=config)
```

Technical requirements:

- `run_id` must be stable for the current pipeline run.
- The terminal runner must reuse the same `config` when resuming.
- The interrupt payload and resume payload must be JSON-serializable.
- Code before `interrupt()` must not write files or append LLM logs, because it will run again on resume.
- File writes should happen only after the resume payload is validated.
- For MVP, `InMemorySaver` is acceptable. For production or long-lived resumability, replace it with a persistent checkpointer.

## HITL Integration Map

Required HITL point:

- `approve_rubric`
  - Pauses after draft rubric generation.
  - Operator can approve, edit, or regenerate.
  - Candidate scoring is blocked until approval.

Optional future HITL points:

- `audit_bias`
  - Human reviewer can inspect audit findings before anonymized re-scoring.
- `finalise_ranking`
  - Human reviewer can confirm final ranking before summary generation.

MVP rule:

- Only `approve_rubric` is mandatory.
- Optional HITL points must not weaken the required automated ordering checks.

## Stage 1: `load_inputs`

Purpose:

- Load job and candidate fixtures from disk.

Inputs:

- `job_description_path`
- `candidates_path`

Outputs:

- `job_description`
- `candidates`
- `stage = INIT`

Technical requirements:

- Parse both files as JSON.
- Validate that the job description contains `role`, `company`, `requirements`, `nice_to_have`, and `explicitly_not_required`.
- Validate that each candidate contains `id`, `name`, and `summary`.
- Candidate IDs must be unique.
- Do not depend on candidate order, candidate names, or sample fixture text.
- Do not call the LLM in this stage.
- Do not write generated artifacts in this stage.

## Stage 2: `generate_rubric`

Purpose:

- Make the Stage 1 LLM call that creates a job-specific rubric.

Required prior state:

- `stage = INIT`
- `job_description` loaded

LLM input:

- Full job description.
- Explicit instruction that `explicitly_not_required` items must not become positive scoring factors.

Structured output:

```python
class Criterion(BaseModel):
    name: str
    weight: float = Field(gt=0)
    scale: Literal["0-10"] = "0-10"
    ten_point_description: str

class Rubric(BaseModel):
    criteria: list[Criterion] = Field(min_length=6, max_length=6)
```

Technical requirements:

- Use the OpenRouter chat model through a local model factory.
- Bind the response to `Rubric` using `with_structured_output(Rubric)` or the closest supported structured-output strategy.
- Reject output unless exactly 6 criteria are returned.
- Reject output unless weights sum to `1.0` within tolerance `0.01`.
- Reject generic criteria that are not grounded in the job description.
- Store the generated rubric only as `draft_rubric`.
- Do not write `scoring_rubric.json` yet.
- Append one LLM call record to `llm_calls.jsonl`.

LLM log values:

- `stage = "RUBRIC_GENERATED"`
- `input_artifacts = ["data/job_description.json"]`
- `output_artifact = "state.draft_rubric"`
- `candidate_names_included = false`

Output state:

- `draft_rubric`
- `stage = RUBRIC_GENERATED`

## Stage 3: `approve_rubric` HITL Checkpoint

Purpose:

- Stop execution until the operator approves, edits, or rejects the generated rubric.

Required prior state:

- `stage = RUBRIC_GENERATED`
- `draft_rubric` exists

Command imports:

```python
from typing import Literal

from langgraph.types import Command, interrupt
```

Node return type:

```python
def approve_rubric(
    state: PipelineState,
) -> Command[Literal["generate_rubric", "score_candidates"]]:
    ...
```

Interrupt trigger:

```python
decision = interrupt({
    "checkpoint": "rubric_approval",
    "question": "Approve, edit, or regenerate the rubric?",
    "draft_rubric": state["draft_rubric"],
    "allowed_actions": ["approve", "edit", "regenerate"],
    "resume_schema": {
        "action": "approve | edit | regenerate",
        "edited_rubric": "required only when action is edit"
    }
})
```

Resume payload:

```json
{
  "action": "approve",
  "edited_rubric": null
}
```

or:

```json
{
  "action": "edit",
  "edited_rubric": {
    "criteria": []
  }
}
```

or:

```json
{
  "action": "regenerate",
  "edited_rubric": null
}
```

Interrupt handling rules:

- The terminal runner must detect `__interrupt__` in the graph result.
- The terminal runner must print the draft rubric in a readable form.
- The terminal runner must collect exactly one of:
  - approve unchanged
  - edit rubric JSON
  - regenerate
- The terminal runner must resume with `graph.invoke(Command(resume=payload), config=config)`.
- The same `thread_id` must be used for initial invocation and resume.
- The resume payload must be validated before it is used.
- If `action = approve`, validate `draft_rubric`, write it to `scoring_rubric.json`, and route to `score_candidates`.
- If `action = edit`, validate `edited_rubric`, write it to `scoring_rubric.json`, and route to `score_candidates`.
- If `action = regenerate`, do not write `scoring_rubric.json`; route back to `generate_rubric`.
- If payload is invalid, raise a validation error and do not advance the stage.

Command routing rules:

- Use `Command(update=..., goto="score_candidates")` after approve or edit.
- Use `Command(update=..., goto="generate_rubric")` after regenerate.
- Do not pass `Command(update=...)` into `graph.invoke()` from the terminal runner.
- Only use `Command(resume=payload)` as the external resume command.
- Do not add a static edge from `approve_rubric` to `score_candidates` in the final graph if `Command(goto=...)` handles routing.

Side-effect rules:

- Do not write files before calling `interrupt()`.
- Do not append to `llm_calls.jsonl` in this node unless a future LLM call is added.
- Write `scoring_rubric.json` only after a valid approve or edit action.
- Candidate scoring must fail if `scoring_rubric.json` does not exist.

Output state on approve/edit:

- `approved_rubric`
- `artifacts.scoring_rubric = "scoring_rubric.json"`
- `stage = RUBRIC_APPROVED`

Output state on regenerate:

- `stage = INIT` or `stage = RUBRIC_GENERATED_REJECTED`
- route target `generate_rubric`

MVP decision:

- Prefer `stage = INIT` on regenerate to reuse the existing `generate_rubric` precondition without adding another enum value.

## Stage 4: `score_candidates`

Purpose:

- Make the Stage 2 LLM call that scores all candidates using the approved rubric.

Required prior state:

- `stage = RUBRIC_APPROVED`
- `approved_rubric` exists
- `scoring_rubric.json` exists

LLM input:

- Job description.
- Approved rubric.
- All candidates, including names.

Structured output:

```python
class CriterionScore(BaseModel):
    criterion_name: str
    score: float = Field(ge=0, le=10)
    rationale: str

class CandidateScore(BaseModel):
    candidate_id: str
    scores: list[CriterionScore]
    total_weighted_score: float

class ScoringBatch(BaseModel):
    candidate_scores: list[CandidateScore]
```

Technical requirements:

- Use a separate LLM call from rubric generation.
- Every candidate from `data/candidates.json` must appear exactly once.
- Every criterion from `approved_rubric` must appear exactly once for each candidate.
- Recompute `total_weighted_score` in code after the LLM returns scores.
- Store LLM rationales, but trust code-calculated totals.
- Preserve output under `original_scores`.
- Write `candidate_scores.json` with `original_scores`, `bias_audit_status = "not_started"`, and empty `final_ranking`.
- Do not create ranking in this stage.

LLM log values:

- `stage = "CANDIDATES_SCORED"`
- `input_artifacts = ["data/job_description.json", "data/candidates.json", "scoring_rubric.json"]`
- `output_artifact = "candidate_scores.json"`
- `candidate_names_included = true`

Output state:

- `original_scores`
- `stage = CANDIDATES_SCORED`

## Stage 5: `audit_bias`

Purpose:

- Make the mandatory Stage 3 LLM call that audits scores before any ranking exists.

Required prior state:

- `stage = CANDIDATES_SCORED`
- `original_scores` exists
- `candidate_scores.json` exists
- `final_ranking` is empty

LLM input must include:

- Candidate names.
- Candidate summaries.
- Approved rubric.
- Original Stage 2 scoring results.

Structured output:

```python
class BiasFinding(BaseModel):
    bias_type: str
    affected_candidates: list[str]
    affected_criteria: list[str]
    evidence: str
    severity: Literal["flagged", "watch", "clear"]

class BiasAudit(BaseModel):
    findings: list[BiasFinding]
    audit_complete: bool = True
```

Technical requirements:

- Use a separate LLM call from rubric generation and candidate scoring.
- Audit for name or nationality signals, credential prestige, employer prestige, geography, startup vs corporate context, and criteria that appear correlated with demographic signals.
- Save the complete audit to `bias_audit.json`.
- Update `candidate_scores.json` with `bias_audit_status = "completed"`.
- Extract `flagged_criteria` from findings with `severity = "flagged"`.
- Do not create ranking in this stage.

LLM log values:

- `stage = "BIAS_AUDITED"`
- `input_artifacts = ["data/candidates.json", "scoring_rubric.json", "candidate_scores.json"]`
- `output_artifact = "bias_audit.json"`
- `candidate_names_included = true`

Output state:

- `bias_audit`
- `flagged_criteria`
- `stage = BIAS_AUDITED`

## Stage 6: `maybe_rescore`

Purpose:

- Apply required de-biasing logic after the audit.

Required prior state:

- `stage = BIAS_AUDITED`
- `bias_audit.audit_complete = true`

No flagged findings:

- Set `corrected_scores = original_scores`.
- Set `scores_changed = false`.
- Do not make a re-scoring LLM call.
- Continue to ranking.

Flagged findings:

- Collect all affected criteria from flagged findings.
- Anonymize candidates in code before the re-scoring prompt is built.
- Remove `name`.
- Preserve `id`.
- Remove demographic or prestige signals that are unrelated to job requirements where practical.
- Re-score only affected criteria.
- Merge corrected criterion scores into a copy of original scores.
- Preserve `original_scores` unchanged.

Anonymized re-scoring input rules:

- Candidate names must not appear in the prompt.
- The `candidate_names_included` log value must be `false`.
- The prompt must state that only `flagged_criteria` may be re-scored.
- The prompt must include approved rubric criteria only for flagged criteria.

Technical requirements:

- If the LLM returns scores for unflagged criteria, ignore those values.
- Recompute corrected totals in code.
- Set `scores_changed = true` only if any corrected score differs from the original.
- Update `candidate_scores.json` with `corrected_scores`, `flagged_criteria`, and `scores_changed`.

LLM log values if re-scoring occurs:

- `stage = "FLAGGED_RESCORING_COMPLETE"`
- `input_artifacts = ["bias_audit.json", "candidate_scores.json", "scoring_rubric.json"]`
- `output_artifact = "candidate_scores.json"`
- `candidate_names_included = false`

Output state:

- `corrected_scores`
- `stage = FLAGGED_RESCORING_COMPLETE` if re-scoring happened
- otherwise keep `stage = BIAS_AUDITED`

## Stage 7: `finalise_ranking`

Purpose:

- Produce the final ranked candidate list after bias audit and required re-scoring.

Required prior state:

- `stage >= BIAS_AUDITED`
- If flagged criteria exist, `stage = FLAGGED_RESCORING_COMPLETE`

Hard guard:

```python
assert_at_least(PipelineStage(state["stage"]), PipelineStage.BIAS_AUDITED)
```

Additional guard:

```python
if state["flagged_criteria"]:
    assert state["stage"] == PipelineStage.FLAGGED_RESCORING_COMPLETE
```

Technical requirements:

- Ranking must fail before `BIAS_AUDITED`.
- Ranking must fail if flagged findings exist but corrected scores are missing.
- Use `corrected_scores` when available.
- Use `original_scores` only when no flagged re-scoring is required.
- Sort by final weighted total descending.
- Write ranking to `candidate_scores.json`.
- Include a clear `ranking_source` value: `original_scores` or `corrected_scores`.

Output state:

- `final_ranking`
- `stage = RANKING_FINALISED`

## Stage 8: `generate_summaries`

Purpose:

- Generate hiring committee-ready summaries for the top 3 candidates.

Required prior state:

- `stage = RANKING_FINALISED`
- `final_ranking` exists

LLM input:

- Job description.
- Approved rubric.
- Final ranking.
- Final score source.
- Top 3 candidate summaries.
- Bias audit summary.

Output file:

- `hiring_summaries.md`

Required content:

- Top 3 candidate summaries.
- Strengths mapped to job description requirements.
- Gaps with criticality.
- Three interview focus areas per candidate.
- Hire confidence: `Strong Yes`, `Yes`, `Maybe`, or `No`.
- One-sentence confidence justification.
- Five structured interview questions for the rank 1 candidate.
- One-paragraph cohort analysis.
- Optional counter-intuitive pick for lowest-ranked candidate.
- Optional blind re-ranking comparison.

Technical requirements:

- Use a separate LLM call from scoring and audit.
- Do not change candidate scores.
- Do not change ranking.
- Save Markdown only after successful generation.

LLM log values:

- `stage = "SUMMARIES_GENERATED"`
- `input_artifacts = ["data/job_description.json", "data/candidates.json", "candidate_scores.json", "bias_audit.json"]`
- `output_artifact = "hiring_summaries.md"`
- `candidate_names_included = true`

Output state:

- `summaries_markdown`
- `stage = SUMMARIES_GENERATED`

## Artifact Requirements

`candidate_scores.json` must preserve:

- `approved_rubric_reference`
- `original_scores`
- `bias_audit_status`
- `flagged_criteria`
- `corrected_scores`
- `scores_changed`
- `ranking_source`
- `final_ranking`

Shape:

```json
{
  "approved_rubric_reference": "scoring_rubric.json",
  "original_scores": [],
  "bias_audit_status": "completed",
  "flagged_criteria": [],
  "corrected_scores": [],
  "scores_changed": false,
  "ranking_source": "original_scores",
  "final_ranking": []
}
```

`llm_calls.jsonl` record shape:

```json
{
  "stage": "string",
  "timestamp": "ISO-8601 timestamp",
  "model": "string",
  "provider": "openrouter",
  "prompt_hash": "sha256...",
  "input_artifacts": ["path"],
  "output_artifact": "path",
  "candidate_names_included": true
}
```

## Validation Requirements

`python validate.py` must check:

- Required artifacts exist.
- JSON artifacts parse.
- Rubric has exactly 6 criteria.
- Rubric weights sum to `1.0`.
- Candidate IDs are unique.
- All candidates are scored exactly once.
- All rubric criteria are scored for each candidate.
- `candidate_scores.json` references `scoring_rubric.json`.
- `original_scores` exists and remains separate from `corrected_scores`.
- `bias_audit.json` exists before `final_ranking` is non-empty.
- `bias_audit_status = "completed"` before ranking.
- Calling ranking with a pre-audit state raises an error.
- If any finding has `severity = "flagged"`, then:
  - `flagged_criteria` is non-empty.
  - corrected scores exist.
  - anonymized re-scoring log exists.
  - anonymized re-scoring log has `candidate_names_included = false`.
- `llm_calls.jsonl` has separate records for required LLM stages.
- No anonymized re-scoring prompt artifact contains candidate names, if prompt artifacts are stored.

## Implementation Order

1. Confirm the OpenRouter import path and model factory.
2. Implement file IO and schema validation.
3. Implement graph compilation with `InMemorySaver`.
4. Implement `generate_rubric`.
5. Implement `approve_rubric` with `interrupt()` and `Command`.
6. Implement terminal runner detection for `__interrupt__`.
7. Implement candidate scoring.
8. Implement bias audit.
9. Implement anonymized re-scoring.
10. Implement ranking guard and final ranking.
11. Implement summaries.
12. Implement validation.

## Assumptions

- "Langchain-mcp" means the LangChain documentation MCP server currently available in the environment.
- Stage Two command and interrupt requirements refer to the human rubric approval checkpoint, which is the required HITL point.
- `InMemorySaver` is acceptable for the MVP because the evaluator will run the pipeline in one local process.
- Persistent checkpointing can be added later without changing the stage contract.
- Candidate names are allowed in initial scoring and bias audit, but not in anonymized re-scoring.
- Candidate IDs are not treated as demographic signals and may remain in anonymized prompts.

## Clarification Needed

- Confirm whether "Stage Two" should mean `generate_rubric` or the HITL `approve_rubric` checkpoint. This spec treats the HITL checkpoint as the stage needing command/import/interrupt detail.
- Confirm the exact OpenRouter package import path expected by your environment for `ChatOpenRouter`.
- Confirm whether edited rubrics should be entered as raw JSON in the terminal or through a simpler guided edit flow.
- Confirm whether prompt text should be persisted as artifacts for validation, or whether `prompt_hash` in `llm_calls.jsonl` is enough.
- Confirm whether a durable checkpointer is required for evaluation, or whether in-memory checkpointing is acceptable for the MVP.
