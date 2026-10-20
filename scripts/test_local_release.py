"""Local release lifecycle guards. No Docker, models or external services."""

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import nova_local as n


class ReleaseTests(unittest.TestCase):
    def config(self):
        return {
            "volumes": {"data": {"name": "nova-v1-local_data"}},
            "networks": {
                name: {"internal": True}
                for name in ["application", "state", "telemetry", "identity"]
            },
            "services": {
                "backend": {
                    "environment": {"OWNED_DRAFT_MODE": "FIXTURE"},
                    "volumes": [
                        {"type": "bind", "source": str(n.ROOT / "backend/app"), "read_only": True}
                    ],
                }
            },
        }

    def test_release_config_refuses_protected_data_and_real_mode(self):
        good = self.config()
        n.validate(good)
        for kind in ["external", "shared", "writable", "real", "network"]:
            bad = copy.deepcopy(good)
            if kind == "external":
                bad["volumes"]["data"]["external"] = True
            if kind == "shared":
                bad["volumes"]["data"]["name"] = "protected_data"
            if kind == "writable":
                bad["services"]["backend"]["volumes"][0]["read_only"] = False
            if kind == "real":
                bad["services"]["backend"]["environment"]["OWNED_DRAFT_MODE"] = "LOCAL_REAL"
            if kind == "network":
                bad["networks"]["state"]["internal"] = False
            with self.assertRaises(RuntimeError):
                n.validate(bad)

    def test_pid_reuse_is_never_signalled(self):
        with patch.object(n, "alive", return_value=False), patch.object(n.os, "killpg") as kill:
            n.stop_process({"pid": 123, "birth": "different process"})
            kill.assert_not_called()

    def test_atomic_state_and_private_database_secret(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(n, "ROOT", Path(folder)):
            release = n.Release()
            n.atomic(release.runtime_file, {"test": True})
            self.assertEqual(release.runtime_file.read_text().strip(), '{\n  "test": true\n}')
            self.assertEqual((release.private / "database.json").stat().st_mode & 0o777, 0o600)
            self.assertNotIn("password", release.runtime_file.read_text())

    def test_unhealthy_release_cannot_smoke(self):
        from types import SimpleNamespace

        from smoke_local_release import smoke

        with self.assertRaisesRegex(RuntimeError, "RELEASE_NOT_READY"):
            smoke(SimpleNamespace(status=lambda: {"status": "BLOCKED"}))

    def test_source_drift_refuses_before_launch(self):
        import json

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "release").mkdir()
            (root / "release/local-v1.0.json").write_text(
                json.dumps({"source_sha256": {"file.py": "before"}})
            )
            with patch.object(n, "source_files", return_value={"file.py": "after"}):
                with self.assertRaisesRegex(RuntimeError, "SOURCE_DRIFT"):
                    n.verify_sources(root)

    def test_resource_refusal_terminates_only_owned_command(self):
        import sys

        with tempfile.TemporaryDirectory() as folder, patch.object(n, "ROOT", Path(folder)):
            release = n.Release()
            release.gate = lambda: (_ for _ in ()).throw(RuntimeError("RESOURCE_GATE"))
            with self.assertRaisesRegex(RuntimeError, "RESOURCE_GATE"):
                release.command([sys.executable, "-c", "import time; time.sleep(30)"], "refused")
            # Cleanup commands bypass the work gate rather than silently skipping cleanup.
            self.assertEqual(
                release.command([sys.executable, "-c", "pass"], "cleanup", monitor=False), 0
            )


if __name__ == "__main__":
    unittest.main()
