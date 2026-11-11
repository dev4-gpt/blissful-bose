"""Generate four self-contained GPU-only notebooks; never start compute."""
import argparse
import ast
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
MODELS = {
    "llava": ("liuhaotian/llava-v1.5-7b", "4481d270cc22fd5c4d1bb5df129622006ccd9234", "4.37.2", "colab", "mm_safetybench_llava_7b.ipynb"),
    "instructblip": ("Salesforce/instructblip-vicuna-7b", "19103d0c5b5263c8a7891012e08573439fb6607f", "4.46.3", "colab", "mm_safetybench_instructblip_generation.ipynb"),
    "qwen_vl": ("Qwen/Qwen-VL-Chat", "f57cfbd358cb56b710d963669ad1bcfb44cdcdd8", "4.32.0", "kaggle", "mm_safetybench_qwen_vl_generation.ipynb"),
    "idefics": ("HuggingFaceM4/idefics-9b-instruct", "7065afb8a5bb03015700b315f6751dc3dd4e16eb", "4.46.3", "kaggle", "mm_safetybench_idefics_generation.ipynb"),
}
INSTRUCTBLIP_VISUAL_REFERENCE = dict(do_sample=False, num_beams=5, max_length=256, min_length=1,
                                    top_p=0.9, repetition_penalty=1.5, length_penalty=1.0, temperature=1)


def definitions(source):
    tree = ast.parse(source)
    nodes = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    return "\n\n".join(ast.get_source_segment(source, node) for node in nodes.values())


def worker_source(root, *, instructblip_reference=False, allow_no_response=False):
    base = json.loads((root / "notebooks/mm_safetybench_reproduction.ipynb").read_text())
    preflight, = ["".join(c["source"]) for c in base["cells"]
                  if c["cell_type"] == "code" and "def make_manifest(" in "".join(c["source"])]
    helpers = definitions(preflight).replace('dir="/content"', 'dir=WORK')
    # Use only author-template extraction, never the old track-specific exporter.
    judge = (root / "tools/nb_gen/mm_safetybench_judge_handoff.py").read_text()
    tree = ast.parse(judge)
    rubrics = "\n\n".join(ast.get_source_segment(judge, n) for n in tree.body
        if (isinstance(n, ast.FunctionDef) and n.name == "released_rubrics")
        or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "RELEASE_RUBRIC" for t in n.targets)))
    imports = "from collections import defaultdict\nfrom contextlib import nullcontext\nfrom zipfile import ZipFile\nimport ast\n"
    names = ("TRACK MODEL_ID REVISION MODE MAX_NEW_TOKENS DEADLINE WORK RUN_ROOT AUTHOR_ZIP IMAGE_ZIP "
             "IMAGE_DIR AUTHOR_SHA FIELDS EXPECTED_MANIFEST EXPECTED_IMAGES LLAVA_COMMIT CLIP_REVISION CODE_SHA")
    imports += "\n".join(f"{name} = None" for name in names.split()) + "\n"
    models = (root / "tools/nb_gen/mm_safetybench_portable_models.py").read_text()
    runtime = (root / "tools/nb_gen/mm_safetybench_portable_runtime.py").read_text()
    if instructblip_reference:
        # Preserve the exact worker hashes used by the existing ledgers.
        imports += f"VISUAL_GENERATION = {INSTRUCTBLIP_VISUAL_REFERENCE!r}\n"
        visual_call = "tokens = model.generate(**inputs, **settings)"
        placement_record = 'identity["placement"] = placement'
        cap_flag = "tokens >= MAX_NEW_TOKENS if tokens is not None else None"
        for template, marker in ((models, visual_call), (runtime, placement_record), (runtime, cap_flag)):
            if template.count(marker) != 1:
                raise ValueError(f"Reference notebook template changed: {marker}")
        models = models.replace(visual_call, "tokens = model.generate(**inputs, **VISUAL_GENERATION)")
        runtime = runtime.replace(placement_record, placement_record + '\n    identity["visual_generation"] = VISUAL_GENERATION')
        # The upstream example uses max_length. The greedy new-token cap applies only to text.
        runtime = runtime.replace(cap_flag,
                                  'tokens >= MAX_NEW_TOKENS if tokens is not None and case["image_path"] is None else None')
    if allow_no_response:
        if not instructblip_reference:
            raise ValueError("No-response handling is approved for the reference track")
        from mm_safetybench_no_response import with_no_response
        runtime = with_no_response(runtime)
    source = imports + helpers + "\n\n" + rubrics + "\n\n" + models + "\n\n" + runtime
    # AST formatting removes comments/blank lines without altering literal contents.
    return "\n".join(line for line in ast.unparse(ast.parse(source)).splitlines() if line.strip()) + "\n"


LAUNCHER = r'''
import os, json, subprocess, sys, time, shutil, hashlib, zipfile
from pathlib import Path

def launch():
    if MODE not in {"smoke", "pilot", "full", "export"}:
        raise ValueError("Choose smoke, pilot, full, or export")
    for path in (AUTHOR_ZIP, IMAGE_ZIP):
        if not Path(path).is_file():
            raise FileNotFoundError(f"Attach the released input file: {path}")
    work = Path("/content/mm_gpu_only") if PLATFORM == "colab" else Path("/kaggle/working/mm_gpu_only_PRIVATE")
    work.mkdir(parents=True, exist_ok=True)
    root = Path(OUTPUT_ROOT) / TRACK / RUN_ID
    root.mkdir(parents=True, exist_ok=True)
    worker = work / f"{TRACK}_worker_PRIVATE.py"
    worker.write_text(WORKER_SOURCE)
    gpu_rows = []
    if MODE != "export":
        if not APPROVAL_RECORD or not ALLOCATION_ID or not (EXISTING_QUOTA_ONLY and GPU_MINUTES is None or GPU_MINUTES is not None and GPU_MINUTES > 0):
            raise RuntimeError("New GPU budget required: set APPROVAL_RECORD, ALLOCATION_ID and GPU_MINUTES. The old 210-minute allocation is exhausted.")
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.free", "--format=csv,noheader,nounits"],
                                check=True, capture_output=True, text=True)
        gpu_rows = [line.rsplit(",", 1) for line in result.stdout.strip().splitlines()]
        print("Assigned GPUs:", gpu_rows)
        usable = sum(max(0, int(free) - 3072) for _, free in gpu_rows)
        required = {"llava": 14, "instructblip": 16, "idefics": 18, "qwen_vl": 20}[TRACK] * 1024
        if usable < required:
            raise RuntimeError("GPU-only FP16 estimate does not fit with activation reserve. Choose a larger GPU or T4 ×2. No downloads started.")
        allocation_path = root / "allocations_PRIVATE" / (hashlib.sha256(ALLOCATION_ID.encode()).hexdigest() + ".json")
        allocation_path.parent.mkdir(parents=True, exist_ok=True)
        specification = dict(record=APPROVAL_RECORD, gpu_minutes=GPU_MINUTES, gpu_count=len(gpu_rows))
        if allocation_path.exists():
            allocation = json.loads(allocation_path.read_text())
            if allocation["specification"] != specification:
                raise ValueError("Existing allocation cannot be changed/reset. Record a separately approved new allocation ID.")
        else:
            allocation = dict(specification=specification, deadline=None if GPU_MINUTES is None else time.time() + 60 * GPU_MINUTES / len(gpu_rows))
            with allocation_path.open("x") as stream:
                json.dump(allocation, stream)
        deadline = allocation["deadline"]
    else:
        deadline = time.time() + 600  # CPU-only export; no model download or generation.
    def call(command):
        remaining = None if deadline is None else deadline - time.time()
        if remaining is not None and remaining <= 0:
            raise TimeoutError("Approved allocation elapsed; saved answers remain intact")
        log = root / "runtime_PRIVATE.log"
        print("Running:", Path(command[0]).name, "— private log:", log, flush=True)
        try:
            with log.open("ab") as stream:
                subprocess.run(command, check=True, timeout=remaining, stdout=stream, stderr=subprocess.STDOUT,
                               env={**os.environ, "MPLBACKEND": "Agg"})
        except subprocess.CalledProcessError:
            print("Failure detail (private notebook):\n", log.read_text(errors="replace")[-3500:], flush=True)
            raise
    environment = work / f"env_{TRACK}_311"
    python = environment / "bin/python"
    if MODE == "export":
        python = Path(sys.executable)
    elif not (environment / ".ready_v1").exists():
        uv = shutil.which("uv")
        if not uv:
            call([sys.executable, "-m", "pip", "install", "uv==0.9.5"])
            uv = shutil.which("uv")
        if not uv:
            raise RuntimeError("uv installation failed")
        if not python.is_file():
            call([uv, "venv", "--python", "3.11", str(environment)])
        pip = [uv, "pip", "install", "--python", str(python)]
        call([*pip, "--index-url", "https://download.pytorch.org/whl/cu124", "torch==2.6.0", "torchvision==0.21.0"])
        packages = [f"transformers=={TRANSFORMERS_VERSION}", "accelerate==0.27.2", "huggingface-hub==0.36.2",
                    "numpy==1.26.4", "sentencepiece==0.1.99", "protobuf==4.25.3", "Pillow==10.4.0",
                    "shortuuid==1.0.13", "einops==0.8.0", "requests==2.32.3", "safetensors==0.4.5"]
        if TRACK == "qwen_vl":
            packages += ["tiktoken==0.7.0", "transformers-stream-generator==0.0.5", "matplotlib==3.9.2"]
        call([*pip, *packages])
        (environment / ".ready_v1").touch()
    config = dict(TRACK=TRACK, MODEL_ID=MODEL_ID, REVISION=REVISION, MODE=MODE,
                  MAX_NEW_TOKENS=MAX_NEW_TOKENS, DEADLINE=deadline, WORK=str(work), RUN_ROOT=str(root),
                  AUTHOR_ZIP=AUTHOR_ZIP, IMAGE_ZIP=IMAGE_ZIP, IMAGE_DIR=str(work / "images"),
                  AUTHOR_SHA=AUTHOR_SHA, FIELDS=FIELDS, EXPECTED_MANIFEST=EXPECTED_MANIFEST,
                  EXPECTED_IMAGES=EXPECTED_IMAGES, LLAVA_COMMIT=LLAVA_COMMIT, CLIP_REVISION=CLIP_REVISION,
                  CODE_SHA=hashlib.sha256(WORKER_SOURCE.encode()).hexdigest())
    config_path = work / f"{TRACK}_config_PRIVATE.json"
    config_path.write_text(json.dumps(config))
    try:
        call([str(python), "-u", str(worker), str(config_path)])
    except subprocess.TimeoutExpired:
        # The parent enforces the deadline even during downloads, model load or a single long answer.
        aggregate_path = root / "benchmark/aggregate.json"
        if aggregate_path.exists():
            aggregate = json.loads(aggregate_path.read_text())
            aggregate["status"] = "budget_stop"
            aggregate_path.write_text(json.dumps(aggregate, indent=2))
        raise RuntimeError("Budget elapsed. Partial answers are saved; generation is not complete.")
    finally:
        # Always retain code, config and a portable private result bundle, including partial runs.
        shutil.copy2(worker, root / "worker_PRIVATE.py")
        shutil.copy2(config_path, root / "launch_PRIVATE.json")
        bundle = root.parent / (RUN_ID + "_PRIVATE.zip")
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in root.rglob("*"):
                if file.is_file():
                    archive.write(file, file.relative_to(root))
        print("Saved run:", root, "\nPrivate recovery bundle:", bundle)
        if PLATFORM == "kaggle":
            print("Before ending the Kaggle session: save notebook version WITH outputs privately or download the PRIVATE.zip. /kaggle/working alone is not permanent storage.")

def launch_locked():
    import fcntl
    if PLATFORM == "colab":
        from google.colab import drive
        # Mount before creating any folders/lock files under Drive. The dedicated
        # location avoids the orphaned local folders left by the older launch order.
        mountpoint = "/content/mm_safetybench_drive"
        drive.mount(mountpoint)
        for name in ("AUTHOR_ZIP", "IMAGE_ZIP", "OUTPUT_ROOT"):
            globals()[name] = globals()[name].replace("/content/drive/MyDrive", mountpoint + "/MyDrive", 1)
    root = Path(OUTPUT_ROOT) / TRACK / RUN_ID
    root.mkdir(parents=True, exist_ok=True)
    with (root / "writer_PRIVATE.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("This run already has a writer. Do not run two sessions against the same ledger.")
        launch()

if RUN_GENERATION:
    launch_locked()
'''


def build(root=ROOT, *, instructblip_reference=False, allow_no_response=False):
    source = worker_source(root, instructblip_reference=instructblip_reference, allow_no_response=allow_no_response)
    compile(source, "portable worker", "exec")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    archive = root / "audit_work" / "portable_notebook_snapshots_PRIVATE" / stamp
    archive.mkdir(parents=True)
    checksums = {}
    tracks = ("instructblip",) if instructblip_reference else MODELS
    for track in tracks:
        model, revision, version, platform, filename = MODELS[track]
        if instructblip_reference:
            filename = "mm_safetybench_instructblip_reference.ipynb"
        path = root / "notebooks" / filename
        if path.exists():
            shutil.copy2(path, archive / filename)
            checksums[filename] = sha256(path.read_bytes()).hexdigest()
        private = "/content/drive/MyDrive/MM_SafetyBench_Full_20261102_PRIVATE" if platform == "colab" else "/kaggle/input/datasets/aryamandev/mm-safetybench-private"
        output = private + "/Runs/GPU_Only_PRIVATE" if platform == "colab" else "/kaggle/working/Runs_PRIVATE"
        config = dict(TRACK=track, PLATFORM=platform, MODEL_ID=model, REVISION=revision,
                      TRANSFORMERS_VERSION=version, MODE="full", RUN_GENERATION=True,
                      RUN_ID="gpu_only_v1", APPROVAL_RECORD="Owner approved 2026-11-05: run four notebooks until completion or platform/error stop within existing quota only; no purchases/top-ups",
                      ALLOCATION_ID="owner_existing_quota_20261105", GPU_MINUTES=None, EXISTING_QUOTA_ONLY=True,
                      AUTHOR_ZIP=private + "/MM-SafetyBench-main.zip" + (".bin" if platform == "kaggle" else ""),
                      IMAGE_ZIP=private + "/MM-SafetyBench(imgs).zip" + (".bin" if platform == "kaggle" else ""),
                      OUTPUT_ROOT=output, MAX_NEW_TOKENS=512 if track == "llava" else 256,
                      AUTHOR_SHA="801a891382a06b7c3b29083dd3844b6da6a3e0ef31d3dfdd9086e30b323f322b",
                      EXPECTED_MANIFEST="22044115d3fcca0d50fb87c44a6f8b845d75bbe0f7ddc67c7ba8bbadd2ebf162",
                      EXPECTED_IMAGES="e3de9b42b0ba143db82643f14d06aba534d4b1dda8b55f9b1b25a91797c7733c",
                      LLAVA_COMMIT="c121f0432da27facab705978f83c4ada465e46fd",
                      CLIP_REVISION="ce19dc912ca5cd21c8a653c79e251e808ccabcd1",
                      FIELDS={"TEXT": "Question", "SD": "Rephrased Question(SD)", "TYPO": "Rephrased Question", "SD_TYPO": "Rephrased Question"})
        intro = f"""# MM-SafetyBench — {model} — {platform.title()}

One notebook: environment → input verification → unchanged upstream FP16 inference → four benign routing cases → 52-case timing pilot (13 scenarios × four conditions) → remaining benchmark answers → Azure-ready export. **GPU behavior is not yet validated for this new configuration.** No training or Azure calls.

The owner approved running these four notebooks **until completion or a platform/error stop using existing quota only**, with no purchases or top-ups, on 5 November 2026. No software time cap is applied (`GPU_MINUTES=None`). Full mode includes smoke and pilot automatically; pilot timing is reported rather than used as a time gate. Optional finite allocations still retain immutable deadlines. Platform session/quota limits remain in force.

{('Colab: select a GPU with enough FP16 memory; mounting Drive requires your click. Existing partial runs stay untouched.' if platform == 'colab' else 'Kaggle: use a PRIVATE notebook, Internet enabled and T4 ×2. Attach the authors’ original ZIP bytes as private inputs; the .zip.bin filename suffix prevents Kaggle from auto-extracting them and does not change their checksums. Set exact paths below. Save notebook versions WITH outputs privately or download the recovery ZIP before ending the session. To resume a later session, extract that saved run folder under OUTPUT_ROOT first.')}

Authors provide the benchmark data and scoring rubrics; model authors provide the checkpoints/processors. We provide orchestration, adapters, validation, timing and private ledgers. Reference: [paper v5](https://arxiv.org/html/2311.17600v5), [pinned benchmark release](https://github.com/isXinLiu/MM-SafetyBench/tree/b80eedea3db312c09ded2082813390f68e750ef3), [pinned model](https://huggingface.co/{model}/tree/{revision}).

Four conditions each contain 1,680 questions: TEXT, SD, TYPO, SD_TYPO (6,720 answers total). SD images are reused, not regenerated. TYPO uses the release README's `Rephrased Question`, which differs from the paper Section 3.2 description. Historical model/code revisions, precision and decoding settings are not fully recovered: these are pinned reproduction candidates, not exact reproductions. FP16, greedy, batch one and the configured token cap are declared choices; upstream image preprocessing is retained. Text-only for InstructBLIP uses its embedded LLM without visual conditioning and is an additional baseline where absent from the reported experiment. Modern Python 3.11/PyTorch 2.6 compatibility environments are declared deviations. Qwen custom Python code runs only from the pinned upstream snapshot; FlashAttention is disabled explicitly for T4 compatibility. No quantization or CPU/disk fallback.
"""
        config_notes = ("Existing-quota-only execution without a software time cap is approved and recorded below. "
                        "Verify platform input paths. Keep RUN_ID when resuming identical work; use a new RUN_ID "
                        "for changed inference settings. No purchases, top-ups or paid judge calls are performed.")
        if instructblip_reference:
            config.update(MODE="pilot", RUN_GENERATION=False, RUN_ID="instructblip_documented_visual_v1",
                          APPROVAL_RECORD="", ALLOCATION_ID="", EXISTING_QUOTA_ONLY=False)
            intro = """# MM-SafetyBench — InstructBLIP documented visual decoding

This Colab notebook uses the same released checkpoint and benchmark inputs. Image cases use the
[Transformers 4.46.3 generation example](https://github.com/huggingface/transformers/blob/v4.46.3/src/transformers/models/instructblip/modeling_instructblip.py#L1257-L1269).
Text-only uses the same embedded language model with greedy decoding and a 256 new-token cap.
The visual decoding settings returned a nonempty answer on the typography case that stopped
the greedy run. The full 52-case pilot and the remaining cases have yet to be tested.
The pinned benchmark release supplies the questions and images for 13 scenarios and four conditions.
The runner stops on empty answers and saves nonempty answers to a distinct run directory.
The historical MM-SafetyBench InstructBLIP decoding settings are unverified.
"""
            config_notes = ("Record the approved allocation in the configuration. Enable RUN_GENERATION "
                            "to run the four benign routing checks and 52-case pilot on a GPU with FP16 capacity. "
                            "After verifying the pilot, full mode resumes from its verified answers. "
                            "Keep RUN_ID and the generation settings fixed when resuming.")
            if allow_no_response:
                config.update(RUN_ID="instructblip_documented_outcomes_v1", RUN_GENERATION=True, MODE="full",
                              APPROVAL_RECORD="Owner approved recording no_response and continuing within existing quota on 7 November 2026.",
                              ALLOCATION_ID="amendment22_instructblip_existing_quota", EXISTING_QUOTA_ONLY=True)
                intro = intro.replace(
                    "The runner stops on empty answers and saves nonempty answers to a distinct run directory.",
                    "The runner saves each completed benchmark outcome, including empty decoded completions.")
                config_notes = ("Run all to resume the approved generation within existing quota. "
                                "The four benign smoke cases precede the 52-case pilot and full generation. "
                                "Progress reports nonempty answers and no_response outcomes separately.")
                intro += ("\nCompleted empty benchmark generations are saved with response_status=no_response. "
                          "Benign smoke checks still require nonempty answers. Coverage includes all generation outcomes. "
                          "The Azure queue contains nonempty answers and a separate list of no_response case IDs. "
                          "Matching answers from the previous reference run are imported with explicit provenance.\n")
        def cell(kind, text):
            value = dict(cell_type=kind, id=sha256((track + kind + text).encode()).hexdigest()[:12],
                         metadata={}, source=text.splitlines(True))
            if kind == "code":
                value.update(execution_count=None, outputs=[])
            return value
        cfg = "# *** -------\n" + "\n".join(f"{k} = {v!r}" for k, v in config.items())
        cells = [cell("markdown", intro), cell("markdown", "## Configuration\n" + config_notes),
                 cell("code", cfg), cell("markdown", "## Self-contained inference implementation\nThe following embedded worker is written to the VM and executed in an isolated Python environment. It contains all data, model and output code; no project repository checkout is needed."),
                 cell("code", "# *** -------\nWORKER_SOURCE = " + repr(source)),
                 cell("markdown", "## Run sequential stages for this model\nProgress shows counts, not private replies. Any failure stops generation; valid answers remain saved. A CPU/disk/meta placement, malformed image tensor, empty answer, source mismatch or insufficient budget stops the run. Existing answers are not rerun. Different models can run in parallel in separate approved sessions."),
                 cell("code", "# *** -------\n" + LAUNCHER),
                 cell("markdown", "## Read the result before closing\n`completed_unscored` with 6,720 verified answers and `Judge_Handoff_PRIVATE/queue_PRIVATE.json` means ready for judging, not measured ASR. Other statuses are partial. The pilot records condition-specific timing evidence and estimated remaining duration. Safety ASR and refusal must be judged separately using the released scenario safety templates and the paper’s Figure 21 refusal rubric. No scores are inferred here. For offline export use MODE='export'; it does not load a model or require a GPU budget. Keep every response and recovery bundle private."),
                 cell("code", "# *** -------\nrun = Path(OUTPUT_ROOT) / TRACK / RUN_ID\nfor relative in ('smoke/aggregate.json', 'pilot_PRIVATE.json', 'benchmark/aggregate.json'):\n    file = run / relative\n    print(relative, json.loads(file.read_text()) if file.is_file() else 'Not available')\nqueue = run / 'benchmark/Judge_Handoff_PRIVATE/queue_PRIVATE.json'\nprint('Azure queue exists:', queue.is_file())")]
        if allow_no_response:
            cells[5] = cell("markdown", "## Run the generation stages\nCompleted blank outputs are recorded as "
                            "no_response and included in case coverage. Runtime errors stop the worker. "
                            "Smoke checks require nonempty answers. Each completed outcome is saved immediately.")
            cells[7] = cell("markdown", "## Read the result before closing\nA completed_unscored status with "
                            "6,720 unique outcomes means every case completed generation. The aggregate reports "
                            "nonempty_answers and no_response separately. The Azure queue contains the nonempty "
                            "answers and a separate no_response_cases inventory. Report both counts alongside "
                            "judging results and retain the full 6,720-case denominator when reporting coverage. "
                            "No-response outcomes have no automatic safety or refusal label.")
        nb = dict(cells=cells, nbformat=4, nbformat_minor=5,
                  metadata=dict(kernelspec=dict(display_name="Python 3", language="python", name="python3")))
        # Compact JSON keeps generated notebook files below the repository's 500-line limit.
        path.write_text(json.dumps(nb, ensure_ascii=False) + "\n")
    (archive / "checksums_PRIVATE.json").write_text(json.dumps(checksums, indent=2))
    print("Preserved previous notebook versions:", archive)
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instructblip-reference", action="store_true",
                        help="Generate only the separate notebook with documented visual decoding.")
    parser.add_argument("--allow-no-response", action="store_true",
                        help="Record empty benchmark completions in the approved reference track.")
    args = parser.parse_args()
    build(instructblip_reference=args.instructblip_reference, allow_no_response=args.allow_no_response)
