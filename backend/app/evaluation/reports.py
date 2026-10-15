def markdown_report(run):
    lines = [
        "# NOVA fixture evaluation",
        f"Run: {run['id']}",
        f"Dataset: {run['reproducibility']['dataset']} {run['reproducibility']['dataset_version']}",
        f"Configuration: {run['configuration']} / {run['configuration_fingerprint']}",
        run["reproducibility"]["disclosure"],
        "",
        "| Metric | Value | Denominator | Methodology |",
        "| --- | --- | --- | --- |",
    ]
    for m in run["metrics"]:
        lines.append(f"| {m['name']} | {m['value']} | {m['denominator']} | {m['methodology']} |")
    lines += ["", "## Gates"] + [
        f"- {g['name']}: {g['status']} ({g['observed']}; threshold {g['threshold']})"
        for g in run["gates"]
    ]
    lines += ["", "## Failures"]
    for row in run["scenarios"]:
        for g in row["graders"]:
            if not g["passed"]:
                lines.append(
                    f"- {row['scenario_id']} / {g['name']} / {g['severity']}: {g['reason']}"
                )
    lines += [
        "",
        "## Limits",
        "Local fixture correctness only; real judge absent; compute unpriced.",
    ]
    return "\n".join(lines) + "\n"
