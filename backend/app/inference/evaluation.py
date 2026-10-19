"""Separate fixture retrieval evaluation. No real model/judge silently activated."""

import json
import math
import time
from pathlib import Path

from app.evaluation.isolation import reset_scenario, scenario_database
from app.memory.contracts import MemoryInput, MemoryQuery
from app.memory.embeddings import FixtureEmbeddingProvider
from app.memory.service import MemoryService, digest


def evaluate(include_real=False):
    real_provider = None
    if include_real:
        from app.inference.providers import selected

        real_provider = selected("LOCAL_REAL", "EMBED")
    dataset = json.loads(Path(__file__).with_name("retrieval-v1.json").read_text())
    results = []
    with scenario_database() as schema:
        reset_scenario(schema)
        service = MemoryService(provider=FixtureEmbeddingProvider())
        ids = {}
        for row in dataset["corpus"]:
            memory = service.mutate(
                "create", row["id"], MemoryInput(**row["memory"], idempotency_key=row["id"])
            )
            ids[row["id"]] = memory["id"]
        comparisons = [
            (strategy, service, "FIXTURE_TOKEN_HASH_NOT_SEMANTIC_MODEL")
            for strategy in ["LEXICAL", "SEMANTIC", "HYBRID"]
        ]
        if real_provider:
            from app.database import SessionLocal
            from app.inference.service import eligible
            from app.security.identity import current_user_id

            real_service = MemoryService(provider=real_provider)
            with SessionLocal.begin() as session:
                for memory in session.scalars(eligible(current_user_id(), None)):
                    real_service.embedding(session, memory)
            comparisons += [
                (strategy, real_service, real_provider.model) for strategy in ["SEMANTIC", "HYBRID"]
            ]
        for strategy, retrieval_service, embedding_label in comparisons:
            samples = []
            for case in dataset["queries"]:
                start = time.perf_counter()
                hits = retrieval_service.search(
                    MemoryQuery(query=case["query"], retrieval_strategy=strategy, limit=5)
                ).hits
                relevant = {ids[x] for x in case["relevant"]}
                ranks = [i for i, h in enumerate(hits, 1) if str(h.memory_id) in relevant]
                dcg = sum(1 / math.log2(i + 1) for i in ranks)
                ideal = sum(1 / math.log2(i + 1) for i in range(1, min(5, len(relevant)) + 1))
                samples.append(
                    {
                        "case": case["id"],
                        "recall_at_5": len(ranks) / len(relevant) if relevant else None,
                        "mrr": 1 / min(ranks) if ranks else 0 if relevant else None,
                        "ndcg_at_5": dcg / ideal if ideal else None,
                        "latency_ms": (time.perf_counter() - start) * 1000,
                        "no_answer_expected": not relevant,
                        "returned": len(hits),
                        **(
                            {
                                "ranked_scores": [
                                    {
                                        "rank": i,
                                        "relevant": str(hit.memory_id) in relevant,
                                        "semantic_similarity": hit.semantic_similarity,
                                        "fused_score": hit.fused_score,
                                    }
                                    for i, hit in enumerate(hits, 1)
                                ]
                            }
                            if include_real
                            else {}
                        ),
                    }
                )
            results.append(
                {
                    "strategy": strategy,
                    "embedding": "NONE"
                    if strategy == "LEXICAL" and include_real
                    else embedding_label,
                    "samples": samples,
                    "positive_denominator": sum(bool(x["relevant"]) for x in dataset["queries"]),
                }
            )
    return {
        "dataset": dataset["version"],
        "digest": digest(dataset),
        "results": results,
        "real_embeddings": "EXECUTED" if include_real else "NOT_EXECUTED",
        "real_judge": "NOT_CONFIGURED",
        "gate": "PRIVACY/OWNERSHIP/DELETED/APPROVAL FAILURES ARE HARD FAILURES IN TESTS",
        "quality_threshold": "Recall@5 >=0.8 on positive cases before any real evaluation",
        "scope": "FIVE POSITIVE QUESTIONS; NO GENERAL QUALITY CLAIM"
        if include_real
        else "FIXTURE RETRIEVAL ONLY; NO GENERAL QUALITY CLAIM",
    }
