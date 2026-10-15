#!/usr/bin/env python3
"""Judge runner: scores saved responses with an open model, following the HoliSafe protocol.

Protocol (HoliSafe paper App. D and the authors' eval scripts): the judge is told the expected
behaviour (safety_label safe / unsafe) and answers True (adhered) or False (violation) in a
<label> tag. ASR = share of False on unsafe-expected items; RR = share of False on safe-expected
items. String-match labels (the authors' list and our stricter variant) are written beside the
judge label and are never merged with it.

Modes
  vision  the judge sees the image (default; judge model must be a different family from the
          models being judged, e.g. OpenGVLab/InternVL3-8B-hf for LLaVA and Qwen targets)
  text    the judge sees only the query and response (AutoModelForCausalLM)

Never simulates judgments: if the judge model cannot load the run fails before writing anything.
Unparseable judge output is stored with adherent=null and the raw text, never guessed.
Judgments can echo harmful text. Keep the output out of git (data/eval/ is ignored).

Usage
  python3 -m src.eval.run_judge --responses data/eval/responses.jsonl --benchmark holisafe \\
      --holisafe-config data/eval/holisafe_config.json --manifest data/eval/manifest.jsonl --dry-run
"""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from src.data.data_types import BenchmarkItem
from src.eval import benchmark_loaders as bl
from src.eval import run_vlm_eval as rv
from src.eval import safety_judge as sj

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "data" / "eval" / "judgments.jsonl"
DEFAULT_JUDGE = {"vision": "OpenGVLab/InternVL3-8B-hf", "text": "Qwen/Qwen2.5-7B-Instruct"}


def read_responses(path: Path) -> List[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def expected_for(row: dict, expected_arg: str) -> str:
    """Expected behaviour ('safe'/'unsafe') for a response row. Refuses to mislabel silently."""
    state = (row.get("meta") or {}).get("state")
    if expected_arg == "from-state":
        if not state:
            raise ValueError("response row has no state in meta; pass --expected safe|unsafe "
                             "only for benchmarks that have no states")
        return sj.expected_label(state)
    if state:
        raise ValueError(f"--expected {expected_arg} would conflict with the row's state {state!r}; use from-state")
    return expected_arg


def join_responses(rows: List[dict], items: List[BenchmarkItem]) -> Tuple[List[Tuple[dict, BenchmarkItem]], List[str]]:
    by_id: Dict[str, BenchmarkItem] = {it.id: it for it in items}
    pairs = [(r, by_id[r["id"]]) for r in rows if r["id"] in by_id]
    return pairs, [r["id"] for r in rows if r["id"] not in by_id]


def load_judge_model(args) -> Callable[[str, BenchmarkItem], str]:
    """Return judge(prompt, item) -> raw text. Raises if the model cannot load."""
    import torch

    model_id = args.judge_model or DEFAULT_JUDGE[args.mode]
    if args.mode == "vision":
        processor, model, device = rv.load_model(model_id)

        def judge_vision(prompt: str, item: BenchmarkItem) -> str:
            messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}]
            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=[text], images=[item.image.convert("RGB")], return_tensors="pt").to(device)
            with torch.no_grad():
                gen = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
            return processor.decode(gen[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        return judge_vision

    from transformers import AutoModelForCausalLM, AutoTokenizer
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float16 if device == "mps" else torch.float32
    print(f"Loading judge {model_id} on {device} ({dtype})")
    tok = AutoTokenizer.from_pretrained(model_id)
    try:
        model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype)
    except TypeError:  # older transformers spell it torch_dtype
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype)
    model = model.to(device).eval()

    def judge_text(prompt: str, item: BenchmarkItem) -> str:
        text = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                       add_generation_prompt=True)
        inputs = tok(text, return_tensors="pt").to(device)
        with torch.no_grad():
            gen = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False)
        return tok.decode(gen[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    return judge_text


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--responses", required=True, help="JSONL written by run_vlm_eval")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--mode", choices=["vision", "text"], default="vision")
    ap.add_argument("--judge-model", help="default: InternVL3-8B-hf (vision) or Qwen2.5-7B-Instruct (text)")
    ap.add_argument("--expected", choices=["from-state", "safe", "unsafe"], default="from-state")
    ap.add_argument("--max-new-tokens", type=int, default=100, help="the authors' judge uses 100")
    # Item selection, reused from run_vlm_eval.select_items so images and prompts match the responses.
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--benchmark", choices=["mmsafety", "vlsbench", "holisafe"])
    ap.add_argument("--scenarios", nargs="+")
    ap.add_argument("--variants", nargs="+", choices=list(bl.MMSAFETY_CHANNELS))
    ap.add_argument("--holisafe-config")
    ap.add_argument("--manifest")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.set_defaults(sample_per_stratum=None, stratify_by="channel", seed=0, manifest_out=None)
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    rows = read_responses(Path(args.responses))
    pairs, missing = join_responses(rows, rv.select_items(args))
    if missing:
        print(f"WARNING: {len(missing)} responses have no matching item (first: {missing[:3]})")

    plan = []  # validate everything before any model is loaded or file is written
    for row, item in pairs:
        if args.mode == "vision" and item.image is None:
            raise ValueError(f"vision judge needs an image for {item.id}; use --mode text or fix selection")
        plan.append((row, item, expected_for(row, args.expected)))
    out = Path(args.out)
    finished = rv.done_ids(out)
    todo = [t for t in plan if t[0]["id"] not in finished]
    print(f"{len(rows)} responses, {len(plan)} matched, {len(todo)} to judge "
          f"({len(finished)} already in {out.name}); expected: {dict(Counter(t[2] for t in plan))}")
    if args.dry_run:
        print("Dry run OK: responses matched and validated; no model loaded and nothing written.")
        return 0

    judge = load_judge_model(args)
    out.parent.mkdir(parents=True, exist_ok=True)
    judge_id = args.judge_model or DEFAULT_JUDGE[args.mode]
    with out.open("a") as f:
        for i, (row, item, expected) in enumerate(todo, 1):
            prompt = sj.build_judge_prompt(item.prompt, row["response"], expected, has_image=(args.mode == "vision"))
            raw = judge(prompt, item)
            rec = {"id": row["id"], "judge_model": judge_id, "mode": args.mode, "expected": expected,
                   "adherent": sj.parse_judge_output(raw), "raw": raw,
                   "string_match_paper": sj.string_match_label(row["response"], "paper"),
                   "string_match_strict": sj.string_match_label(row["response"], "strict")}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"[{i}/{len(todo)}] {row['id']}  adherent={rec['adherent']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
