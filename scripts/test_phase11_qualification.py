"""Deterministic qualification-runner safety tests; never Docker/model traffic."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import qualify_phase11 as q


class QualificationTests(unittest.TestCase):
    def config(self):
        return {
            "volumes": {"db": {"name": "nova-phase11-q-012345abcdef_db"}},
            "services": {
                "backend": {
                    "environment": {"OWNED_DRAFT_MODE": "FIXTURE"},
                    "volumes": [
                        {"type": "bind", "source": str(q.ROOT / "backend/app"), "read_only": True}
                    ],
                }
            },
        }

    def test_exact_limits(self):
        q.enforce({"swap_mib": 2047.99, "free_disk_bytes": 5 * 1024**3})
        for swap, disk in [(2048, 6 * 1024**3), (0, 5 * 1024**3 - 1)]:
            with self.assertRaisesRegex(RuntimeError, "RESOURCE_GATE"):
                q.enforce({"swap_mib": swap, "free_disk_bytes": disk})

    def test_config_refuses_protected_mounts_and_real_settings(self):
        good = self.config()
        q.validate_config(good, "nova-phase11-q-012345abcdef")
        bad = []
        for key in ["INFERENCE_CONFIG_FILE", "INFERENCE_RESIDENCY_KEY_FILE"]:
            item = copy.deepcopy(good)
            item["services"]["backend"]["environment"][key] = "/private/key"
            bad.append(item)
        item = copy.deepcopy(good)
        item["volumes"]["db"]["external"] = True
        bad.append(item)
        item = copy.deepcopy(good)
        item["volumes"]["db"]["name"] = "protected_app_db"
        bad.append(item)
        item = copy.deepcopy(good)
        item["services"]["backend"]["volumes"][0]["read_only"] = False
        bad.append(item)
        for item in bad:
            with self.assertRaises(ValueError):
                q.validate_config(item, "nova-phase11-q-012345abcdef")
        with self.assertRaises(ValueError):
            q.validate_config(good, "nova")

    def test_child_group_termination(self):
        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"], start_new_session=True
        )
        try:
            q.Runner.terminate(child)
            self.assertIsNotNone(child.poll())
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=2)

    def test_failed_required_stage_never_passes(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(q, "ROOT", Path(folder)):
            runner = q.Runner(["host"])
            runner.setup = lambda: None
            runner.gate = lambda: None
            runner.run = lambda *a, **k: (_ for _ in ()).throw(
                RuntimeError("SCRIPTED_STAGE_FAILURE")
            )
            self.assertFalse(runner.execute())
            report = json.loads((runner.out / "report.json").read_text())
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["real_calls"], 0)

    def test_subset_cannot_claim_full_qualification(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(q, "ROOT", Path(folder)):
            runner = q.Runner(["host"])
            runner.setup = lambda: None
            runner.gate = lambda: None
            runner.run = lambda *a, **k: None
            self.assertTrue(runner.execute())
            self.assertEqual(runner.report["status"], "PARTIAL_PASS")

    def test_cleanup_failure_cannot_pass_and_does_not_stop_other_projects(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(q, "ROOT", Path(folder)):
            runner = q.Runner(["host"])
            runner.setup = lambda: None
            runner.gate = lambda: None
            runner.run = lambda *a, **k: None
            runner.owned = True
            runner.cleanup = lambda: False
            self.assertFalse(runner.execute())
            self.assertFalse(runner.report["services_stopped"])

    def test_resource_refusal_prevents_child_launch(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(q, "ROOT", Path(folder)):
            runner = q.Runner(["host"])
            runner.gate = lambda: (_ for _ in ()).throw(RuntimeError("RESOURCE_GATE"))
            with patch.object(q.subprocess, "Popen") as child:
                with self.assertRaisesRegex(RuntimeError, "RESOURCE_GATE"):
                    runner.run(["false"], "refused")
                child.assert_not_called()

    def test_command_failure_is_recorded_without_retry(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(q, "ROOT", Path(folder)):
            runner = q.Runner(["host"])
            runner.gate = lambda: None
            with self.assertRaisesRegex(RuntimeError, "scripted FAILED"):
                runner.run([sys.executable, "-c", "raise SystemExit(3)"], "scripted", cwd=folder)
            self.assertEqual(len(runner.records), 1)
            self.assertEqual(runner.records[0]["exit_code"], 3)

    def test_network_plan_avoids_existing_and_host_routes(self):
        self.assertEqual(
            q.allocate_subnets(["10.240.0.0/23", "192.168.4.0/22"], 2),
            ["10.240.2.0/24", "10.240.3.0/24"],
        )
        with self.assertRaisesRegex(RuntimeError, "NO_ISOLATED_NETWORK_SPACE"):
            q.allocate_subnets(["10.0.0.0/8"], 1)

    def test_legacy_fixture_harness_allows_only_reviewed_phase11_project_shape(self):
        from acceptance_phase10 import isolated_project

        self.assertTrue(isolated_project("nova-phase10-qualification"))
        self.assertTrue(isolated_project("nova-phase11-q-012345abcdef"))
        for project in ("nova", "nova-phase11-production", "nova-phase11-q-invalid"):
            self.assertFalse(isolated_project(project))

    def test_terminal_policy_allows_refusal_but_never_real_calls_or_missing_data(self):
        from phase11_integration import verify_terminal

        snapshot = {
            "real_configuration_refusals": 1,
            "running_or_done_real_inference_rows": 0,
            "unexpected_real_failures": 0,
            "non_fixture_invocations": 0,
            "owned_draft_executions": 0,
            "evaluation_schemas": 0,
        }
        verify_terminal(snapshot)
        for key in snapshot:
            bad = dict(snapshot)
            del bad[key]
            with self.assertRaises(RuntimeError):
                verify_terminal(bad)
        for key in set(snapshot) - {"real_configuration_refusals"}:
            with self.assertRaises(RuntimeError):
                verify_terminal({**snapshot, key: 1})


if __name__ == "__main__":
    unittest.main()
