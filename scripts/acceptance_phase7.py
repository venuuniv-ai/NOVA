"""Run/verify NOVA's local deterministic evaluation and offline experiment simulations."""

import argparse
import hashlib
import json
import time
import urllib.request
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--verify-run")
    parser.add_argument("--experiments", default="")
    args = parser.parse_args()

    def call(path, payload=None):
        request = urllib.request.Request(
            args.base_url + "/api/v1" + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    def wait(path, ready):
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            data = call(path)
            if ready(data):
                return data
            time.sleep(0.2)
        raise AssertionError("Evaluation did not complete within ten minutes")

    if args.verify_run:
        run_id = args.verify_run
        experiment_ids = args.experiments.split(",") if args.experiments else []
    else:
        payload = {"idempotency_key": str(uuid4()), "suite": "FULL"}
        started = call("/evaluation/runs", payload)
        run_id = started["id"]
        assert call("/evaluation/runs", payload)["id"] == run_id
        wait("/evaluation/runs/" + run_id, lambda r: r["status"] != "RUNNING")
        experiment_ids = []
        for mode in ["AB", "SHADOW", "CANARY"]:
            experiment = call(
                "/experiments",
                {
                    "idempotency_key": str(uuid4()),
                    "name": mode + " Phase 7 acceptance",
                    "mode": mode,
                    "candidate_percentage": 50 if mode == "AB" else 20,
                    "suite": "REGRESSION",
                },
            )
            eid = experiment["id"]
            experiment_ids.append(eid)
            intent = {"idempotency_key": "acceptance"}
            first = call("/experiments/" + eid + "/run", intent)
            assert call("/experiments/" + eid + "/run", intent)["id"] == first["id"]
            wait(
                "/experiments/" + eid,
                lambda e: bool(e["results"]) and e["results"][0]["status"] != "RUNNING",
            )
    run = call("/evaluation/runs/" + run_id)
    assert run["status"] == "DONE" and run["summary"]["evaluated"] >= 100
    assert run["summary"]["critical_violations"] == 0 and run["summary"]["gate_status"] == "PASS"
    assert len(run["scenarios"]) == run["summary"]["evaluated"]
    assert all(s["judge"] is None for s in run["scenarios"])
    assert all(m["value"] is None for m in run["metrics"] if m["denominator"] == 0)
    experiments = []
    for eid in experiment_ids:
        row = call("/experiments/" + eid)
        result = row["results"][0]
        assert result["status"] == "DONE"
        comparison = result["comparison"]
        assert (
            comparison["external_messages"] == 0
            and not comparison["authoritative_user_state_modified"]
        )
        assert comparison["critical_violations"] == 0
        assert (
            comparison["gate_status"] == "FAIL"
        )  # Deliberately cautious threshold loses labeled fixture utility.
        if row["definition"]["mode"] == "SHADOW":
            assert comparison["candidate_action_executions"] == 0
        reproduced = call(
            "/evaluation/compare",
            {"baseline_id": result["baseline_id"], "candidate_id": result["candidate_id"]},
        )
        assert all(comparison[key] == value for key, value in reproduced.items())
        assignments = json.dumps(row["assignments"], sort_keys=True).encode()
        experiments.append(
            {
                "id": eid,
                "mode": row["definition"]["mode"],
                "assignments": len(row["assignments"]),
                "assignment_sha256": hashlib.sha256(assignments).hexdigest(),
                "candidate_gate": comparison["gate_status"],
                "baseline_id": result["baseline_id"],
                "candidate_id": result["candidate_id"],
                "external_messages": comparison["external_messages"],
            }
        )
    print(
        json.dumps(
            {
                "result": "PASS",
                "run_id": run_id,
                "dataset": run["reproducibility"]["dataset"],
                "version": run["reproducibility"]["dataset_version"],
                "summary": run["summary"],
                "metrics": run["metrics"],
                "experiments": experiments,
                "real_judge": "REAL LLM JUDGE NOT CONFIGURED",
                "real_embedding": "REAL EMBEDDING MODEL NOT CONFIGURED",
                "required_external_spend_usd": 0,
                "scope": "LOCAL FIXTURE SYSTEM ONLY",
                "restart_verification": bool(args.verify_run),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
