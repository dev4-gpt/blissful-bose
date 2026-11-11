"""Diagnostic-only worker: replay the stopped InstructBLIP case; never edit answer ledgers."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import json
import os
import sys


def diagnose(root):
    from importlib.metadata import version
    import torch
    from PIL import Image
    from io import BytesIO

    root = Path(root)
    config = json.loads((root / "launch_PRIVATE.json").read_text())
    saved_identity = json.loads((root / "runtime_identity_PRIVATE.json").read_text())
    if config["TRACK"] != "instructblip":
        raise ValueError("This diagnostic is only for the stopped InstructBLIP run")
    environment = dict(torch=torch.__version__, transformers=version("transformers"),
                       gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
                       packages={name: version(name) for name in saved_identity["packages"]})
    if any(value != saved_identity[name] for name, value in environment.items()):
        raise ValueError(f"Diagnostic environment differs from the stopped run: {environment}")
    source = root / "worker_PRIVATE.py"
    if sha256(source.read_bytes()).hexdigest() != saved_identity["code_sha256"]:
        raise ValueError("Saved worker differs from the run identity")
    # Keep the exact saved model adapter, input mapping and generation settings.
    spec = importlib.util.spec_from_file_location("saved_instructblip_worker", source)
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)
    worker.__dict__.update(config)
    for name in ("AUTHOR_ZIP", "IMAGE_ZIP", "IMAGE_DIR", "WORK", "RUN_ROOT"):
        worker.__dict__[name] = Path(config[name])
    worker.WORK.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = root / "Diagnostics_PRIVATE" / stamp
    out.mkdir(parents=True, exist_ok=False)
    result = dict(status="started", original_identity=saved_identity, diagnostic_only=True,
                  note="No prompt, token-limit, model-weight or stopping-setting changes; no benchmark ledger writes.")
    def save():
        worker.atomic(out / "token_inspection_PRIVATE.json", result)
    save()
    rows = json.loads((root / "manifest_PRIVATE.json").read_text())
    case, = [row for row in rows if row["scenario"] == "03-Malware_Generation"
             and str(row["id"]) == "0" and row["variant"] == "TYPO"]
    worker.stage_local_images()
    with worker.open_images() as images:
        if worker.manifest_hash(rows) != saved_identity["manifest_sha256"]:
            raise ValueError("Saved manifest mismatch")
        if worker.image_hash(images, rows) != saved_identity["image_sha256"]:
            raise ValueError("Saved required-image fingerprint mismatch")
        loaded = worker.load_model(worker.gpu_budgets(torch))
        model, processor = loaded
        if worker.assert_gpu_only(model) != saved_identity["placement"]:
            raise ValueError("Diagnostic placement differs from stopped run")
        lm = model.language_model
        tokenizer = processor.tokenizer
        result.update(case={k: case[k] for k in ("scenario", "id", "variant")},
                      tokenizer=dict(bos=tokenizer.bos_token_id, eos=tokenizer.eos_token_id,
                                     pad=tokenizer.pad_token_id, unk=tokenizer.unk_token_id,
                                     all_special_ids=tokenizer.all_special_ids,
                                     ids_0_1_2=tokenizer.convert_ids_to_tokens([0, 1, 2])),
                      outer_generation=model.generation_config.to_dict(),
                      language_generation=lm.generation_config.to_dict(),
                      image_token_index=getattr(model.config, "image_token_index", None),
                      processor_num_query_tokens=getattr(processor, "num_query_tokens", None),
                      attempts=[])
        original_generate = lm.generate
        current = {}
        def capture_generate(*args, **kwargs):
            current["generation_kwargs"] = {k: v for k, v in kwargs.items()
                                             if k not in {"inputs_embeds", "attention_mask", "input_ids"}}
            current["input_shapes"] = {k: list(v.shape) for k, v in kwargs.items() if torch.is_tensor(v)}
            outputs = original_generate(*args, **kwargs)
            sequence = outputs if torch.is_tensor(outputs) else outputs.sequences
            current["inner_token_ids"] = sequence.detach().cpu().tolist()
            return outputs
        def capture_first_logits(module, args, output):
            if "first_step" in current:
                return
            logits = output.logits[0, -1, :].detach().float()
            values, indices = logits.topk(5)
            current["first_step"] = dict(finite=bool(torch.isfinite(logits).all()),
                top_ids=indices.cpu().tolist(), top_logits=values.cpu().tolist())
        lm.generate = capture_generate
        hook = lm.register_forward_hook(capture_first_logits)
        try:
            for route in ("saved_adapter", "direct_upstream_call"):
                current = dict(route=route)
                result["attempts"].append(current)
                if route == "saved_adapter":
                    answer, count = worker.answer_case(case, images, loaded)
                    current.update(decoded_skip_special=answer, returned_token_count=count)
                else:
                    with Image.open(BytesIO(images.read(case["image_path"]))) as raw:
                        image = raw.convert("RGB")
                    inputs = processor(images=image, text=case["question"], return_tensors="pt")
                    worker.check_pixels(inputs["pixel_values"])
                    current["processor_shapes"] = {k: list(v.shape) for k, v in inputs.items()}
                    image_token_index = getattr(model.config, "image_token_index", None)
                    current["image_token_count"] = (
                        int((inputs["input_ids"] == image_token_index).sum()) if image_token_index is not None else None
                    )
                    inputs = inputs.to(next(model.vision_model.parameters()).device, dtype=torch.float16)
                    with torch.inference_mode():
                        outputs = model.generate(**inputs, do_sample=False, num_beams=1,
                                                 max_new_tokens=config["MAX_NEW_TOKENS"])
                    current["outer_token_ids"] = outputs.detach().cpu().tolist()
                    current["decoded_keep_special"] = tokenizer.batch_decode(outputs, skip_special_tokens=False)[0]
                    current["decoded_skip_special"] = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0].strip()
                ids = current["inner_token_ids"][0]
                current["inner_decoded_keep_special"] = tokenizer.decode(ids, skip_special_tokens=False)
                current["only_special_or_whitespace"] = not tokenizer.decode(ids, skip_special_tokens=True).strip()
                save()
            a, b = result["attempts"]
            result["routes_match"] = a["inner_token_ids"] == b["inner_token_ids"]
            result["status"] = "diagnostic_complete"
        except Exception as exc:
            result.update(status="diagnostic_failure", error_type=type(exc).__name__, error=str(exc))
            raise
        finally:
            lm.generate = original_generate
            hook.remove()
            save()
    # Print numeric IDs and booleans only. Raw decoding stays in the PRIVATE report.
    print(json.dumps(dict(status=result["status"], routes_match=result.get("routes_match"),
          tokenizer=result["tokenizer"], attempts=[dict(route=a["route"], ids=a.get("inner_token_ids"),
          empty=a.get("only_special_or_whitespace"), first_step=a.get("first_step"))
          for a in result["attempts"]], report=str(out / "token_inspection_PRIVATE.json")), indent=2))


if __name__ == "__main__":
    os.environ["MPLBACKEND"] = "Agg"
    diagnose(sys.argv[1])
