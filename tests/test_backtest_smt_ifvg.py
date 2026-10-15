import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import backtest_smt_ifvg as bt  # noqa: E402


def test_wilson_bounds():
    lo, hi = bt.wilson(7, 10)
    assert 0.35 < lo < 0.7 < hi < 0.93
    assert bt.wilson(0, 0) == (0.0, 0.0)


def test_smt_bull_requires_es_to_hold():
    nl = [10.0] * 12 + [9.0]
    assert bt.smt_bull(nl, [10.0] * 12 + [10.0], 12)
    assert not bt.smt_bull(nl, [10.0] * 12 + [8.0], 12)


def test_bearish_fvg_top():
    nh = [0, 0, 5.0]
    nl = [8.0, 0, 0]
    assert bt.bearish_fvg_top(nh, nl, 2) == 8.0
    assert bt.bearish_fvg_top([0, 0, 9.0], nl, 2) is None


def _setup():
    return bt.Setup(entry_idx=0, entry=100.0, stop=90.0, smt_idx=0)


def test_simulate_long_target_and_stop():
    s = _setup()
    cost = 2 * bt.TICK + bt.COMMISSION_PTS
    r = bt.simulate_long([100, 125], [100, 99], [100, 120], 1, s, 120.0)
    assert abs(r - (20 - cost) / 10) < 1e-9
    r = bt.simulate_long([100, 105], [100, 89], [100, 95], 1, s, 120.0)
    assert r < 0


def test_simulate_long_stop_wins_tie_and_no_target():
    s = _setup()
    assert bt.simulate_long([100, 130], [100, 85], [100, 100], 1, s, 120.0) < 0
    assert bt.simulate_long([100], [100], [100], 0, s, None) is None
