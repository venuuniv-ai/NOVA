# ADR 0010: repository golden scenarios and deterministic grading

Accepted for Phase 7 local fixture evaluation.

Use typed, versioned repository JSON with 104 scenario-specific cases. The server
loads expectations; API clients cannot submit graders, expected results, code,
SQL or paths. Reusing a dataset version with changed bytes is refused. Actual
service flows run in temporary schemas and persist normalized evidence/checks.

Define task success by each scenario's checks. Named metrics use explicit
applicable denominators; no zero-denominator perfect score, NaN or invented cost.
Measure fixture elapsed time separately from real model latency. Memory metrics
exercise actual MemoryService/pgvector, never claim semantic quality. Real vision
quality and real-user usefulness are outside the fixture labels.

Keep source/dataset/configuration fingerprints and fixture/grader versions.
See [architecture](../phase-7-architecture.md).
