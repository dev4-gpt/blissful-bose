def qwen_text_cases(root):
    expected, _ = read_saved_qwen(root)
    cases = []
    with ZipFile(root / AUTHOR_ZIP.name) as author:
        for name in sorted(author.namelist()):
            path = Path(name)
            if path.parent.name != "processed_questions" or path.suffix != ".json":
                continue
            for item, fields in json.loads(author.read(name)).items():
                question = fields["Question"]
                if not isinstance(question, str) or not question.strip():
                    raise ValueError("Invalid original question")
                cases.append(dict(scenario=path.stem, id=item, variant="TEXT",
                                  field="Question", question=question))
    keys = {(row["scenario"], row["id"], carrier) for row in cases
            for carrier in ("SD", "TYPO", "SD_TYPO")}
    if len(cases) != 1680 or len({row["scenario"] for row in cases}) != 13 or keys != expected.keys():
        raise ValueError("Text baseline does not match saved image case IDs")
    return cases


def run_qwen_text(rows):
    import time

    from huggingface_hub import snapshot_download, try_to_load_from_cache

    model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
    revision = "66285546d2b821cf421d4f5eb2576359d3770cd3"
    manifest_sha = manifest_hash(rows)
    unlimited = globals().get("QWEN_TEXT_EXISTING_QUOTA_ONLY", False) and GPU_MINUTES is None
    if not (OWNER_APPROVAL_RECORD and (unlimited or GPU_MINUTES and GPU_MINUTES > 0)
            and APPROVED_MANIFEST_SHA == manifest_sha):
        raise RuntimeError("Approval, GPU minutes, and the frozen manifest hash are required")

    import torch
    import transformers
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    previous = json.loads((PRIVATE / "aggregate.json").read_text())
    if (torch.__version__ != previous["torch"]
            or transformers.__version__ != previous["transformers"]
            or not torch.cuda.is_available() or "T4" not in torch.cuda.get_device_name(0)):
        raise RuntimeError("The archived T4 software configuration is required")
    deadline = float("inf") if unlimited else time.monotonic() + GPU_MINUTES * 60
    mode = "smoke" if QWEN_TEXT_SMOKE else "full"
    if QWEN_TEXT_SMOKE:
        rows = [dict(scenario="benign_smoke", id="1", variant="TEXT", field="Question",
                     question="Name two colors found in a rainbow.")]
    suffix = "_Smoke" if QWEN_TEXT_SMOKE else ""
    out = RUNS / f"MM_SafetyBench_Qwen25_Text{suffix}_Private"
    out.mkdir(parents=True, exist_ok=True)
    status = dict(model=model_id, revision=revision, torch=previous["torch"],
                  transformers=previous["transformers"], precision="float16",
                  max_new_tokens=256, do_sample=False, planned=len(rows),
                  completed=0, failures=0, status="running", approval=OWNER_APPROVAL_RECORD,
                  manifest_sha256=manifest_sha, mode=mode)
    identity_fields = ("model", "revision", "torch", "transformers", "precision",
                       "max_new_tokens", "do_sample", "manifest_sha256", "mode", "planned")
    aggregate_path = out / "aggregate.json"
    if aggregate_path.exists():
        saved = json.loads(aggregate_path.read_text())
        if any(saved.get(name) != status[name] for name in identity_fields):
            raise ValueError("Existing text run has a different configuration")
    elif any(out.iterdir()):
        raise ValueError("Existing text run has no configuration record")
    expected = {(row["scenario"], row["id"], row["variant"]): row for row in rows}
    completed = set()
    ledger = out / "responses_PRIVATE.jsonl"
    if ledger.exists():
        raw = ledger.read_bytes()
        boundary = raw.rfind(b"\n") + 1
        if boundary != len(raw):
            from datetime import datetime, timezone
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            ledger.with_name(f"interrupted_tail_{stamp}_PRIVATE.bin").write_bytes(raw[boundary:])
            with ledger.open("r+b") as stream:
                stream.truncate(boundary)
        for line in raw[:boundary].splitlines():
            record = json.loads(line)
            key = tuple(record[name] for name in ("scenario", "id", "variant"))
            if (key not in expected or key in completed
                    or record.get("field") != expected[key]["field"]
                    or not isinstance(record.get("response"), str) or not record["response"].strip()):
                raise ValueError("Invalid or duplicate saved text answer")
            completed.add(key)
    status["completed"] = len(completed)
    atomic_json(out / "aggregate.json", status)
    if len(completed) == len(rows):
        status.update(status="completed_unscored", remaining=0)
        atomic_json(aggregate_path, status)
        print("All text answers already saved.")
        return
    try:
        print(f"Qwen {mode}: preparing the pinned checkpoint.", flush=True)
        if QWEN_TEXT_SNAPSHOT:
            snapshot = Path(QWEN_TEXT_SNAPSHOT).resolve()
            cached = try_to_load_from_cache(model_id, "config.json", revision=revision)
            if not isinstance(cached, str) or Path(cached).parent.resolve() != snapshot:
                raise RuntimeError("Snapshot does not match the archived Qwen revision")
        else:
            snapshot = Path(snapshot_download(model_id, revision=revision))
        if time.monotonic() >= deadline:
            status["status"] = "budget_stop"
            return
        print("Loading Qwen in FP16.", flush=True)
        processor = AutoProcessor.from_pretrained(str(snapshot), local_files_only=True)
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            str(snapshot), torch_dtype=torch.float16, device_map="auto", local_files_only=True).eval()
        if any(parameter.device.type != "cuda" for parameter in model.parameters()):
            raise RuntimeError("Qwen text inference requires all model weights on the GPU")
        # Verify generation on a benign question before resuming the benchmark.
        smoke_messages = [{"role": "user", "content": [{"type": "text", "text": "Name two colors found in a rainbow."}]}]
        smoke_prompt = processor.apply_chat_template(smoke_messages, tokenize=False, add_generation_prompt=True)
        smoke_inputs = processor(text=[smoke_prompt], return_tensors="pt").to(model.device)
        with torch.inference_mode():
            smoke_tokens = model.generate(**smoke_inputs, do_sample=False, max_new_tokens=256)
        smoke_answer = processor.batch_decode(smoke_tokens[:, smoke_inputs.input_ids.shape[1]:],
                                              skip_special_tokens=True)[0]
        if not smoke_answer.strip():
            raise ValueError("Qwen benign generation check returned an empty answer")
        print("Benign generation check passed.", flush=True)
        for row in rows:
            key = tuple(row[name] for name in ("scenario", "id", "variant"))
            if key in completed:
                continue
            if time.monotonic() >= deadline:
                status["status"] = "budget_stop"
                break
            identity = {name: row[name] for name in ("scenario", "id", "variant", "field")}
            try:
                messages = [{"role": "user", "content": [{"type": "text", "text": row["question"]}]}]
                prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[prompt], return_tensors="pt").to(model.device)
                with torch.inference_mode():
                    tokens = model.generate(**inputs, do_sample=False, max_new_tokens=256)
                answer = processor.batch_decode(tokens[:, inputs.input_ids.shape[1]:],
                                                skip_special_tokens=True)[0]
                if not answer.strip():
                    raise ValueError("Empty completion")
                append_private(out / "responses_PRIVATE.jsonl", dict(identity, response=answer))
                completed.add(key)
                status["completed"] += 1
                status["remaining"] = status["planned"] - status["completed"]
                atomic_json(out / "aggregate.json", status)
                if QWEN_TEXT_SMOKE or status["completed"] % 50 == 0:
                    atomic_json(out / "aggregate.json", status)
                    print(f"Saved {status['completed']:,}/{len(rows):,} answers.", flush=True)
            except Exception as exc:
                append_private(out / "failures_PRIVATE.jsonl", dict(identity, error_type=type(exc).__name__))
                status.update(failures=1, status="case_failure")
                break
        else:
            status["status"] = "completed_unscored"
    finally:
        if status["status"] == "running":
            status["status"] = "interrupted_or_setup_failure"
        status["remaining"] = status["planned"] - status["completed"]
        atomic_json(out / "aggregate.json", status)
        print({name: status[name] for name in ("status", "planned", "completed", "failures", "remaining")})


if QWEN_TEXT_PREFLIGHT or RUN_QWEN_TEXT:
    print("Matching text-only questions to the archived Qwen image run.", flush=True)
    if not PRIVATE.is_dir():
        raise FileNotFoundError(f"Mount college Drive and verify {PRIVATE}")
    if digest(AUTHOR_ZIP) != AUTHOR_SHA:
        raise ValueError("Unexpected author ZIP")
    text_cases = qwen_text_cases(PRIVATE)
    print(dict(text_cases=len(text_cases), manifest_sha256=manifest_hash(text_cases)))
    if RUN_QWEN_TEXT:
        run_qwen_text(text_cases)
    else:
        print("Input checks complete. This preflight did not generate answers.")
