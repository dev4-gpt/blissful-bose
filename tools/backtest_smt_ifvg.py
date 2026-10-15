"""Backtest of the "NY open SMT divergence + inverse FVG retrace" strategy.

Rules and rationale: docs/PLAN_SMT_IFVG_BACKTEST.md. Research exercise only, not trading advice.
Usage: python tools/backtest_smt_ifvg.py [--days 59] [--draws 1000]
"""
from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from datetime import time

import pandas as pd

TICK = 0.25
COMMISSION_PTS = 2.25  # $4.50 round trip per MNQ at $2/pt
SMT_LOOKBACK = 12
IFVG_WINDOW = 12
FILL_WINDOW = 12
WIN_START, WIN_END, FLAT = time(9, 30), time(11, 30), time(12, 0)


@dataclass
class Setup:
    entry_idx: int      # bar where limit is filled
    entry: float
    stop: float
    smt_idx: int


def wilson(wins: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / d, (c + m) / d)


def smt_bull(nl, el, i: int, n: int = SMT_LOOKBACK) -> bool:
    """Bar i sweeps NQ's n-bar low while ES holds its own."""
    if i < n:
        return False
    return nl[i] < min(nl[i - n:i]) and el[i] >= min(el[i - n:i])


def bearish_fvg_top(nh, nl, k: int) -> float | None:
    """Top of the bearish FVG completed at bar k (gap between bar k-2 low and bar k high)."""
    if k >= 2 and nl[k - 2] > nh[k]:
        return nl[k - 2]
    return None


def find_long_setup(nh, nl, nc, el, idxs: list[int]) -> Setup | None:
    """First SMT -> IFVG -> retrace-fill sequence inside the entry window (long side)."""
    for i in idxs:
        if not smt_bull(nl, el, i):
            continue
        extreme = nl[i]
        for j in range(i + 1, min(i + 1 + IFVG_WINDOW, len(nc))):
            top = None
            for k in range(max(2, i - 6), j):
                t = bearish_fvg_top(nh, nl, k)
                if t is not None and nc[j] > t:
                    top = t
            if top is None:
                continue
            stop = extreme - TICK
            if top - stop < 1.0:
                continue
            for m in range(j + 1, min(j + 1 + FILL_WINDOW, len(nc))):
                if nc[m] <= stop:
                    break
                if nl[m] <= top:
                    return Setup(m, top, stop, i)
            break
    return None


def simulate_long(nh, nl, nc, end_idx: int, s: Setup, target: float | None) -> float | None:
    """Return R for a long; None if no valid target. Stop wins ties; target ignored on fill bar."""
    risk = s.entry - s.stop
    if target is None or target <= s.entry:
        return None
    cost = 2 * TICK + COMMISSION_PTS
    if nl[s.entry_idx] <= s.stop:
        return (-risk - cost) / risk
    for b in range(s.entry_idx + 1, end_idx + 1):
        if nl[b] <= s.stop:
            return (-risk - cost) / risk
        if nh[b] >= target:
            return (target - s.entry - cost) / risk
    return (nc[end_idx] - s.entry - cost) / risk


def liquidity_target(nh, s: Setup, session_lo: int, prev_high: float) -> float | None:
    """Nearest resting liquidity above entry giving >= 1R: swing highs before SMT, or previous-day high."""
    risk = s.entry - s.stop
    cands = [prev_high]
    for x in range(max(session_lo + 2, 2), s.smt_idx - 2):
        if nh[x] == max(nh[x - 2:x + 3]):
            cands.append(nh[x])
    ok = [c for c in cands if c - s.entry >= risk]
    return min(ok) if ok else None


def load(days: int) -> pd.DataFrame:
    import yfinance as yf
    raw = {}
    for name, sym in (("n", "NQ=F"), ("e", "ES=F")):
        d = yf.download(sym, period=f"{days}d", interval="5m", progress=False, auto_adjust=False)
        d.columns = [c[0] if isinstance(c, tuple) else c for c in d.columns]
        d.index = d.index.tz_convert("America/New_York")
        raw[name] = d[["High", "Low", "Close"]].rename(columns={"High": "h", "Low": "l", "Close": "c"}).add_prefix(name)
    df = raw["n"].join(raw["e"], how="inner").dropna()
    return df[~df.index.duplicated()]


def run(df: pd.DataFrame, draws: int, seed: int = 7) -> None:
    dates = sorted(set(df.index.date))
    results = {"2R": [], "3R": [], "liq": []}
    infos = []
    for di, day in enumerate(dates[1:], 1):
        prev = df[df.index.date == dates[di - 1]]
        cur = df[df.index.date == day]
        pre = cur[cur.index.time <= time(9, 25)]
        if prev.empty or pre.empty:
            continue
        ph, pl = prev["nh"].max(), prev["nl"].min()
        long_side = pre["nc"].iloc[-1] < (ph + pl) / 2
        sign = 1 if long_side else -1
        # mirror shorts into longs by negating and swapping highs/lows
        nh = (cur["nh"] if long_side else -cur["nl"]).to_numpy()
        nl = (cur["nl"] if long_side else -cur["nh"]).to_numpy()
        nc = (sign * cur["nc"]).to_numpy()
        el = (cur["el"] if long_side else -cur["eh"]).to_numpy()
        t = cur.index.time
        idxs = [i for i in range(len(cur)) if WIN_START <= t[i] <= WIN_END]
        end_idx = max(i for i in range(len(cur)) if t[i] <= FLAT)
        s = find_long_setup(nh, nl, nc, el, idxs)
        if s is None:
            continue
        risk = s.entry - s.stop
        prev_high = ph if long_side else -pl
        tg = {"2R": s.entry + 2 * risk, "3R": s.entry + 3 * risk,
              "liq": liquidity_target(nh, s, 0, prev_high)}
        for k, v in tg.items():
            r = simulate_long(nh, nl, nc, end_idx, s, v)
            if r is not None:
                results[k].append(r)
        infos.append((cur, idxs, end_idx, s, sign))

    print(f"Sessions scanned: {len(dates) - 1}  setups found: {len(infos)}")
    for k, rs in results.items():
        n = len(rs)
        if n == 0:
            print(f"[{k}] no trades")
            continue
        w = sum(r > 0 for r in rs)
        lo, hi = wilson(w, n)
        gp = sum(r for r in rs if r > 0)
        gl = -sum(r for r in rs if r < 0)
        eq, peak, dd = 0.0, 0.0, 0.0
        for r in rs:
            eq += r
            peak = max(peak, eq)
            dd = max(dd, peak - eq)
        pf = gp / gl if gl else float("inf")
        print(f"[{k}] trades={n} win={w / n:.1%} (95% CI {lo:.0%}-{hi:.0%}) "
              f"avgR={sum(rs) / n:+.2f} PF={pf:.2f} maxDD={dd:.1f}R")

    rng = random.Random(seed)
    for mult, key in ((2, "2R"), (3, "3R")):
        if not results[key]:
            continue
        strat = sum(results[key]) / len(results[key])
        exps = []
        for _ in range(draws):
            rs = []
            for cur, idxs, end_idx, s, sign in infos:
                nh = (cur["nh"] if sign == 1 else -cur["nl"]).to_numpy()
                nl = (cur["nl"] if sign == 1 else -cur["nh"]).to_numpy()
                nc = (sign * cur["nc"]).to_numpy()
                b = rng.choice(idxs[:-1])
                e = nc[b]
                risk = s.entry - s.stop
                fake = Setup(b + 1, e, e - risk, b)
                r = simulate_long(nh, nl, nc, end_idx, fake, e + mult * risk)
                if r is not None:
                    rs.append(r)
            if rs:
                exps.append(sum(rs) / len(rs))
        pct = sum(x < strat for x in exps) / len(exps)
        print(f"[{key}] strategy avgR {strat:+.2f} beats {pct:.0%} of {len(exps)} random-entry draws")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=59)
    ap.add_argument("--draws", type=int, default=1000)
    a = ap.parse_args()
    run(load(a.days), a.draws)
