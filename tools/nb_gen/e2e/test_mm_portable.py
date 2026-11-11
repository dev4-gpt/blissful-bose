"""CPU tests of recovery, coverage, strict placement, export and notebook launch gates."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zipfile import ZipFile
from io import BytesIO
import json
import sys
import tempfile
import unittest

GEN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GEN))
import make_mm_safetybench_portable as builder
import mm_safetybench_portable_models as models
import mm_safetybench_portable_runtime as runtime

FIELDS = {"TEXT": "Question", "SD": "Rephrased Question(SD)",
          "TYPO": "Rephrased Question", "SD_TYPO": "Rephrased Question"}


def cases(n=1680):
    return [dict(scenario=f"{i % 13 + 1:02d}_scenario", id=str(i), variant=v,
                 field=field, question="benign test fixture", image_path=None)
            for i in range(n) for v, field in FIELDS.items()]


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "run"
        self.rows = cases(3)
        self.identity = dict(model="fixture", revision="fixed", manifest="fixed")
        runtime.FIELDS = FIELDS

    def tearDown(self):
        self.temp.cleanup()

    def record(self, row):
        return dict(row, response="benign answer", identity_sha256=runtime.fingerprint(self.identity), seconds=2)

    def test_resume_does_not_reinfer_saved_answers(self):
        runtime.validated_ledger(self.root, self.rows, self.identity)
        runtime.append(self.root / "responses_PRIVATE.jsonl", self.record(self.rows[0]))
        seen = runtime.validated_ledger(self.root, self.rows, self.identity)
        calls = []
        def answer(row, images, loaded):
            calls.append(runtime.uid(row))
            return "benign generated answer", 2
        fake_torch = SimpleNamespace(cuda=SimpleNamespace(synchronize=lambda: None))
        with patch.dict(sys.modules, torch=fake_torch), patch.object(runtime, "answer_case", answer, create=True):
            runtime.MAX_NEW_TOKENS = 256
            runtime.generate_rows(self.rows, self.rows, self.root, seen, self.identity, None, None, float("inf"))
        self.assertEqual(len(calls), len(self.rows) - 1)
        self.assertEqual(len(runtime.validated_ledger(self.root, self.rows, self.identity)), len(self.rows))

    def test_interrupted_tail_archived_and_complete_prefix_kept(self):
        runtime.validated_ledger(self.root, self.rows, self.identity)
        ledger = self.root / "responses_PRIVATE.jsonl"
        runtime.append(ledger, self.record(self.rows[0]))
        with ledger.open("ab") as stream:
            stream.write(b'{"incomplete":')
        seen = runtime.validated_ledger(self.root, self.rows, self.identity)
        self.assertEqual(len(seen), 1)
        self.assertEqual(len(list(self.root.glob("interrupted_tail_*"))), 1)
        self.assertTrue(ledger.read_bytes().endswith(b"\n"))

    def test_duplicates_wrong_checkpoint_unknown_and_empty_rejected(self):
        for kind in ("duplicate", "checkpoint", "unexpected", "empty"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / "run"
                runtime.validated_ledger(root, self.rows, self.identity)
                record = self.record(self.rows[0])
                if kind == "unexpected":
                    record["id"] = "unknown"
                if kind == "empty":
                    record["response"] = " "
                runtime.append(root / "responses_PRIVATE.jsonl", record)
                if kind == "duplicate":
                    runtime.append(root / "responses_PRIVATE.jsonl", record)
                identity = dict(self.identity, revision="changed") if kind == "checkpoint" else self.identity
                with self.assertRaises(ValueError):
                    runtime.validated_ledger(root, self.rows, identity)

    def test_budget_stop_preserves_ledger(self):
        seen = runtime.validated_ledger(self.root, self.rows, self.identity)
        fake_torch = SimpleNamespace(cuda=SimpleNamespace(synchronize=lambda: None))
        with patch.dict(sys.modules, torch=fake_torch), self.assertRaises(TimeoutError):
            runtime.generate_rows(self.rows, self.rows, self.root, seen, self.identity, None, None, 0)
        self.assertFalse((self.root / "responses_PRIVATE.jsonl").exists())

    def test_pilot_coverage_and_eta(self):
        rows = cases()
        pilot = runtime.pilot_cases(rows)
        self.assertEqual(len(pilot), 52)
        remaining = [r for r in rows if runtime.uid(r) not in {runtime.uid(x) for x in pilot}]
        self.assertEqual(runtime.eta_seconds([dict(r, seconds=2) for r in pilot], remaining), 2 * (6720 - 52))
        with self.assertRaises(ValueError):
            runtime.pilot_cases([r for r in rows if r["variant"] != "SD"])

    def test_partial_export_blocked_complete_export_contains_released_rubric_ids(self):
        rows = cases()
        runtime.TRACK = "fixture"
        runtime.AUTHOR_SHA = "fixture_source_hash"
        runtime.RELEASE_RUBRIC = {"08": "special"}
        with patch.object(runtime, "released_rubrics", lambda: {"special": "released fixture"}, create=True), \
             patch.object(runtime, "digest", lambda p: "ledgerhash", create=True):
            runtime.validated_ledger(self.root, rows, self.identity)
            with self.assertRaises(ValueError):
                runtime.export_queue(self.root, rows, self.identity)
            for row in rows:
                runtime.append(self.root / "responses_PRIVATE.jsonl", self.record(row))
            queue = json.loads(runtime.export_queue(self.root, rows, self.identity).read_text())
            self.assertEqual(len(queue["rows"]), 6720)
            self.assertEqual(queue["evaluation_status"], "unscored")
            self.assertTrue(any(r["safety_rubric"] == "special" for r in queue["rows"]))


class PlacementTests(unittest.TestCase):
    def test_cpu_meta_quantization_and_fp32_rejected(self):
        for kind in ("cpu", "meta", "quantized", "fp32", "disk"):
            parameter = SimpleNamespace(device=SimpleNamespace(type="cuda"), dtype="torch.float16",
                                        is_floating_point=lambda: True)
            model = SimpleNamespace(hf_device_map={"": 0}, named_parameters=lambda: [("weight", parameter)])
            if kind in {"cpu", "meta"}:
                parameter.device = SimpleNamespace(type=kind)
            if kind == "disk":
                model.hf_device_map = {"": "disk"}
            if kind == "quantized":
                model.is_loaded_in_4bit = True
            if kind == "fp32":
                parameter.dtype = "torch.float32"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                models.assert_gpu_only(model)

    def test_bchw_no_shape_repair(self):
        models.check_pixels(SimpleNamespace(ndim=4, shape=(1, 3, 224, 224)))
        for shape in ((1, 1, 3, 224, 224), (2, 3, 224, 224), (1, 4, 224, 224)):
            with self.assertRaises(ValueError):
                models.check_pixels(SimpleNamespace(ndim=len(shape), shape=shape))

    def test_two_gpu_budgets_and_single_t4_rejected(self):
        models.TRACK = "idefics"
        def gpu(count):
            return SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: True, device_count=lambda: count,
                                   mem_get_info=lambda i: (15 * 2**30, 16 * 2**30)))
        with self.assertRaises(RuntimeError):
            models.gpu_budgets(gpu(1))
        self.assertEqual(len(models.gpu_budgets(gpu(2))), 2)


class NotebookTests(unittest.TestCase):
    def test_two_gpu_allocation_clock_is_immutable_and_setup_is_capped(self):
        output = self._tmp()
        scratch = self._tmp()
        namespace = dict(RUN_GENERATION=True, MODE="full", PLATFORM="kaggle", TRACK="idefics",
                         AUTHOR_ZIP=__file__, IMAGE_ZIP=__file__, OUTPUT_ROOT=output, RUN_ID="test",
                         WORKER_SOURCE="", APPROVAL_RECORD="fixture owner approval", ALLOCATION_ID="fixture",
                         GPU_MINUTES=120, EXISTING_QUOTA_ONLY=False)
        launcher = builder.LAUNCHER.replace('/kaggle/working/mm_gpu_only_PRIVATE', scratch)
        def fake_run(command, **kwargs):
            if command[0] == "nvidia-smi":
                return SimpleNamespace(stdout="T4, 15360\nT4, 15360\n")
            raise RuntimeError("stop before installation")
        with patch("subprocess.run", side_effect=fake_run), patch("shutil.which", return_value="/usr/bin/uv"):
            for now in (1000, 1030):
                with patch("time.time", return_value=now), self.assertRaisesRegex(RuntimeError, "stop before installation"):
                    exec(launcher, namespace)
                allocation, = (Path(output) / "idefics/test/allocations_PRIVATE").glob("*.json")
                self.assertEqual(json.loads(allocation.read_text())["deadline"], 4600)
            namespace["GPU_MINUTES"] = 121
            with self.assertRaisesRegex(ValueError, "cannot be changed/reset"):
                exec(launcher, namespace)

    def test_existing_quota_approval_has_no_software_deadline(self):
        output, scratch = self._tmp(), self._tmp()
        namespace = dict(RUN_GENERATION=True, MODE="full", PLATFORM="kaggle", TRACK="idefics",
                         AUTHOR_ZIP=__file__, IMAGE_ZIP=__file__, OUTPUT_ROOT=output, RUN_ID="test",
                         WORKER_SOURCE="", APPROVAL_RECORD="owner existing quota approval", ALLOCATION_ID="quota",
                         GPU_MINUTES=None, EXISTING_QUOTA_ONLY=True)
        launcher = builder.LAUNCHER.replace('/kaggle/working/mm_gpu_only_PRIVATE', scratch)
        def fake_run(command, **kwargs):
            if command[0] == "nvidia-smi":
                return SimpleNamespace(stdout="T4, 15360\nT4, 15360\n")
            self.assertIsNone(kwargs["timeout"])
            raise RuntimeError("stop before installation")
        with patch("subprocess.run", side_effect=fake_run), patch("shutil.which", return_value="/usr/bin/uv"), self.assertRaisesRegex(RuntimeError, "stop before installation"):
            exec(launcher, namespace)
        allocation, = (Path(output) / "idefics/test/allocations_PRIVATE").glob("*.json")
        self.assertIsNone(json.loads(allocation.read_text())["deadline"])

    def test_release_pairing_rejects_missing_image(self):
        namespace = {"__name__": "test_worker"}
        exec(builder.worker_source(builder.ROOT), namespace)
        namespace["FIELDS"] = FIELDS
        data = BytesIO()
        scenario = "01_fixture"
        with ZipFile(data, "w") as archive:
            archive.writestr("release/TinyVersion_ID_List.json", json.dumps([{"Scenario": scenario}]))
            archive.writestr(f"release/data/processed_questions/{scenario}.json",
                             json.dumps({"0": dict.fromkeys(FIELDS.values(), "benign fixture")}))
        class MissingImages:
            def namelist(self):
                return []
        with ZipFile(data) as author, self.assertRaisesRegex(ValueError, "Missing or ambiguous"):
            namespace["make_manifest"](author, MissingImages(), expected_items=1, expected_scenarios=1)

    def test_embedded_code_and_launcher_gate(self):
        source = builder.worker_source(builder.ROOT)
        compile(source, "worker", "exec")
        for _, (_, _, _, _, filename) in builder.MODELS.items():
            nb = json.loads((builder.ROOT / "notebooks" / filename).read_text())
            embedded = {}
            exec("".join(nb["cells"][4]["source"]), embedded)
            self.assertEqual(embedded["WORKER_SOURCE"], source)
            for cell in nb["cells"]:
                if cell["cell_type"] == "code":
                    compile("".join(cell["source"]), filename, "exec")
        # No installs, subprocesses, mounts or downloads before a new allocation is supplied.
        namespace = dict(RUN_GENERATION=True, MODE="full", PLATFORM="kaggle", TRACK="idefics",
                         AUTHOR_ZIP=__file__, IMAGE_ZIP=__file__, OUTPUT_ROOT=self._tmp(), RUN_ID="test",
                         WORKER_SOURCE=source, APPROVAL_RECORD="", ALLOCATION_ID="", GPU_MINUTES=0)
        # Isolate hardcoded Kaggle scratch creation in a temporary path for CPU testing.
        launcher = builder.LAUNCHER.replace('/kaggle/working/mm_gpu_only_PRIVATE', self._tmp())
        with patch("subprocess.run", side_effect=AssertionError("No subprocess authorized")), self.assertRaisesRegex(RuntimeError, "New GPU budget"):
            exec(launcher, namespace)

    def _tmp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return directory.name


if __name__ == "__main__":
    unittest.main()
