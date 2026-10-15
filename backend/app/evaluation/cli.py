import argparse
import json
from pathlib import Path
from uuid import uuid4

from app.evaluation.contracts import RunInput
from app.evaluation.reports import markdown_report
from app.evaluation.runner import EvaluationRunner


def exit_code(run):
    return 0 if run["status"] == "DONE" and run["summary"].get("gate_status") == "PASS" else 1


def main():
    parser = argparse.ArgumentParser(description="Local fixture evaluation; no model traffic")
    parser.add_argument("--suite", choices=["SMOKE", "REGRESSION", "FULL"], default="REGRESSION")
    parser.add_argument(
        "--configuration", choices=["BASELINE", "CAUTIOUS_THRESHOLD"], default="BASELINE"
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run = EvaluationRunner().run(
        RunInput(idempotency_key=str(uuid4()), suite=args.suite, configuration=args.configuration)
    )
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "report.json").write_text(json.dumps(run, indent=2) + "\n")
        (args.output / "report.md").write_text(markdown_report(run))
    print(json.dumps({"id": run["id"], "status": run["status"], "summary": run["summary"]}))
    raise SystemExit(exit_code(run))


if __name__ == "__main__":
    main()
