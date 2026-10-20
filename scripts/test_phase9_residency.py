"""Offline controller failure tests; no models, services or downloads."""

import unittest

from phase9_residency import Residency


class ApprovedProfileTests(unittest.TestCase):
    def test_distinct_profile_limits_and_no_overrides(self):
        from phase9_residency import generation_port

        for model, limit in [("nova-qwen-phase9", 32), ("nova-qwen-phase9-rag96", 96)]:
            body = {"model": model, "max_tokens": limit, "temperature": 0, "stream": False}
            self.assertEqual(generation_port(body), 11434)
            for change in [
                {"max_tokens": limit + 1},
                {"max_tokens": True},
                {"max_tokens": 0},
                {"num_gpu": 1},
                {"num_ctx": 1024},
                {"stream": True},
                {"temperature": 0.1},
                {"model": "unknown"},
            ]:
                with self.assertRaises(ValueError):
                    generation_port({**body, **change})
        with self.assertRaises(ValueError):
            generation_port(
                {"model": "nova-qwen-phase9", "max_tokens": 96, "temperature": 0, "stream": False}
            )


class ResidencyTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.now = 0
        self.r = Residency(
            lambda m: self.events.append(("start", m)),
            lambda: self.events.append(("stop",)),
            lambda: self.events.append(("gate",)),
            lambda: self.now,
        )

    def test_sequential_acquisition_release(self):
        for model in ("bge", "qwen"):
            token = self.r.acquire(model)
            self.r.check(token, model)
            self.r.release(token)
        self.assertEqual(
            self.events,
            [("gate",), ("start", "bge"), ("stop",), ("gate",), ("start", "qwen"), ("stop",)],
        )

    def test_busy_cannot_stop_other_lease(self):
        token = self.r.acquire("bge")
        with self.assertRaises(RuntimeError):
            self.r.acquire("qwen")
        self.r.check(token, "bge")
        self.assertNotIn(("stop",), self.events)

    def test_wrong_release_cannot_stop(self):
        token = self.r.acquire("bge")
        with self.assertRaises(RuntimeError):
            self.r.release("wrong")
        self.r.check(token, "bge")

    def test_expiry_reaps_abandoned_client(self):
        self.r.acquire("bge")
        self.now = 61
        self.r.reap()
        self.assertIsNone(self.r.model)
        self.assertEqual(self.events[-1], ("stop",))

    def test_resource_failure_never_starts(self):
        def refuse():
            raise RuntimeError("RESOURCE_GATE")

        self.r.resource = refuse
        with self.assertRaises(RuntimeError):
            self.r.acquire("bge")
        self.assertNotIn(("start", "bge"), self.events)

    def test_startup_failure_cleans_process(self):
        def refuse(_):
            raise TimeoutError("startup")

        self.r.start = refuse
        with self.assertRaises(TimeoutError):
            self.r.acquire("bge")
        self.assertEqual(self.events[-1], ("stop",))
        self.assertIsNone(self.r.model)

    def test_shutdown_failure_poisoned(self):
        def refuse():
            raise RuntimeError("TERMINATION_UNVERIFIED")

        token = self.r.acquire("bge")
        self.r.stop = refuse
        with self.assertRaises(RuntimeError):
            self.r.release(token)
        self.assertTrue(self.r.poisoned)
        with self.assertRaises(RuntimeError):
            self.r.acquire("qwen")

    def test_cancelled_start_cleans_process(self):
        def cancelled(_):
            raise KeyboardInterrupt

        self.r.start = cancelled
        with self.assertRaises(KeyboardInterrupt):
            self.r.acquire("bge")
        self.assertEqual(self.events[-1], ("stop",))
        self.assertIsNone(self.r.model)

    def test_wrong_model_rejected(self):
        token = self.r.acquire("bge")
        with self.assertRaises(RuntimeError):
            self.r.check(token, "qwen")


class InferenceAdmissionTests(unittest.TestCase):
    def test_swap_changes_after_acquire_refuse_before_generation(self):
        from unittest.mock import Mock

        resource = Mock(side_effect=[None, RuntimeError("RESOURCE_GATE")])
        stop, invoke = Mock(), Mock()
        r = Residency(lambda _: None, stop, resource)
        token = r.acquire("qwen")
        with self.assertRaisesRegex(RuntimeError, "RESOURCE_GATE"):
            r.infer(token, "qwen", invoke)
        invoke.assert_not_called()
        stop.assert_called_once()
        self.assertIsNone(r.token)

    def test_duplicate_lease_cannot_queue_or_replace_runtime(self):
        import threading

        r = Residency(lambda _: None, lambda: None, lambda: None)
        token = r.acquire("bge")
        entered = threading.Event()
        finish = threading.Event()
        outcomes = []

        def run():
            def invoke():
                entered.set()
                finish.wait(2)
                return "controlled"

            try:
                outcomes.append(r.infer(token, "bge", invoke))
            except RuntimeError:
                outcomes.append("refused")

        worker = threading.Thread(target=run)
        worker.start()
        self.assertTrue(entered.wait(1))
        try:
            with self.assertRaisesRegex(RuntimeError, "BUSY"):
                r.infer(token, "bge", lambda: None)
            r.release(token)
            with self.assertRaises(RuntimeError):
                r.acquire("qwen")
        finally:
            finish.set()
            worker.join(timeout=2)
        self.assertEqual(outcomes, ["refused"])
        self.assertFalse(worker.is_alive())
        token = r.acquire("qwen")
        r.release(token)


class ProcessTerminationTests(unittest.TestCase):
    def refused_child(self, folder):
        import subprocess
        import sys
        from pathlib import Path

        from phase9_residency import Runtime

        runtime = Runtime(Path(folder), Path(folder))
        # A tiny Python sleeper stands for loading; no model/framework is used.
        runtime.model = "bge-small-en-v1.5"
        runtime.records = [{"state": "STARTING"}]
        runtime.process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        return runtime, runtime.process

    def test_swap_exceeded_during_loading_records_refusal_and_terminates(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import Mock

        with tempfile.TemporaryDirectory() as folder:
            runtime, child = self.refused_child(folder)
            runtime.last_resources = {"swap_mib": 2100, "free_disk_bytes": 10 * 1024**3}
            runtime.resources = Mock(side_effect=RuntimeError("RESOURCE_GATE"))
            runtime.persist()
            r = Residency(lambda _: None, runtime.stop, lambda: None)
            token = r.acquire("qwen")
            try:
                with self.assertRaisesRegex(RuntimeError, "RESOURCE_GATE"):
                    runtime.monitor()
                with self.assertRaisesRegex(RuntimeError, "RESOURCE_GATE"):
                    r.release(token)
                record = json.loads((Path(folder) / "residency.json").read_text())[0]
                self.assertEqual(record["last_resources"]["swap_mib"], 2100)
                self.assertTrue(record["stopped"])
                self.assertEqual(record["after_resource_error"], "RESOURCE_CHECK_FAILED")
                self.assertNotIn("inference_started_at", record)
                self.assertIsNotNone(child.poll())
                self.assertIsNone(runtime.process)
                self.assertTrue(r.poisoned)
                with self.assertRaisesRegex(RuntimeError, "RESIDENCY_UNAVAILABLE"):
                    r.acquire("qwen")
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=2)

    def test_record_write_failure_still_terminates_and_poisons(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as folder:
            runtime, child = self.refused_child(folder)
            runtime.resources = lambda: {"swap_mib": 0, "free_disk_bytes": 10 * 1024**3}
            runtime.persist()
            r = Residency(lambda _: None, runtime.stop, lambda: None)
            token = r.acquire("qwen")
            try:
                with patch.object(Path, "replace", side_effect=PermissionError("unavailable")):
                    with self.assertRaises(PermissionError):
                        r.release(token)
                self.assertIsNotNone(child.poll())
                self.assertIsNone(runtime.process)
                self.assertTrue(r.poisoned)
                # The last valid file survives failed atomic replacement, without
                # falsely claiming that its STARTING record verifies termination.
                record = json.loads((Path(folder) / "residency.json").read_text())[0]
                self.assertEqual(record, {"state": "STARTING"})
                with self.assertRaisesRegex(RuntimeError, "RESIDENCY_UNAVAILABLE"):
                    r.acquire("qwen")
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=2)

    def test_exact_swap_ceiling_refuses_but_retains_measurement(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch

        from phase9_residency import Runtime

        with tempfile.TemporaryDirectory() as folder:
            runtime = Runtime(Path(folder), Path(folder))
            with patch("shutil.disk_usage", return_value=SimpleNamespace(free=10 * 1024**3)):
                for swap in (2047.99, 2048.0, 2100.0):
                    with patch("subprocess.check_output", return_value=f"used = {swap}M"):
                        if swap < 2048:
                            self.assertEqual(runtime.resources()["swap_mib"], swap)
                        else:
                            with self.assertRaisesRegex(RuntimeError, "RESOURCE_GATE"):
                                runtime.resources()
                        self.assertEqual(runtime.last_resources["swap_mib"], swap)

    def test_inference_deadline_refused(self):
        import tempfile
        import time
        from pathlib import Path

        from phase9_residency import Runtime

        with tempfile.TemporaryDirectory() as folder:
            runtime = Runtime(Path(folder), Path(folder))
            runtime.resources = lambda: {}
            runtime.request_deadline = time.monotonic() - 1
            with self.assertRaisesRegex(RuntimeError, "INFERENCE_DEADLINE"):
                runtime.monitor()

    def test_real_child_terminated_without_model(self):
        import subprocess
        import sys
        import tempfile
        from pathlib import Path

        from phase9_residency import Runtime

        with tempfile.TemporaryDirectory() as folder:
            runtime = Runtime(Path(folder), Path(folder))
            runtime.resources = lambda: {"swap_mib": 0, "free_disk_bytes": 10 * 1024**3}
            runtime.model = "bge-small-en-v1.5"
            runtime.records = [{"state": "STARTING"}]
            runtime.process = subprocess.Popen(
                [sys.executable, "-c", "import time; time.sleep(30)"]
            )
            child = runtime.process
            try:
                runtime.stop()
                self.assertIsNotNone(child.poll())
                self.assertTrue(runtime.records[-1]["stopped"])
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=2)


if __name__ == "__main__":
    unittest.main()
