# *** -------
# Approved full-generation continuation; append after the benign smoke and export helpers.
import inspect
import time
from contextlib import nullcontext

FULL_TRACK = "__TRACK__"
FULL_GPU_MINUTES = 105  # Owner approved 210 total minutes, split equally between two models.
FULL_APPROVAL = "Owner approved 210 combined GPU minutes for LLaVA and InstructBLIP full runs; 105 each"
FULL_MANIFEST_SHA = "22044115d3fcca0d50fb87c44a6f8b845d75bbe0f7ddc67c7ba8bbadd2ebf162"
FULL_IMAGE_SHA = "e3de9b42b0ba143db82643f14d06aba534d4b1dda8b55f9b1b25a91797c7733c"


def verified_smoke(root, expected_model):
    for directory in [root.with_name(root.name + "_Smoke"),
                      *root.parent.glob(root.name + "_Smoke_retry_*")]:
        if not (directory / "aggregate.json").is_file():
            continue
        status = json.loads((directory / "aggregate.json").read_text())
        if (status.get("status") != "completed_unscored"
                or status.get("completed") != 4 or status.get("planned") != 4
                or status.get("failures") != 0 or not status.get("smoke")
                or status.get("placement") != "fp16_auto_10gib_v1"
                or status.get("model", status.get("checkpoint")) != expected_model):
            continue
        rows = [json.loads(line) for line in
                (directory / "responses_PRIVATE.jsonl").read_text().splitlines()]
        if (len(rows) == 4 and {r["variant"] for r in rows} == set(FIELDS)
                and all(isinstance(r.get("response"), str) and r["response"].strip()
                        for r in rows)):
            return directory
    raise RuntimeError("The four-condition smoke must finish successfully before full generation")


def run_approved_full():
    import sys
    full_root = (OUT if FULL_TRACK == "llava" else
                 RUNS / "MM_SafetyBench_instructblip_PRIVATE")
    model_identity = LLAVA_MODEL if FULL_TRACK == "llava" else MODEL_ID
    smoke_root = verified_smoke(full_root, model_identity)
    smoke_status = json.loads((smoke_root / "aggregate.json").read_text())
    if (len(cases) != 6720 or manifest_hash(cases) != FULL_MANIFEST_SHA
            or image_sha != FULL_IMAGE_SHA):
        raise RuntimeError("The approved 6,720-case input manifest or image fingerprint differs")
    import shutil
    from datetime import datetime, timezone
    budget_path = RUNS / f"{FULL_TRACK}_full_budget_PRIVATE.json"
    if not budget_path.exists():
        previous_starts = []
        for folder in (RUNS / "Snapshots_PRIVATE").glob(FULL_TRACK + "_*"):
            try:
                previous_starts.append(datetime.strptime(
                    folder.name[len(FULL_TRACK) + 1:], "%Y%m%dT%H%M%S%fZ"
                ).replace(tzinfo=timezone.utc).timestamp())
            except ValueError:
                continue
        # Include setup performed after the successful smoke, before this cell.
        began = min(previous_starts, default=min(
            time.time(), (smoke_root / "aggregate.json").stat().st_mtime))
        with budget_path.open("x") as stream:
            json.dump(dict(approval=FULL_APPROVAL, started_epoch=began,
                           deadline_epoch=began + FULL_GPU_MINUTES * 60), stream)
    budget = json.loads(budget_path.read_text())
    remaining_budget = min(FULL_GPU_MINUTES * 60, budget["deadline_epoch"] - time.time())
    if remaining_budget <= 0:
        raise RuntimeError("The original full-run cap has elapsed; do not reset its budget file")
    notebook_name = ("mm_safetybench_llava_7b_run_all.ipynb" if FULL_TRACK == "llava"
                     else "mm_safetybench_instructblip_run_all.ipynb")
    source_notebook = RUNS / notebook_name
    if not source_notebook.is_file():
        raise RuntimeError("Save this notebook with outputs in Runs before starting the full phase")
    snapshot = RUNS / "Snapshots_PRIVATE" / (FULL_TRACK + "_" +
               datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    snapshot.mkdir(parents=True, exist_ok=False)
    shutil.copy2(source_notebook, snapshot / notebook_name)
    shutil.copy2(smoke_root / "aggregate.json", snapshot / "smoke_aggregate.json")
    print(f"Preserved notebook and smoke aggregate in {snapshot}", flush=True)
    if full_root.exists():
        status = json.loads((full_root / "aggregate.json").read_text())
        if status.get("status") == "completed_unscored":
            checked_answers(full_root, {key(row): row for row in cases},
                            expected_image_sha=FULL_IMAGE_SHA)
            print(export_judge_handoff(FULL_TRACK), flush=True)
            return
        failures = full_root / "failures_PRIVATE.jsonl"
        failure_rows = ([json.loads(line) for line in failures.read_text().splitlines()]
                        if failures.exists() else [])
        if (status.get("status") != "case_failure" or not failure_rows
                or failure_rows[-1].get("error_type") != "OutOfMemoryError"
                or status.get("manifest_sha256") != FULL_MANIFEST_SHA):
            raise RuntimeError("Preserve and review the partial run before retrying")
        archive = full_root.with_name(full_root.name + "_OOM_" +
                  datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
        full_root.rename(archive)
        print(f"Preserved OOM attempt separately: {archive}. Its answers will not be pooled.", flush=True)
    started = time.monotonic()
    deadline = started + remaining_budget
    # Release an unreachable smoke model before a child loads another copy.
    import gc
    gc.collect()
    if "torch" in sys.modules and sys.modules["torch"].cuda.is_available():
        sys.modules["torch"].cuda.empty_cache()
    payload = Path("/content") / f"mm_safetybench_{FULL_TRACK}_full_PRIVATE.json"
    payload.write_text(json.dumps(cases, ensure_ascii=False))
    interpreter = str(LLAVA_PYTHON) if FULL_TRACK == "llava" else sys.executable
    if not Path(interpreter).is_file():
        raise RuntimeError("The model's prepared interpreter is unavailable")
    settings = dict(FIELDS=FIELDS, AUTHOR_SHA=AUTHOR_SHA, TRACK=FULL_TRACK,
                    MODE="full", LLAVA_SIZE=LLAVA_SIZE, LLAVA_MODEL=LLAVA_MODEL,
                    LLAVA_COMMIT=LLAVA_COMMIT, OWNER_APPROVAL_RECORD=FULL_APPROVAL,
                    APPROVED_MANIFEST_SHA=FULL_MANIFEST_SHA, APPROVED_IMAGE_SHA=FULL_IMAGE_SHA,
                    image_sha=FULL_IMAGE_SHA, GPU_MINUTES=remaining_budget / 60,
                    MAX_NEW_TOKENS=512 if FULL_TRACK == "llava" else 256)
    if FULL_TRACK == "instructblip":
        settings.update(TRACK="instructblip", MODEL_ID=MODEL_ID)
        revision = smoke_status["revision"]
        if revision != "19103d0c5b5263c8a7891012e08573439fb6607f":
            raise RuntimeError("The InstructBLIP smoke checkpoint differs from the reviewed revision")
    else:
        revision = Path(WEIGHTS).name
        if (revision != "4481d270cc22fd5c4d1bb5df129622006ccd9234"
                or Path(CLIP_SNAPSHOT).name != "ce19dc912ca5cd21c8a653c79e251e808ccabcd1"):
            raise RuntimeError("The LLaVA/CLIP snapshots differ from the successful smoke")
    provenance = dict(model=model_identity, revision=revision, precision="float16",
                      max_new_tokens=settings["MAX_NEW_TOKENS"], do_sample=False,
                      num_beams=1, approval=FULL_APPROVAL, gpu_minutes=FULL_GPU_MINUTES,
                      smoke_source=str(smoke_root), placement="fp16_auto_10gib_v1",
                      remaining_gpu_minutes=remaining_budget / 60)
    settings["provenance"] = provenance
    worker = ("import os, re, json, subprocess, sys\nfrom pathlib import Path\n"
              "from hashlib import sha256\nfrom io import BytesIO\n"
              "from zipfile import ZipFile\nfrom contextlib import nullcontext\n")
    worker += "globals().update(" + repr(settings) + ")\n"
    paths = dict(IMAGE_DIR=IMAGE_DIR, IMAGE_ZIP=IMAGE_ZIP, OUT=full_root,
                 LLAVA_CHECKOUT=LLAVA_CHECKOUT)
    if FULL_TRACK == "llava":
        paths.update(WEIGHTS=WEIGHTS, CLIP_SNAPSHOT=CLIP_SNAPSHOT)
    for name, path in paths.items():
        worker += f"{name} = Path({str(path)!r})\n"
    worker += f"cases = json.loads(Path({str(payload)!r}).read_text())\n"
    # inspect.getsource(class) fails for classes defined in Colab's __main__.
    worker += (
        "\nclass ExtractedImages:\n"
        "    def namelist(self):\n"
        "        return sorted(p.relative_to(IMAGE_DIR).as_posix()\n"
        "                      for p in IMAGE_DIR.rglob('*.jpg') if p.is_file())\n"
        "    def read(self, name):\n"
        "        return (IMAGE_DIR / name).read_bytes()\n"
    )
    helpers = [open_images, key, manifest_hash, atomic_json,
               append_private, smoke_cases, execute]
    if FULL_TRACK == "llava":
        worker += "sys.path.insert(0, str(LLAVA_CHECKOUT))\n"
        helpers += [load_llava, generate_llava]
        invocation = "load_llava, generate_llava"
    else:
        helpers += [load_candidate, generate_candidate]
        invocation = f"lambda: load_candidate({revision!r}), generate_candidate"
    for helper in helpers:
        worker += "\n" + inspect.getsource(helper) + "\n"
    worker += ("\nimport torch, transformers\n"
               "provenance.update(torch=torch.__version__, transformers=transformers.__version__, "
               "gpu=torch.cuda.get_device_name(0), python=sys.version.split()[0])\n")
    worker += f"execute(cases, OUT, {invocation}, provenance, False)\n"
    compile(worker, "<approved full generation>", "exec")
    log_path = full_root.parent / f"{full_root.name}_runtime_PRIVATE.log"
    print(f"FULL: {FULL_TRACK}, 6,720 cases, {remaining_budget / 60:.1f} minutes remain. Saving to {full_root}", flush=True)
    print(f"Private runtime log: {log_path}", flush=True)
    try:
        with log_path.open("a") as log:
            subprocess.run([interpreter, "-u", "-c", worker], check=True,
                           env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
                           stdout=log, stderr=subprocess.STDOUT,
                           timeout=max(1, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        if (full_root / "aggregate.json").is_file():
            status = json.loads((full_root / "aggregate.json").read_text())
            ledger = full_root / "responses_PRIVATE.jsonl"
            rows = [json.loads(line) for line in ledger.read_text().splitlines()] if ledger.exists() else []
            status.update(status="budget_stop", completed=len(rows), remaining=6720 - len(rows))
            atomic_json(full_root / "aggregate.json", status)
        raise RuntimeError("Full-run time cap reached; partial answers remain in Drive") from None
    print("Full-generation process finished; verifying all case IDs.", flush=True)
    print(export_judge_handoff(FULL_TRACK), flush=True)


run_approved_full()
