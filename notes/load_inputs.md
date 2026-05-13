# load_inputs

Reads `data/job_description.json` and `data/candidates.json`, validates required
keys and unique candidate IDs, then sets `stage = INIT`. It does not call the LLM
or write generated artifacts.
