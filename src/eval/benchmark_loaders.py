"""Loaders that map public safety-benchmark rows to the shared BenchmarkItem record.

Pure row->item mappers are unit-tested on synthetic rows. The thin `load_*`
functions fetch from the Hugging Face Hub (lazy `datasets` import) and are NOT
exercised offline; verify them against the real data before relying on them.

HoliSafe-Bench is gated and its column schema has not been inspected, so its
mapper requires an explicit column map and state map and never guesses.
"""

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from PIL import Image

from src.data.data_types import BenchmarkItem

# Canonical image/text safety states (HoliSafe paper naming: U/S = unsafe/safe,
# i = image, t = text; SiStU = safe+safe that becomes unsafe, SiStS = safe+safe, safe).
CANONICAL_STATES = ("UiUt", "UiSt", "SiUt", "SiStU", "SiStS")

# MM-SafetyBench splits -> the channel carrying the request.
MMSAFETY_CHANNELS = {
    "Text_only": "text",
    "SD": "image_sd",
    "TYPO": "image_typo",
    "SD_TYPO": "image_sd_typo",
}

# Config names on the Hub (spelling, including "Illegal_Activitiy", is the dataset's own).
MMSAFETY_SCENARIOS = (
    "EconomicHarm", "Financial_Advice", "Fraud", "Gov_Decision", "HateSpeech",
    "Health_Consultation", "Illegal_Activitiy", "Legal_Opinion", "Malware_Generation",
    "Physical_Harm", "Political_Lobbying", "Privacy_Violence", "Sex",
)

_HOLISAFE_COLUMN_KEYS = ("id", "prompt", "image", "state", "category")


def mmsafety_rows_to_items(rows: Iterable[Dict[str, Any]], scenario: str, variant: str) -> List[BenchmarkItem]:
    if variant not in MMSAFETY_CHANNELS:
        raise ValueError(f"unknown MM-SafetyBench variant {variant!r}; expected one of {sorted(MMSAFETY_CHANNELS)}")
    return [
        BenchmarkItem(
            id=f"mmsafety/{scenario}/{variant}/{row['id']}",
            prompt=row["question"],
            benchmark_name="MM-SafetyBench",
            image=row.get("image"),
            attack_category=scenario,
            # One question appears in every variant of a scenario; cluster/pair_key link those copies.
            metadata={"scenario": scenario, "variant": variant, "channel": MMSAFETY_CHANNELS[variant],
                      "cluster": f"{scenario}/{row['id']}", "pair_key": f"{scenario}/{row['id']}"},
        )
        for row in rows
    ]


def vlsbench_rows_to_items(rows: Iterable[Dict[str, Any]]) -> List[BenchmarkItem]:
    return [
        BenchmarkItem(
            id=f"vlsbench/{row['instruction_id']}",
            prompt=row["instruction"],
            benchmark_name="VLSBench",
            image=row.get("image"),
            attack_category=row.get("category"),
            metadata={"category": row.get("category"), "sub_category": row.get("sub_category"),
                      "source": row.get("source"),
                      "cluster": row.get("image_path") or f"vlsbench/{row['instruction_id']}"},
        )
        for row in rows
    ]


def holisafe_rows_to_items(
    rows: Iterable[Dict[str, Any]], column_map: Dict[str, str], state_map: Dict[str, str]
) -> List[BenchmarkItem]:
    """Map HoliSafe-style rows using an explicit schema.

    column_map: keys id/prompt/image/state/category -> actual column names.
    state_map:  raw label value -> one of CANONICAL_STATES.
    """
    missing_keys = [k for k in _HOLISAFE_COLUMN_KEYS if k not in column_map]
    if missing_keys:
        raise KeyError(f"column_map is missing keys: {missing_keys}")
    bad = {v for v in state_map.values() if v not in CANONICAL_STATES}
    if bad:
        raise ValueError(f"state_map values must be canonical states {CANONICAL_STATES}; got {sorted(bad)}")

    items = []
    for row in rows:
        for key in _HOLISAFE_COLUMN_KEYS:
            if column_map[key] not in row:
                raise KeyError(f"missing column {column_map[key]!r} (mapped from {key!r})")
        cluster_col = column_map.get("cluster")
        if cluster_col is not None and cluster_col not in row:
            raise KeyError(f"missing column {cluster_col!r} (mapped from 'cluster')")
        raw_state = row[column_map["state"]]
        if raw_state not in state_map:
            raise ValueError(f"unknown state label {raw_state!r}; add it to state_map after checking the schema")
        item_id = f"holisafe/{row[column_map['id']]}"
        items.append(BenchmarkItem(
            id=item_id,
            prompt=row[column_map["prompt"]],
            benchmark_name="HoliSafe-Bench",
            image=row[column_map["image"]],
            attack_category=row[column_map["category"]],
            metadata={"state": state_map[raw_state], "category": row[column_map["category"]],
                      "cluster": str(row[cluster_col]) if cluster_col else item_id},
        ))
    return items


def stratified_sample(
    items: Sequence[BenchmarkItem], key_fn: Callable[[BenchmarkItem], str], n_per_stratum: int, seed: int
) -> Tuple[List[BenchmarkItem], Dict[str, int]]:
    """Deterministic equal-per-stratum sample. Returns (sample, shortfalls).

    A stratum with fewer than n_per_stratum items contributes all of them and is
    reported in `shortfalls` (stratum -> missing count) instead of silently shrinking.
    """
    strata: Dict[str, List[BenchmarkItem]] = {}
    for it in items:
        strata.setdefault(key_fn(it), []).append(it)
    sample: List[BenchmarkItem] = []
    shortfalls: Dict[str, int] = {}
    for stratum in sorted(strata):
        pool = sorted(strata[stratum], key=lambda it: it.id)
        k = min(n_per_stratum, len(pool))
        if k < n_per_stratum:
            shortfalls[stratum] = n_per_stratum - k
        picked = random.Random(f"{seed}|{stratum}").sample(pool, k)
        sample.extend(sorted(picked, key=lambda it: it.id))
    return sample, shortfalls


def write_manifest(items: Sequence[BenchmarkItem], path: Path, key_fn: Callable[[BenchmarkItem], str]) -> None:
    """Write ids and strata only (never prompt text) so manifests are safe to share."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for it in items:
            f.write(json.dumps({"id": it.id, "stratum": key_fn(it)}) + "\n")


def read_manifest(path: Path) -> List[Dict[str, str]]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def manifest_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def synthetic_items(n_per_channel: int = 2) -> List[BenchmarkItem]:
    """Neutral placeholder items for dry runs and tests. Contains no harmful content."""
    items = []
    for channel in ("text", "image"):
        for i in range(n_per_channel):
            img = Image.new("RGB", (64, 64), (200, 200, 200)) if channel == "image" else None
            items.append(BenchmarkItem(
                id=f"synthetic/{channel}/{i}", prompt=f"Placeholder question {i}",
                benchmark_name="SYNTHETIC", image=img, attack_category="placeholder",
                metadata={"channel": channel},
            ))
    return items


# ---- Thin Hub loaders (network; not covered by offline tests) ----------------

def load_mmsafety(scenarios: Optional[Sequence[str]] = None,
                  variants: Sequence[str] = tuple(MMSAFETY_CHANNELS),
                  repo: str = "PKU-Alignment/MM-SafetyBench") -> List[BenchmarkItem]:
    from datasets import load_dataset
    items: List[BenchmarkItem] = []
    for scenario in (scenarios or MMSAFETY_SCENARIOS):
        for variant in variants:
            ds = load_dataset(repo, scenario, split=variant)
            items.extend(mmsafety_rows_to_items(ds, scenario, variant))
    return items


def load_vlsbench(repo: str = "Foreshhh/vlsbench") -> List[BenchmarkItem]:
    from datasets import load_dataset
    return vlsbench_rows_to_items(load_dataset(repo, split="train"))


def load_holisafe(column_map: Dict[str, str], state_map: Dict[str, str], split: str,
                  config: Optional[str] = None, repo: str = "etri-vilab/holisafe-bench") -> List[BenchmarkItem]:
    """Requires Hub login with access granted. `split` has no default on purpose: inspect the schema first."""
    from datasets import load_dataset
    return holisafe_rows_to_items(load_dataset(repo, config, split=split), column_map, state_map)
