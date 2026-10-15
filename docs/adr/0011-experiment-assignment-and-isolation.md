# ADR 0011: stable assignment and paired offline experiment simulation

Accepted for Phase 7 local demonstration.

Persist immutable baseline/candidate definitions, SHA-256 subject buckets and
chosen variants. Evaluate both configurations on the same eligible fixtures;
use allocation to select simulated served outcomes. Label AB/shadow/canary as
offline simulations, never production traffic or statistical significance.

Use disposable PostgreSQL schemas with no public business-table fallback and
reset state per case. Public evidence stores bounded snapshots. Shadow refuses
approval/execution even within its temporary schema; positive action cases are
excluded from both shadow arms. Hash normal business state before/after runs;
no raw personal content enters comparison reports. One owned local slot prevents
competing experiments/evaluations. No cloud or external action adapters are added.
