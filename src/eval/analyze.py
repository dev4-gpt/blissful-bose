"""Cross-benchmark analysis helpers: rates with cluster-bootstrap CIs, paired tests, rank correlation.

Rates are fractions in [0, 1] (the paper tables use percent; multiply by 100 when reporting).
A "success" is whatever the caller defines: attack success on unsafe-state items, refusal on
the benign state. Records are plain dicts, so one set of functions serves every benchmark.

The bootstrap resamples clusters (images), not items, because several questions can share one
image. Paired comparisons need a shared key (e.g. an image id) present in both conditions; when
no such key exists, do not force a paired test: compare the two rates with their CIs instead.
All functions are deterministic given `seed`. No scipy dependency.
"""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Hashable, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from src.eval import safety_judge as sj


def cluster_bootstrap_ci(clusters: Sequence[Hashable], successes: Sequence[bool],
                         n_boot: int = 2000, seed: int = 0,
                         alpha: float = 0.05) -> Tuple[float, float, float]:
    """Return (rate, lo, hi): pooled success rate with a percentile CI from cluster resampling."""
    if len(clusters) != len(successes):
        raise ValueError("clusters and successes must have the same length")
    if not len(clusters):
        raise ValueError("no observations")
    counts: Dict[Hashable, List[int]] = defaultdict(lambda: [0, 0])
    for c, s in zip(clusters, successes):
        counts[c][0] += int(bool(s))
        counts[c][1] += 1
    k = np.array([v[0] for v in counts.values()], dtype=float)
    m = np.array([v[1] for v in counts.values()], dtype=float)
    idx = np.random.default_rng(seed).integers(0, len(k), size=(n_boot, len(k)))
    rates = k[idx].sum(axis=1) / m[idx].sum(axis=1)
    lo, hi = np.quantile(rates, [alpha / 2, 1 - alpha / 2])
    return float(k.sum() / m.sum()), float(lo), float(hi)


def rate_table(records: Iterable[Mapping], keys: Sequence[str], cluster_key: str = "cluster",
               success_key: str = "success", n_boot: int = 2000, seed: int = 0) -> List[dict]:
    """One row per group of `keys`: n, n_clusters, rate, lo, hi. Rows sorted by group."""
    groups: Dict[tuple, List[Mapping]] = defaultdict(list)
    for r in records:
        groups[tuple(r[k] for k in keys)].append(r)
    rows = []
    for gk in sorted(groups, key=lambda t: tuple(map(str, t))):
        recs = groups[gk]
        rate, lo, hi = cluster_bootstrap_ci([r[cluster_key] for r in recs], [r[success_key] for r in recs],
                                            n_boot=n_boot, seed=seed)
        rows.append({**dict(zip(keys, gk)), "n": len(recs), "n_clusters": len({r[cluster_key] for r in recs}),
                     "rate": rate, "lo": lo, "hi": hi})
    return rows


def mcnemar_exact(b: int, c: int) -> float:
    """Exact two-sided McNemar p-value from the discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1))
    return min(1.0, 2 * tail / 2 ** n)


def cohens_kappa(n11: int, n10: int, n01: int, n00: int) -> float:
    """Chance-corrected agreement of two binary outcomes; nan when undefined."""
    n = n11 + n10 + n01 + n00
    if n == 0:
        return float("nan")
    po = (n11 + n00) / n
    pa, pb = (n11 + n10) / n, (n11 + n01) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def paired_comparison(a: Mapping[Hashable, bool], b: Mapping[Hashable, bool]) -> dict:
    """Compare two conditions over the keys they share.

    n10 = success in a only, n01 = success in b only. odds_ratio is the matched-pairs
    ratio n10/n01 with a 0.5 continuity correction; p_value is the exact McNemar test;
    kappa measures how much the two outcomes agree beyond chance (the "coupling").
    """
    n11 = n10 = n01 = n00 = 0
    for key in a.keys() & b.keys():
        x, y = bool(a[key]), bool(b[key])
        n11 += x and y
        n10 += x and not y
        n01 += (not x) and y
        n00 += (not x) and (not y)
    return {"n_pairs": n11 + n10 + n01 + n00, "n11": n11, "n10": n10, "n01": n01, "n00": n00,
            "odds_ratio": (n10 + 0.5) / (n01 + 0.5), "p_value": mcnemar_exact(n10, n01),
            "kappa": cohens_kappa(n11, n10, n01, n00)}


def _average_ranks(values: Sequence[float]) -> List[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for t in range(i, j + 1):
            ranks[order[t]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    """Spearman rank correlation with average ranks for ties; nan if undefined."""
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if len(x) < 2:
        return float("nan")
    rx, ry = np.array(_average_ranks(x)), np.array(_average_ranks(y))
    dx, dy = rx - rx.mean(), ry - ry.mean()
    denom = math.sqrt(float((dx ** 2).sum() * (dy ** 2).sum()))
    return float("nan") if denom == 0 else float((dx * dy).sum() / denom)


def rank_stability(rates: Mapping[str, Mapping[str, float]]) -> Dict[Tuple[str, str], float]:
    """Spearman between benchmarks' model rankings over their common models.

    rates: benchmark -> {model: rate}. Fewer than 3 common models gives nan, because a
    correlation over 2 points is always +/-1 and says nothing.
    """
    names = sorted(rates)
    out: Dict[Tuple[str, str], float] = {}
    for i, b1 in enumerate(names):
        for b2 in names[i + 1:]:
            common = sorted(set(rates[b1]) & set(rates[b2]))
            out[(b1, b2)] = (spearman([rates[b1][m] for m in common], [rates[b2][m] for m in common])
                             if len(common) >= 3 else float("nan"))
    return out


def _per_cluster(records: Iterable[Mapping], group_key: str, cond: Hashable,
                 cluster_key: str, success_key: str) -> Dict[Hashable, List[int]]:
    """cluster -> [successes, count] for the records in one condition."""
    out: Dict[Hashable, List[int]] = defaultdict(lambda: [0, 0])
    for r in records:
        if r[group_key] == cond:
            out[r[cluster_key]][0] += int(bool(r[success_key]))
            out[r[cluster_key]][1] += 1
    return out


def image_level_difference(records: Sequence[Mapping], cond_a: Hashable, cond_b: Hashable,
                           group_key: str = "state", cluster_key: str = "cluster",
                           success_key: str = "success", n_boot: int = 2000, seed: int = 0,
                           alpha: float = 0.05) -> dict:
    """Paired comparison of two conditions at the image level.

    Item-level McNemar needs one item per condition per key, which the benchmarks do not give
    (e.g. different numbers of UiUt and UiSt questions). Instead each shared image gets a rate
    under each condition; the statistic is the mean of (rate_a - rate_b) over shared images,
    with a percentile CI from resampling images.
    """
    a = _per_cluster(records, group_key, cond_a, cluster_key, success_key)
    b = _per_cluster(records, group_key, cond_b, cluster_key, success_key)
    shared = sorted(set(a) & set(b), key=str)
    if not shared:
        raise ValueError("no cluster has both conditions; use unpaired_difference instead")
    ra = np.array([a[c][0] / a[c][1] for c in shared])
    rb = np.array([b[c][0] / b[c][1] for c in shared])
    d = ra - rb
    idx = np.random.default_rng(seed).integers(0, len(d), size=(n_boot, len(d)))
    lo, hi = np.quantile(d[idx].mean(axis=1), [alpha / 2, 1 - alpha / 2])
    return {"n_clusters": len(shared), "rate_a": float(ra.mean()), "rate_b": float(rb.mean()),
            "diff": float(d.mean()), "lo": float(lo), "hi": float(hi)}


def unpaired_difference(records: Sequence[Mapping], cond_a: Hashable, cond_b: Hashable,
                        group_key: str = "state", cluster_key: str = "cluster",
                        success_key: str = "success", n_boot: int = 2000, seed: int = 0,
                        alpha: float = 0.05) -> dict:
    """Rate difference when the conditions share no images: clusters are resampled independently."""
    a = _per_cluster(records, group_key, cond_a, cluster_key, success_key)
    b = _per_cluster(records, group_key, cond_b, cluster_key, success_key)
    if not a or not b:
        raise ValueError("a condition has no records")
    ka, ma = (np.array([v[i] for v in a.values()], dtype=float) for i in (0, 1))
    kb, mb = (np.array([v[i] for v in b.values()], dtype=float) for i in (0, 1))
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, len(ka), size=(n_boot, len(ka)))
    ib = rng.integers(0, len(kb), size=(n_boot, len(kb)))
    boots = ka[ia].sum(axis=1) / ma[ia].sum(axis=1) - kb[ib].sum(axis=1) / mb[ib].sum(axis=1)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    rate_a, rate_b = float(ka.sum() / ma.sum()), float(kb.sum() / mb.sum())
    return {"n_clusters_a": len(ka), "n_clusters_b": len(kb), "rate_a": rate_a, "rate_b": rate_b,
            "diff": rate_a - rate_b, "lo": float(lo), "hi": float(hi)}


def agreement_metrics(pred: Sequence[bool], truth: Sequence[bool]) -> dict:
    """Agreement of a cheap labeller (pred) with hand labels (truth); positive = violation."""
    if len(pred) != len(truth):
        raise ValueError("pred and truth must have the same length")
    tp = sum(bool(p) and bool(t) for p, t in zip(pred, truth))
    fp = sum(bool(p) and not t for p, t in zip(pred, truth))
    fn = sum((not p) and bool(t) for p, t in zip(pred, truth))
    tn = len(pred) - tp - fp - fn
    nan = float("nan")
    return {"n": len(pred), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": tp / (tp + fp) if tp + fp else nan,
            "recall": tp / (tp + fn) if tp + fn else nan,
            "accuracy": (tp + tn) / len(pred) if len(pred) else nan,
            "kappa": cohens_kappa(tp, fp, fn, tn)}


def calibration_by_group(rows: Iterable[Mapping], group_key: str, pred_key: str, truth_key: str) -> List[dict]:
    """agreement_metrics per group (e.g. per state), rows sorted by group."""
    groups: Dict[Hashable, List[Mapping]] = defaultdict(list)
    for r in rows:
        groups[r[group_key]].append(r)
    return [{group_key: g, **agreement_metrics([r[pred_key] for r in groups[g]],
                                               [r[truth_key] for r in groups[g]])}
            for g in sorted(groups, key=str)]


_SUCCESS_FIELDS = {"judge": "judge_violation", "string_paper": "string_paper_violation",
                   "string_strict": "string_strict_violation"}


def _read_jsonl(path) -> List[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def load_joined(responses_path, judgments_path) -> List[dict]:
    """Join saved responses with judgments by id into flat records.

    A violation is True when the model failed the expected behaviour (attack success on
    unsafe-expected items, over-refusal or a bad answer on safe-expected items); None means the
    judge output could not be parsed.
    """
    responses = {r["id"]: r for r in _read_jsonl(responses_path)}
    records = []
    for j in _read_jsonl(judgments_path):
        r = responses.get(j["id"])
        if r is None:
            continue
        meta = r.get("meta") or {}
        expected = j["expected"]
        records.append({
            "id": j["id"], "benchmark": r.get("benchmark_name"), "state": meta.get("state"),
            "channel": meta.get("channel"), "scenario": meta.get("scenario"), "category": meta.get("category"),
            "cluster": meta.get("cluster") or j["id"], "expected": expected,
            "judge_violation": sj.is_violation(j.get("adherent")),
            "string_paper_violation": sj.string_match_violation(j["string_match_paper"], expected),
            "string_strict_violation": sj.string_match_violation(j["string_match_strict"], expected),
        })
    return records


def summarize(records: Sequence[Mapping], success: str, group_by: Sequence[str],
              n_boot: int = 2000, seed: int = 0) -> Tuple[List[dict], int]:
    """Violation-rate table per group plus the number of records excluded for having no label."""
    field = _SUCCESS_FIELDS[success]
    kept = [{**r, "success": r[field]} for r in records if r[field] is not None]
    table = rate_table(kept, tuple(group_by), n_boot=n_boot, seed=seed) if kept else []
    return table, len(records) - len(kept)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Per-group violation rates from saved responses and judgments.")
    ap.add_argument("--responses", required=True)
    ap.add_argument("--judgments", required=True)
    ap.add_argument("--success", choices=sorted(_SUCCESS_FIELDS), default="judge")
    ap.add_argument("--group-by", nargs="+", default=["benchmark", "state"])
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--csv")
    ap.add_argument("--compare", nargs=2, metavar=("STATE_A", "STATE_B"),
                    help="image-level difference between two states (rate_a - rate_b)")
    args = ap.parse_args(argv)

    records = load_joined(args.responses, args.judgments)
    table, excluded = summarize(records, args.success, args.group_by, args.n_boot, args.seed)
    print(f"Violation rate by {', '.join(args.group_by)} using '{args.success}' "
          "(attack success rate for unsafe-expected groups, refusal/error rate for the benign state)")
    for row in table:
        label = " / ".join(str(row[k]) for k in args.group_by)
        print(f"  {label}  n={row['n']}  images={row['n_clusters']}  rate={row['rate'] * 100:.1f}%  "
              f"95% CI [{row['lo'] * 100:.1f}, {row['hi'] * 100:.1f}]")
    print(f"Excluded (no parsed label): {excluded}")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[*args.group_by, "n", "n_clusters", "rate", "lo", "hi"])
            w.writeheader()
            w.writerows(table)
    if args.compare:
        a, b = args.compare
        field = _SUCCESS_FIELDS[args.success]
        kept = [{**r, "success": r[field]} for r in records if r[field] is not None]
        try:
            res = image_level_difference(kept, a, b, n_boot=args.n_boot, seed=args.seed)
            print(f"Image-level difference {a} - {b}: {res['diff'] * 100:+.1f} points over {res['n_clusters']} "
                  f"shared images (95% CI [{res['lo'] * 100:.1f}, {res['hi'] * 100:.1f}])")
        except ValueError as exc:
            print(f"Image-level comparison unavailable: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
