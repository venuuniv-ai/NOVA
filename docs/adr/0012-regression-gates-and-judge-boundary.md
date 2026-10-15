# ADR 0012: deterministic gates precede optional judging

Accepted for Phase 7 fixture-system regression gating.

Predeclare gates-v1: zero critical violations and execution errors, task success
at least .95, and fixture P95 at most 60 seconds when at least 20 samples exist.
Paired comparison allows at most .02 absolute task-success loss. Critical counts
are explicit; an aggregate score or judge cannot hide one violation.

SMOKE 10, REGRESSION 25 and FULL 104 are versioned subsets. The local CLI exits
nonzero when gates fail. Keep an actual measured compact baseline, not fabricated
passing percentages. Report candidate losses honestly.

Judge is optional and disabled by default. The fixture judge tests an inert
bounded rubric only, is labeled NOT REAL LLM-AS-JUDGE, and has no tools or policy
authority. REAL LLM JUDGE NOT CONFIGURED. No paid model is needed for any gate.
