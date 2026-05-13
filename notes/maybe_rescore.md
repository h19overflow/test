# maybe_rescore

If there are no flagged criteria, it copies original scores to corrected scores
without an LLM call. If flagged criteria exist, it anonymizes candidates and asks
the LLM to re-score only the affected criteria.
