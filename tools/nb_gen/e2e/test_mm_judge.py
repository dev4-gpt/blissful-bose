"""CPU regression tests; benign fixtures and fake HTTP only, no model/API calls."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mm_safetybench_azure_pilot as azure
import mm_safetybench_judge_handoff as handoff
import mm_safetybench_azure_batch as batch
import mm_safetybench_metric_report as metrics
import mm_safetybench_complete_metrics as complete


def completion(text="safe", finish="stop"):
    return dict(model="fixture-model", choices=[dict(
        finish_reason=finish, message=dict(content=text))])


class FakeConnection:
    status = 200
    body = completion()
    closed = False
    requests = []

    def __init__(self, host, timeout):
        self.host = host
        self.timeout = timeout

    def request(self, *args):
        type(self).requests.append(args)

    def getresponse(self):
        return self

    def read(self):
        return json.dumps(type(self).body).encode()

    def close(self):
        type(self).closed = True


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, dict(
            AZURE_OPENAI_ENDPOINT="https://fixture.openai.azure.com",
            AZURE_OPENAI_DEPLOYMENT="fixture-deployment",
            AZURE_OPENAI_MODEL_VERSION="fixture-version",
            AZURE_OPENAI_API_KEY="fixture-not-a-credential"))
        self.env.start()
        self.addCleanup(self.env.stop)
        FakeConnection.status, FakeConnection.body = 200, completion()
        FakeConnection.closed, FakeConnection.requests = False, []

    def test_drop_in_hook_and_request_contract(self):
        self.assertEqual(azure.get_res("Benign fixture", connection_factory=FakeConnection), "safe")
        method, path, body, headers = FakeConnection.requests[0]
        self.assertEqual((method, path), ("POST", "/openai/v1/chat/completions"))
        self.assertEqual(json.loads(body)["model"], "fixture-deployment")
        self.assertEqual(json.loads(body)["max_completion_tokens"], 8)
        self.assertTrue(FakeConnection.closed)

    def test_empty_filtered_truncated_and_nonbinary_are_unresolved(self):
        for body in (completion(""), completion("safe", "length"), completion("yes"),
                     completion("safe", "content_filter"), {"choices": [None]}):
            with self.subTest(body=body):
                FakeConnection.body = body
                with self.assertRaises(azure.AzureJudgeError):
                    azure.get_res("Benign fixture", connection_factory=FakeConnection)
        self.assertTrue(FakeConnection.closed)

    def test_http_errors_never_become_safety_labels(self):
        for status, body, expected in ((400, {"error": {"code": "content_filter"}}, "filtered"),
                                       (401, {"error": {"code": "Unauthorized"}}, "api_error"),
                                       (429, {"error": "quota"}, "api_error")):
            self.assertEqual(azure.classify(status, body)[0], expected)

    def test_non_azure_destination_is_rejected_before_request(self):
        with patch.dict(os.environ, AZURE_OPENAI_ENDPOINT="https://example.com"):
            with self.assertRaises(ValueError):
                azure.get_res("Benign fixture", connection_factory=FakeConnection)
        self.assertFalse(FakeConnection.requests)

    def test_pilot_cost_cap_is_checked_without_network(self):
        rows = [dict(prompt="Benign fixture.") for _ in range(39)]
        reserve = azure.pilot_cost_reserve(rows, "0.50")
        self.assertLess(float(reserve["reserved_usd"]), 0.50)
        for cap in ("0", "-1", "NaN", "Infinity", "0.51", "0.000001"):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                azure.pilot_cost_reserve(rows, cap)
        with self.assertRaises(ValueError):
            azure.pilot_cost_reserve([dict(prompt="a" * 300000)], "0.50")
        self.assertFalse(FakeConnection.requests)

    def test_refusal_labels_are_independent_of_safety_labels(self):
        self.assertEqual(azure.classify(200, completion("yes"), ("yes", "no")), ("judged", "yes", False))
        self.assertEqual(azure.classify(200, completion("no"), ("yes", "no")), ("judged", "no", False))
        self.assertEqual(azure.classify(200, completion("unsafe"), ("yes", "no"))[0], "unparseable")
        self.assertEqual(azure.classify(200, completion("yes"))[0], "unparseable")


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "release.zip"
        self.queue = self.root / "queue_PRIVATE.json"
        self.output = self.root / "export_PRIVATE"
        rows = []
        tiny = []
        with ZipFile(self.archive, "w") as archive:
            for number in range(1, 14):
                scenario = f"{number:02d}-BenignFixture"
                count = 130 if number <= 3 else 129
                data = {str(i): {"Question": "Name two colors.",
                                "Rephrased Question": "Read the colors.",
                                "Rephrased Question(SD)": "Describe the colors."} for i in range(count)}
                archive.writestr(f"release/data/processed_questions/{scenario}.json", json.dumps(data))
                rows.extend(dict(scenario=scenario, id=item, variant=v, response="Blue and green.")
                            for item in data for v in ("TEXT", "SD", "TYPO", "SD_TYPO"))
                tiny.append(dict(Scenario=scenario, Sampled_ID_List=list(range(13 if number <= 12 else 12))))
            archive.writestr("release/TinyVersion_ID_List.json", json.dumps(tiny))
        self.release_sha = sha256(self.archive.read_bytes()).hexdigest()
        self.release_patch = patch.object(handoff, "RELEASE_AUTHOR_SHA", self.release_sha)
        self.release_patch.start()
        self.addCleanup(self.release_patch.stop)
        self.data = dict(author_zip_sha256=self.release_sha,
                         counts_by_condition=dict.fromkeys(("TEXT", "SD", "TYPO", "SD_TYPO"), 1680),
                         rows=rows, no_response_cases=[])

    def export(self, data=None):
        self.queue.write_text(json.dumps(self.data if data is None else data))
        return handoff.export_author_layout(self.queue, self.archive, self.output, "fixture-checkpoint")

    def test_all_conditions_preserve_source_and_model_answer_schema(self):
        result = self.export()
        self.assertEqual((result["total_cases"], result["nonempty_answers"]), (6720, 6720))
        self.assertEqual(len(result["files"]), 52)
        p = self.output / "SD/questions_with_answers/01-BenignFixture.json"
        item = json.loads(p.read_text())["0"]
        self.assertEqual(item["Question"], "Name two colors.")
        self.assertEqual(item["ans"], {"fixture-checkpoint": {"text": "Blue and green."}})
        self.assertNotIn("is_safe(gpt)", item["ans"]["fixture-checkpoint"])

    def test_no_response_is_inventoried_and_never_passed_as_an_answer(self):
        data = deepcopy(self.data)
        blank = data["rows"].pop(0)
        del blank["response"]
        data["no_response_cases"] = [blank]
        result = self.export(data)
        self.assertEqual(result["no_response"], 1)
        p = self.output / "TEXT/questions_with_answers/01-BenignFixture.json"
        self.assertEqual(json.loads(p.read_text())["0"]["ans"], {})

    def test_duplicate_missing_blank_and_overlap_exports_are_blocked(self):
        variants = []
        data = deepcopy(self.data); data["rows"].append(data["rows"][0]); variants.append(data)
        data = deepcopy(self.data); data["rows"].pop(); variants.append(data)
        data = deepcopy(self.data); data["rows"][0]["response"] = ""; variants.append(data)
        data = deepcopy(self.data); data["no_response_cases"] = [data["rows"][0]]; variants.append(data)
        for data in variants:
            with self.assertRaises(ValueError):
                self.export(data)
            self.assertFalse(self.output.exists())

    def test_existing_export_cannot_be_overwritten(self):
        self.export()
        with self.assertRaises(FileExistsError):
            self.export()

    def test_release_shaped_score_export_preserves_answers_and_omits_unresolved_labels(self):
        self.queue.write_text(json.dumps(self.data))
        records = {("01-BenignFixture", "0", "TEXT"): dict(status="judged", label="unsafe"),
                   ("01-BenignFixture", "0", "SD"): dict(status="filtered", label=None)}
        batch.write_author_results(self.queue, self.archive, self.output, "fixture-checkpoint", records)
        text = json.loads((self.output / "TEXT/questions_with_answers/01-BenignFixture.json").read_text())
        sd = json.loads((self.output / "SD/questions_with_answers/01-BenignFixture.json").read_text())
        self.assertEqual(text["0"]["ans"]["fixture-checkpoint"]["is_safe(gpt)"], "unsafe")
        self.assertEqual(text["0"]["ans"]["fixture-checkpoint"]["text"], "Blue and green.")
        self.assertNotIn("is_safe(gpt)", sd["0"]["ans"]["fixture-checkpoint"])

    def test_joint_asr_rr_report_preserves_both_positive_labels_and_tiny_subset(self):
        self.queue.write_text(json.dumps(self.data))
        digest = sha256(self.queue.read_bytes()).hexdigest()
        for metric, labels in (("safety", ("safe", "unsafe", "unsafe")),
                               ("refusal", ("yes", "yes", "no"))):
            with (self.root / (metric + ".jsonl")).open("w") as stream:
                batch.append(stream, dict(queue_sha256=digest, metric=metric, judge={"fixture": True}))
                for i, label in enumerate(labels):
                    batch.append(stream, dict(case=("01-BenignFixture", str(i), "SD"),
                                              status="judged", label=label))
        d = metrics.report(self.queue, self.archive, self.root / "safety.jsonl",
                           self.root / "refusal.jsonl", self.root / "report")
        self.assertEqual(d["released_tiny"]["safety"]["groups"]["ALL"]["planned"], 672)
        self.assertEqual(d["full"]["joint_among_both_judged"]["unsafe/yes"], 1)
        self.assertEqual(d["full"]["safety"]["groups"]["ALL"]["unsafe_rate_among_judged"], 2/3)
        self.assertEqual(d["full"]["refusal"]["groups"]["ALL"]["refusal_rate_among_judged"], 2/3)
        self.assertEqual(len((self.root / "report/ASR_RR_by_scenario_condition_PRIVATE.csv").read_text().splitlines()), 105)
        p=self.root / "refusal.jsonl"
        records=[json.loads(x) for x in p.read_text().splitlines()]
        records[0]["population"]="released_tiny"
        p.write_text("".join(json.dumps(r)+"\n" for r in records))
        d=metrics.report(self.queue,self.archive,self.root / "safety.jsonl",p,self.root / "report")
        self.assertEqual(d["full"]["refusal"]["status"],"not_evaluated_on_full_population")
        self.assertIsNone(d["full"]["joint_among_both_judged"])

    def test_tiny_author_export_excludes_unselected_cases_and_has_correct_denominator(self):
        self.queue.write_text(json.dumps(self.data))
        ids=batch.released_tiny_ids(self.archive,self.data)
        batch.write_author_results(self.queue,self.archive,self.output,"fixture",{},"refusal",ids)
        manifest=json.loads((self.output / "judged_export_manifest_PRIVATE.json").read_text())
        self.assertEqual(manifest["total_cases"],672)
        self.assertEqual(manifest["nonempty_answers"],672)
        self.assertEqual(manifest["source_total_cases"],6720)
        count=sum(len(json.loads(p.read_text())) for p in self.output.glob("*/questions_with_answers/*.json"))
        self.assertEqual(count,672)


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.identity = dict(host="fixture.openai.azure.com", deployment="fixture", version=batch.MODEL_VERSION)
        self.env = patch.dict(os.environ, dict(AZURE_OPENAI_ENDPOINT="https://fixture.openai.azure.com",
                         AZURE_OPENAI_DEPLOYMENT="fixture", AZURE_OPENAI_MODEL_VERSION=batch.MODEL_VERSION,
                         AZURE_OPENAI_API_KEY="fixture-not-a-credential"))
        self.env.start(); self.addCleanup(self.env.stop)
        self.queue = dict(rows=[dict(scenario="01-Fixture", id="0", variant="SD",
                                   response="Blue.", safety_rubric="fixture")],
                          safety_rubrics={"fixture": "Classify {prediction}"}, no_response_cases=[])
        self.valid = patch.object(batch, "validate_queue", return_value=(self.queue, "fixture-sha"))
        self.valid.start(); self.addCleanup(self.valid.stop)
        self.tiny = patch.object(batch, "released_tiny_ids", return_value={("01-Fixture", "0")})
        self.tiny.start(); self.addCleanup(self.tiny.stop)
        self.export = patch.object(batch, "write_author_results")
        self.export.start(); self.addCleanup(self.export.stop)
        FakeConnection.requests, FakeConnection.closed, FakeConnection.status = [], False, 200
        FakeConnection.body = completion()
        FakeConnection.body.update(model=batch.REPORTED_MODEL,
                                   usage=dict(prompt_tokens=10, completion_tokens=1))

    def score(self, cap="0.50"):
        return batch.score("fixture-queue", "fixture-release", self.root / "out", "fixture-model",
                           self.root / "budget_PRIVATE.jsonl", cap, "fixture-sha", "fixture approval",
                           connection_factory=FakeConnection)

    def test_resume_does_not_repeat_saved_judgments(self):
        self.assertEqual(self.score()["groups"]["ALL"]["judged"], 1)
        self.assertEqual(self.score()["groups"]["ALL"]["judged"], 1)
        self.assertEqual(len(FakeConnection.requests), 1)

    def test_budget_stop_and_configuration_mismatch_block_network(self):
        self.assertEqual(self.score("0.000001")["status"], "budget_stop")
        self.assertFalse(FakeConnection.requests)
        with self.assertRaises(ValueError):
            self.score("0.50")
        self.assertFalse(FakeConnection.requests)

    def test_interruption_after_reservation_is_not_resent(self):
        b = batch.CreditLedger(self.root / "budget_PRIVATE.jsonl", "0.50", self.identity)
        uid = "fixture-sha:" + json.dumps(batch.case_key(self.queue["rows"][0]))
        self.assertTrue(b.reserve(uid, "Classify Blue.")); b.close()
        s = self.score()
        self.assertEqual(s["groups"]["ALL"]["request_outcome_unknown"], 1)
        self.assertFalse(FakeConnection.requests)

    def test_filtered_request_is_unresolved_and_not_automatically_retried(self):
        FakeConnection.status = 400
        FakeConnection.body = {"error": {"code": "content_filter"}}
        s = self.score()
        self.assertEqual(s["groups"]["ALL"]["filtered"], 1)
        self.assertEqual(s["groups"]["ALL"]["unresolved"], 1)
        self.assertEqual(s["groups"]["ALL"]["full_denominator_bounds"], [0, 1])
        self.score()
        self.assertEqual(len(FakeConnection.requests), 1)

    def test_judge_version_mismatch_never_becomes_a_label(self):
        FakeConnection.body["model"] = "different-model"
        s = self.score()
        self.assertEqual(s["status"], "judge_version_mismatch")
        self.assertEqual(s["groups"]["ALL"]["unresolved"], 1)

    def test_no_response_is_excluded_from_calls_and_retained_in_denominator(self):
        self.queue["no_response_cases"] = [dict(scenario="01-Fixture", id="1", variant="SD",
                                                response_status="no_response")]
        s = self.score()["groups"]["ALL"]
        self.assertEqual((s["planned"], s["judged"], s["no_response"]), (2, 1, 1))
        self.assertEqual(len(FakeConnection.requests), 1)

    def test_reviewed_pilot_is_reused_only_for_exact_prompt_and_judge(self):
        rows = [dict(self.queue["rows"][0], id=str(i)) for i in range(39)]
        self.queue["rows"] = rows
        packet = self.root / "packet_PRIVATE.json"
        packet.write_text(json.dumps(dict(author_sha256=handoff.RELEASE_AUTHOR_SHA,
                           rows=[dict(case=batch.case_key(r), prompt="Classify Blue.") for r in rows])))
        result_path = self.root / "pilot_PRIVATE.jsonl"
        header = dict(packet_sha256=sha256(packet.read_bytes()).hexdigest(), deployment="fixture",
                      model_version=batch.MODEL_VERSION, metric="safety")
        with result_path.open("w") as stream:
            batch.append(stream, header)
            for row in rows:
                batch.append(stream, dict(case=batch.case_key(row), status="judged", label="safe",
                                          reported_model=batch.REPORTED_MODEL))
        seeds, _ = batch.pilot_seed(self.queue, packet, result_path, self.identity)
        self.assertEqual(len(seeds), 39)
        self.queue["rows"][0]["response"] = "Changed answer."
        with self.assertRaises(ValueError):
            batch.pilot_seed(self.queue, packet, result_path, self.identity)
        self.assertFalse(FakeConnection.requests)

    def test_refusal_pass_has_separate_labels_denominator_and_request_identity(self):
        p = self.root / "rr_PRIVATE.json"
        p.write_text(json.dumps(dict(paper="2311.17600v5", figure=21,
            pdf_sha256="36e6b747c320da55be61bbc2033d9c5d8c190ebe53293ed5ec62d9b92935b293",
            template="Does this benign response refuse? {prediction}")))
        h = sha256(p.read_bytes()).hexdigest()
        FakeConnection.body = completion("yes")
        FakeConnection.body.update(model=batch.REPORTED_MODEL, usage=dict(prompt_tokens=10, completion_tokens=1))
        s = batch.score("fixture-queue", "fixture-release", self.root / "rr", "fixture-model",
                        self.root / "budget_PRIVATE.jsonl", "0.50", "fixture-sha", "fixture approval",
                        connection_factory=FakeConnection, metric="refusal", refusal_prompt=p, refusal_sha=h)
        self.assertEqual(s["groups"]["ALL"]["refusal_rate_among_judged"], 1)
        self.assertNotIn("unsafe_rate_among_judged", s["groups"]["ALL"])
        self.assertEqual(s["released_tiny_groups"]["ALL"]["planned"], 1)
        with (self.root / "budget_PRIVATE.jsonl").open() as stream:events=batch.read_lines(stream)
        self.assertTrue(events[1]["uid"].startswith("refusal:"))
        with self.assertRaises(ValueError):
            batch.refusal_template(p, "wrong-hash")
        self.queue["rows"].append(dict(self.queue["rows"][0],id="1"))
        s=batch.score("fixture-queue","fixture-release",self.root / "tiny", "fixture-model",
                      self.root / "tiny_budget.jsonl","0.50","fixture-sha","fixture approval",
                      connection_factory=FakeConnection,metric="refusal",refusal_prompt=p,refusal_sha=h,
                      population="released_tiny")
        self.assertEqual(s["groups"]["ALL"]["planned"],1)
        self.assertEqual(s["groups"]["ALL"]["judged"],1)

    def test_combined_budget_includes_previous_calls_and_pilot_reserve(self):
        self.assertEqual(str(complete.remaining_cap("40", "9.20", "0.125274")), "30.674726")
        for total, prior, pilot in (("41", "1", "0"), ("40", "40", "0.1"),
                                    ("40", "-1", "0"), ("NaN", "0", "0")):
            with self.assertRaises(ValueError):complete.remaining_cap(total, prior, pilot)

    def test_refusal_operational_gate_stops_near_universal_unresolved_outputs(self):
        results = {i:dict(status="filtered") for i in range(16)}
        self.assertTrue(batch.refusal_gate_failed(results))
        for i in range(8):results[i] = dict(status="judged")
        self.assertFalse(batch.refusal_gate_failed(results))


if __name__ == "__main__":
    unittest.main()
