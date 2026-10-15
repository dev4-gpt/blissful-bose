#!/usr/bin/env python3
"""Resume-safe VLM runner for the cross-benchmark safety evaluation.

Inference only (greedy decoding, no gradients, no weight updates). Raw responses
are appended to a JSONL file and labelling is done separately. The runner NEVER
simulates responses: if the model cannot be loaded the run fails loudly.

Raw responses can contain harmful text. Keep the output out of git and off
shared drives. The model family is chosen by the Hub id alone (LLaVA, Qwen2-VL,
Qwen2.5-VL) via AutoModelForImageTextToText; the first real run is the
compatibility check for the pinned transformers version.

Usage
  python3 -m src.eval.run_vlm_eval --synthetic --dry-run
  python3 -m src.eval.run_vlm_eval --benchmark mmsafety --scenarios Fraud --variants Text_only TYPO \\
      --sample-per-stratum 20 --stratify-by channel --manifest-out data/eval/manifest.jsonl --dry-run
  python3 -m src.eval.run_vlm_eval --benchmark mmsafety --manifest data/eval/manifest.jsonl \\
      --model Qwen/Qwen2-VL-2B-Instruct --out data/eval/responses.jsonl --limit 10
"""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.data.data_types import BenchmarkItem
from src.eval import benchmark_loaders as bl

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "data" / "eval" / "responses.jsonl"
STRATIFY_KEYS = ("state", "channel", "category", "scenario")
KEPT_META = ("state", "channel", "scenario", "category", "variant", "cluster", "pair_key")


def done_ids(path: Path) -> Set[str]:
    path = Path(path)
    if not path.exists():
        return set()
    return {json.loads(line)["id"] for line in path.read_text().splitlines() if line.strip()}


def build_messages(item: BenchmarkItem, system_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
    msgs: List[Dict[str, Any]] = []
    if system_prompt:
        msgs.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})
    content: List[Dict[str, Any]] = []
    if item.image is not None:
        content.append({"type": "image"})
    content.append({"type": "text", "text": item.prompt})
    msgs.append({"role": "user", "content": content})
    return msgs


def select_items(args) -> List[BenchmarkItem]:
    if args.synthetic:
        items = bl.synthetic_items()
    elif args.benchmark == "mmsafety":
        items = bl.load_mmsafety(args.scenarios, tuple(args.variants) if args.variants else tuple(bl.MMSAFETY_CHANNELS))
    elif args.benchmark == "vlsbench":
        items = bl.load_vlsbench()
    elif args.benchmark == "holisafe":
        if not args.holisafe_config:
            raise SystemExit("--holisafe-config (JSON with column_map, state_map, split) is required; "
                             "inspect the gated schema first")
        cfg = json.loads(Path(args.holisafe_config).read_text())
        items = bl.load_holisafe(cfg["column_map"], cfg["state_map"], cfg["split"], cfg.get("config"))
    else:
        raise SystemExit("choose --synthetic or --benchmark {mmsafety,vlsbench,holisafe}")

    if args.manifest:
        wanted = {row["id"] for row in bl.read_manifest(Path(args.manifest))}
        items = [it for it in items if it.id in wanted]
    if args.sample_per_stratum:
        key = lambda it: str(it.metadata[args.stratify_by])  # noqa: E731  (KeyError if the item lacks the field)
        items, short = bl.stratified_sample(items, key, args.sample_per_stratum, args.seed)
        if short:
            print(f"WARNING: strata smaller than requested (missing counts): {short}")
        if args.manifest_out:
            bl.write_manifest(items, Path(args.manifest_out), key)
            print(f"Wrote manifest {args.manifest_out} sha256={bl.manifest_sha256(Path(args.manifest_out))}")
    return items[: args.limit] if args.limit else items


def load_model(model_id: str):
    """Load processor and model, or raise. Never falls back to simulated output."""
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor

    if torch.cuda.is_available():
        device, dtype = "cuda", torch.bfloat16
    elif torch.backends.mps.is_available():
        device, dtype = "mps", torch.float16
    else:
        device, dtype = "cpu", torch.float32
    print(f"Loading {model_id} on {device} ({dtype})")
    processor = AutoProcessor.from_pretrained(model_id)
    try:
        model = AutoModelForImageTextToText.from_pretrained(model_id, dtype=dtype)
    except TypeError:  # older transformers spell it torch_dtype
        model = AutoModelForImageTextToText.from_pretrained(model_id, torch_dtype=dtype)
    return processor, model.to(device).eval(), device


def run(args, items: List[BenchmarkItem]) -> None:
    import torch

    processor, model, device = load_model(args.model)
    out = Path(args.out)
    finished = done_ids(out)
    todo = [it for it in items if it.id not in finished]
    print(f"{len(todo)} to run ({len(finished)} already in {out.name})")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a") as f:
        for i, it in enumerate(todo, 1):
            text = processor.apply_chat_template(
                build_messages(it, args.system_prompt), tokenize=False, add_generation_prompt=True)
            img = it.image.convert("RGB") if it.image is not None else None
            inputs = processor(text=[text], images=[img] if img is not None else None,
                               return_tensors="pt").to(device)
            with torch.no_grad():
                gen = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
            new_ids = gen[0, inputs["input_ids"].shape[1]:]
            row = {
                "id": it.id, "benchmark_name": it.benchmark_name, "model": args.model,
                "response": processor.decode(new_ids, skip_special_tokens=True),
                "new_tokens": int(new_ids.shape[0]), "max_new_tokens": args.max_new_tokens,
                "system_prompt": args.system_prompt,
                "meta": {k: it.metadata[k] for k in KEPT_META if k in it.metadata},
            }
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(f"[{i}/{len(todo)}] {it.id}  {row['response'][:60]!r}")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="Qwen/Qwen2-VL-2B-Instruct")
    ap.add_argument("--synthetic", action="store_true", help="neutral placeholder items; no data or network")
    ap.add_argument("--benchmark", choices=["mmsafety", "vlsbench", "holisafe"])
    ap.add_argument("--scenarios", nargs="+")
    ap.add_argument("--variants", nargs="+", choices=list(bl.MMSAFETY_CHANNELS))
    ap.add_argument("--holisafe-config", help="JSON: column_map, state_map, split[, config]")
    ap.add_argument("--manifest", help="keep only ids listed in this manifest")
    ap.add_argument("--sample-per-stratum", type=int)
    ap.add_argument("--stratify-by", choices=STRATIFY_KEYS, default="channel")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--manifest-out")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--system-prompt")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--dry-run", action="store_true")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    items = select_items(args)
    print(f"{len(items)} items selected: {dict(Counter(it.benchmark_name for it in items))}")
    if args.dry_run:
        print("Dry run OK: items selected; no model loaded and nothing written.")
        return 0
    run(args, items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
