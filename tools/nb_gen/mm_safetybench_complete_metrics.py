"""Complete approved ASR/RR stages after the existing safety pass; no extra inference."""
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import time

import mm_safetybench_azure_batch as batch
from mm_safetybench_metric_report import report

REFUSAL_SHA = "d65e2baa4e04e9ec1ddd5af12bfb3745a7f153ecae48236459f242af6b95117a"
APPROVAL = ("Owner approved up to USD 40 total for required ASR and RR evaluation of "
            "Qwen2.5-VL-3B, InstructBLIP Vicuna-7B and LLaVA-1.5-7B; existing credit only; "
            "reuse prior outcomes; no purchases/top-ups; ask before any increase.")


def remaining_cap(total, prior, pilot_reserve):
    values = [Decimal(str(v)) for v in (total, prior, pilot_reserve)]
    if any(not x.is_finite() for x in values) or not 0 < values[0] <= 40 or min(values[1:]) < 0:
        raise ValueError("Invalid approved total/prior cost")
    cap = values[0] - values[1] - values[2]
    if cap <= 0:
        raise ValueError("Approved total is exhausted; no new calls")
    return cap


def atomic(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2))
    temp.replace(path)


def state(root, status, **values):
    value = dict(status=status, updated_utc=datetime.now(timezone.utc).isoformat(), **values)
    atomic(root / "pipeline_state_PRIVATE.json", value)
    print(value, flush=True)


def completed_safety(first):
    counts = {"qwen25": 6720, "instructblip": 5922}
    for name, n in counts.items():
        p = first / name / "aggregate_PRIVATE.json"
        if not p.exists():
            return False
        s = json.loads(p.read_text())
        if s["status"] != "completed_with_possible_unresolved":
            return False
        with (first / name / "judgments_PRIVATE.jsonl").open() as stream:
            rows = batch.read_lines(stream)
        if len(rows) - 1 != n or len({tuple(x["case"]) for x in rows[1:]}) != n:
            raise ValueError("First-stage coverage differs; preserve and inspect")
    return True


def run(base, key_file):
    base, key_file = Path(base), Path(key_file)
    prep = base / "Runs/Judge_Handoff_PRIVATE/Azure_Preparation_20261108T153750Z_PRIVATE"
    root, first = prep / "Full_Metrics_20261108_PRIVATE", prep / "Full_Safety_20261108_PRIVATE"
    root.mkdir(parents=True, exist_ok=True)
    author = base / "MM-SafetyBench-main.zip"
    config = dict(host="mm-safetybench-judge-20261108.openai.azure.com",
                  deployment="mm-safetybench-gpt41-20250414", version=batch.MODEL_VERSION)
    os.environ.update(AZURE_OPENAI_ENDPOINT="https://" + config["host"] + "/",
                      AZURE_OPENAI_DEPLOYMENT=config["deployment"],
                      AZURE_OPENAI_MODEL_VERSION=config["version"])
    try:
        os.environ["AZURE_OPENAI_API_KEY"] = key_file.read_text().strip()
        key_file.unlink()
        batch.refusal_template(root / "refusal_figure21_PRIVATE.json", REFUSAL_SHA)
        state(root, "waiting_for_existing_safety_pass", total_cap_usd="40", requests_sent_by_this_stage=0)
        while not completed_safety(first):
            time.sleep(30)
        # Acquire the first stage's lock before fixing its final spend. The
        # first worker has no unattempted cases and never retries saved outcomes.
        while True:
            try:
                old = batch.CreditLedger(first / "credit_ledger_PRIVATE.jsonl", "20", config)
                break
            except BlockingIOError:
                time.sleep(1)
        try:
            prior = old.used
            prior_sha = sha256((first / "credit_ledger_PRIVATE.jsonl").read_bytes()).hexdigest()
        finally:
            old.close()
        pilot = json.loads((prep / "pilot_cost_reserve_PRIVATE.json").read_text())
        cap = remaining_cap("40", prior, pilot["reserved_usd"])
        allocation = dict(total_cap_usd="40", first_stage_cost_or_reservations_usd=str(prior),
                          first_stage_ledger_sha256=prior_sha, pilot_reserve_usd=pilot["reserved_usd"],
                          remaining_stage_cap_usd=str(cap), approval=APPROVAL)
        allocation_path = root / "budget_allocation_PRIVATE.json"
        if allocation_path.exists() and json.loads(allocation_path.read_text()) != allocation:
            raise ValueError("Prior spend/allocation changed; no budget reset")
        atomic(allocation_path, allocation)
        budget = root / "credit_ledger_PRIVATE.jsonl"
        qwen = base / "Runs/Judge_Handoff_PRIVATE/qwen_all/queue_PRIVATE.json"
        instruct = base / ("Runs/GPU_Only_PRIVATE (1)/instructblip/"
                           "instructblip_documented_outcomes_v1/benchmark/Judge_Handoff_PRIVATE/queue_PRIVATE.json")
        tasks = [("qwen25", qwen, "Qwen/Qwen2.5-VL-3B-Instruct"),
                 ("instructblip", instruct, "Salesforce/instructblip-vicuna-7b")]
        for name, queue, model in tasks:
            _, digest = batch.validate_queue(queue, author, model)
            with (first / name / "judgments_PRIVATE.jsonl").open() as stream:
                previous = json.loads(stream.readline())
            if (previous["queue_sha256"] != digest or previous["model_key"] != model
                    or previous["judge"] != config):
                raise ValueError("Queue/model/judge differs from the scored safety pass")
            state(root, "judging_refusal", model=name, stage_cap_usd=str(cap))
            result = batch.score(queue, author, root / name / "refusal", model, budget, cap,
                                 digest, APPROVAL, metric="refusal",
                                 refusal_prompt=root / "refusal_figure21_PRIVATE.json", refusal_sha=REFUSAL_SHA)
            report(queue, author, first / name / "judgments_PRIVATE.jsonl",
                   root / name / "refusal/judgments_PRIVATE.jsonl", root / name / "Results_PRIVATE")
            if result["status"] != "completed_with_possible_unresolved":
                state(root, "stopped_for_review", model=name, reason=result["status"])
                return
        llava_root = base / "Runs/GPU_Only_PRIVATE (1)/llava/gpu_only_v1/benchmark"
        queue = llava_root / "Judge_Handoff_PRIVATE/queue_PRIVATE.json"
        state(root, "waiting_for_llava_generation", stage_cap_usd=str(cap))
        while True:
            if queue.exists():
                s = json.loads((llava_root / "aggregate.json").read_text())
                if s.get("status") == "completed_unscored" and s.get("completed") == 6720 and s.get("remaining") == 0:
                    break
            time.sleep(30)
        model = "liuhaotian/llava-v1.5-7b"
        q, digest = batch.validate_queue(queue, author, model)
        if len(q["rows"]) != 6720 or q.get("no_response_cases"):
            raise ValueError("Expected 6,720 nonempty LLaVA answers")
        identity = json.loads((llava_root / "identity_PRIVATE.json").read_text())
        if (q.get("identity") != identity or identity.get("model") != model
                or identity.get("revision") != "4481d270cc22fd5c4d1bb5df129622006ccd9234"
                or q.get("response_sha256") != sha256((llava_root / "responses_PRIVATE.jsonl").read_bytes()).hexdigest()):
            raise ValueError("LLaVA queue and verified generation provenance differ")
        for metric in ("safety", "refusal"):
            state(root, "judging_llava", metric=metric, stage_cap_usd=str(cap))
            kwargs = dict(metric=metric)
            if metric == "refusal":
                kwargs.update(refusal_prompt=root / "refusal_figure21_PRIVATE.json", refusal_sha=REFUSAL_SHA)
            result = batch.score(queue, author, root / "llava" / metric, model, budget, cap,
                                 digest, APPROVAL, **kwargs)
            if result["status"] != "completed_with_possible_unresolved":
                state(root, "stopped_for_review", model="llava", metric=metric, reason=result["status"])
                return
        report(queue, author, root / "llava/safety/judgments_PRIVATE.jsonl",
               root / "llava/refusal/judgments_PRIVATE.jsonl", root / "llava/Results_PRIVATE")
        state(root, "all_three_evaluation_passes_completed_with_unresolved_inventory",
              total_cap_usd="40", exact_historical_reproduction=False,
              result_note="GPT-4.1-labelled ASR/RR; no-response and filtered cases remain unresolved.")
    except BaseException as exc:
        state(root, "interrupted_or_error", error_type=type(exc).__name__)
        raise
    finally:
        os.environ.pop("AZURE_OPENAI_API_KEY", None)
        key_file.unlink(missing_ok=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("private_base", type=Path)
    p.add_argument("--key-file", type=Path, required=True)
    a = p.parse_args()
    run(a.private_base, a.key_file)
