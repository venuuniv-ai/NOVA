"""Prepare the reviewed local source candidate; never stage, commit or include private state."""

import hashlib
import json
import re
import subprocess
import tarfile
from pathlib import Path

from nova_local import ROOT, source_files

EXTRAS = [
    "release/local-v1.0.json",
    "scripts/nova_local.py",
    "scripts/smoke_local_release.py",
    "scripts/test_local_release.py",
    "scripts/package_local_release.py",
    "scripts/start-local.sh",
    "scripts/stop-local.sh",
    "docs/local-release-guide.md",
    "docs/local-release-checklist.md",
    "docs/local-release-test-evidence.md",
]


def main():
    manifest = ROOT / "docs/phase-11-staging-manifest.md"
    phase11 = [name for _, name in re.findall(r"^([MA]) (\S+)$", manifest.read_text(), re.M)]
    candidates = set(phase11 + EXTRAS)
    status = (
        subprocess.check_output(
            ["git", "status", "--porcelain=v1", "--untracked-files=all", "-z"], cwd=ROOT
        )
        .decode()
        .split("\0")
    )
    actual = {line[3:] for line in status if line}
    if actual - candidates:
        raise RuntimeError("UNREVIEWED_CANDIDATES: " + ", ".join(sorted(actual - candidates)))
    descriptor = {
        "version": "1.0.0-local-rc1",
        "base_commit": "80dc41af8d3742fdb700b02e342f579e06389fcf",
        "release_scope": "Authenticated local workflows; deterministic fixture AI by default",
        "real_inference": "DISABLED; fresh bounded approval required",
        "external_actions": "DISABLED",
        "deadline": "2026-10-21 America/New_York",
        "source_sha256": source_files(),
    }
    target = ROOT / "release/local-v1.0.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(descriptor, indent=2) + "\n")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    paths = sorted(set(name for name in tracked if name) | candidates)
    out = ROOT / ".local/release-v1"
    out.mkdir(parents=True, exist_ok=True)
    archive = out / "nova-v1.0-local-rc1.tar.gz"
    forbidden = {".local", ".secrets", ".git", "node_modules", ".next", "test-results", ".venv"}
    hashes = {}
    with tarfile.open(archive, "w:gz") as tar:
        for name in paths:
            path = ROOT / name
            if forbidden.intersection(Path(name).parts) or path.is_symlink() or not path.is_file():
                raise RuntimeError("PROTECTED_OR_UNEXPECTED_ARCHIVE_PATH: " + name)
            if path.suffix in {".gguf", ".safetensors", ".db", ".sqlite", ".key", ".pem", ".log"}:
                raise RuntimeError("PROTECTED_ARTIFACT: " + name)
            data = path.read_bytes()
            if re.search(
                rb"(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", data
            ) or re.search(
                rb"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}", data
            ):
                raise RuntimeError("CREDENTIAL_SHAPE: " + name)
            hashes[name] = hashlib.sha256(data).hexdigest()
            info = tar.gettarinfo(str(path), arcname="nova-v1.0-local-rc1/" + name)
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            with path.open("rb") as stream:
                tar.addfile(info, stream)
    # Read back every member without extracting or executing it.
    with tarfile.open(archive, "r:gz") as tar:
        checked = {
            member.name.split("/", 1)[1]: hashlib.sha256(tar.extractfile(member).read()).hexdigest()
            for member in tar.getmembers()
        }
    assert checked == hashes
    result = {
        "archive": str(archive.relative_to(ROOT)),
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "files": len(hashes),
        "round_trip_hashes_verified": True,
        "private_state_included": False,
    }
    (out / "package.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
