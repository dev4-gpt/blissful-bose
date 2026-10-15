"""Tests for the cross-benchmark analysis helpers, using small hand-checkable tables."""

import math

import pytest

from src.eval import analyze as an


# ---- cluster bootstrap ----------------------------------------------------

def test_cluster_bootstrap_point_estimate_and_determinism():
    clusters = ["a", "a", "b", "b", "c", "c"]
    successes = [True, False, True, True, False, False]
    r1 = an.cluster_bootstrap_ci(clusters, successes, n_boot=500, seed=3)
    r2 = an.cluster_bootstrap_ci(clusters, successes, n_boot=500, seed=3)
    assert r1 == r2
    point, lo, hi = r1
    assert point == pytest.approx(3 / 6)
    assert lo <= point <= hi


def test_cluster_bootstrap_all_successes_is_degenerate():
    assert an.cluster_bootstrap_ci(["a", "b"], [True, True], n_boot=200, seed=0) == (1.0, 1.0, 1.0)


def test_cluster_bootstrap_two_clusters_spans_zero_to_one():
    clusters = ["A"] * 4 + ["B"] * 4
    successes = [True] * 4 + [False] * 4
    point, lo, hi = an.cluster_bootstrap_ci(clusters, successes, n_boot=2000, seed=1)
    assert point == 0.5 and lo == 0.0 and hi == 1.0


def test_cluster_bootstrap_rejects_empty_input():
    with pytest.raises(ValueError):
        an.cluster_bootstrap_ci([], [])


# ---- rate table -----------------------------------------------------------

def test_rate_table_groups_counts_and_rates():
    recs = [
        {"benchmark": "X", "state": "UiSt", "cluster": "i1", "success": True},
        {"benchmark": "X", "state": "UiSt", "cluster": "i1", "success": False},
        {"benchmark": "X", "state": "UiSt", "cluster": "i2", "success": True},
        {"benchmark": "X", "state": "SiUt", "cluster": "i3", "success": False},
    ]
    table = an.rate_table(recs, keys=("benchmark", "state"), n_boot=200, seed=0)
    by_state = {row["state"]: row for row in table}
    assert by_state["UiSt"]["n"] == 3 and by_state["UiSt"]["n_clusters"] == 2
    assert by_state["UiSt"]["rate"] == pytest.approx(2 / 3)
    assert by_state["SiUt"]["rate"] == 0.0
    assert [r["state"] for r in table] == ["SiUt", "UiSt"]  # sorted, deterministic order


# ---- McNemar / paired comparison -----------------------------------------

@pytest.mark.parametrize("b,c,expected", [
    (0, 0, 1.0),
    (5, 0, 0.0625),            # 2 * C(5,0) / 2^5
    (3, 3, 1.0),               # symmetric, capped at 1
    (8, 2, 0.109375),          # 2 * (1+10+45) / 2^10
])
def test_mcnemar_exact_known_values(b, c, expected):
    assert an.mcnemar_exact(b, c) == pytest.approx(expected)


def test_paired_comparison_counts_odds_ratio_and_kappa():
    a = {1: True, 2: True, 3: False, 4: False}
    b = {1: True, 2: False, 3: False, 4: False}
    res = an.paired_comparison(a, b)
    assert (res["n_pairs"], res["n11"], res["n10"], res["n01"], res["n00"]) == (4, 1, 1, 0, 2)
    assert res["odds_ratio"] == pytest.approx((1 + 0.5) / (0 + 0.5))
    assert res["kappa"] == pytest.approx(0.5)
    assert res["p_value"] == pytest.approx(1.0)  # one discordant pair cannot be significant


def test_paired_comparison_uses_only_shared_keys():
    res = an.paired_comparison({1: True, 2: False, 9: True}, {1: True, 2: False, 8: False})
    assert res["n_pairs"] == 2


def test_kappa_is_nan_when_undefined():
    res = an.paired_comparison({1: True, 2: True}, {1: True, 2: True})
    assert math.isnan(res["kappa"])


# ---- Spearman and rank stability -----------------------------------------

def test_spearman_known_values_including_ties():
    assert an.spearman([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)
    assert an.spearman([1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)
    assert an.spearman([1, 1, 2], [1, 2, 3]) == pytest.approx(1.5 / math.sqrt(3))


def test_spearman_degenerate_inputs_return_nan():
    assert math.isnan(an.spearman([1], [1]))
    assert math.isnan(an.spearman([1, 1, 1], [1, 2, 3]))
    with pytest.raises(ValueError):
        an.spearman([1, 2], [1, 2, 3])


def test_rank_stability_needs_at_least_three_common_models():
    two = {"B1": {"m1": 0.2, "m2": 0.5}, "B2": {"m1": 0.1, "m2": 0.9}}
    assert math.isnan(an.rank_stability(two)[("B1", "B2")])
    three = {"B1": {"m1": 0.2, "m2": 0.5, "m3": 0.8}, "B2": {"m1": 0.1, "m2": 0.4, "m3": 0.9}}
    assert an.rank_stability(three)[("B1", "B2")] == pytest.approx(1.0)


# ---- image-level paired difference and the unpaired fallback ---------------

import json  # noqa: E402


def _recs(rows):
    return [{"state": s, "cluster": c, "success": v} for s, c, v in rows]


def test_image_level_difference_known_answer_and_only_shared_clusters():
    recs = _recs([
        ("UiSt", "c1", True), ("UiSt", "c1", True), ("UiUt", "c1", False),   # c1: a=1.0 b=0.0
        ("UiSt", "c2", True), ("UiUt", "c2", True),                          # c2: a=1.0 b=1.0
        ("UiSt", "c3", False), ("UiUt", "c3", False),                        # c3: a=0.0 b=0.0
        ("UiSt", "c4", True),                                                # c4 has no UiUt: excluded
    ])
    res = an.image_level_difference(recs, "UiSt", "UiUt", n_boot=500, seed=0)
    assert res["n_clusters"] == 3
    assert res["rate_a"] == pytest.approx(2 / 3) and res["rate_b"] == pytest.approx(1 / 3)
    assert res["diff"] == pytest.approx(1 / 3)
    assert res["lo"] <= res["diff"] <= res["hi"]
    assert res == an.image_level_difference(recs, "UiSt", "UiUt", n_boot=500, seed=0)


def test_image_level_difference_raises_when_no_cluster_has_both_conditions():
    recs = _recs([("UiSt", "c1", True), ("UiUt", "c2", False)])
    with pytest.raises(ValueError, match="both"):
        an.image_level_difference(recs, "UiSt", "UiUt")


def test_unpaired_difference_known_answer():
    recs = _recs([("A", "c1", True), ("A", "c2", True), ("B", "c3", False), ("B", "c4", False)])
    res = an.unpaired_difference(recs, "A", "B", n_boot=300, seed=0)
    assert (res["rate_a"], res["rate_b"], res["diff"]) == (1.0, 0.0, 1.0)
    assert (res["lo"], res["hi"]) == (1.0, 1.0)
    assert res["n_clusters_a"] == 2 and res["n_clusters_b"] == 2


# ---- agreement with human labels (calibration of string match and judges) ---

def test_agreement_metrics_known_confusion():
    res = an.agreement_metrics([True, True, False, False], [True, False, False, True])
    assert (res["tp"], res["fp"], res["fn"], res["tn"]) == (1, 1, 1, 1)
    assert res["precision"] == 0.5 and res["recall"] == 0.5 and res["accuracy"] == 0.5
    assert res["kappa"] == pytest.approx(0.0)
    assert an.agreement_metrics([True, False], [True, False])["kappa"] == pytest.approx(1.0)


def test_agreement_metrics_undefined_precision_is_nan_and_lengths_are_checked():
    res = an.agreement_metrics([False, False], [True, False])
    assert math.isnan(res["precision"]) and res["recall"] == 0.0
    with pytest.raises(ValueError):
        an.agreement_metrics([True], [True, False])


def test_calibration_by_group_splits_by_state():
    rows = [{"state": "UiSt", "sm": True, "human": True}, {"state": "UiSt", "sm": False, "human": True},
            {"state": "SiStS", "sm": True, "human": False}]
    table = {r["state"]: r for r in an.calibration_by_group(rows, "state", "sm", "human")}
    assert table["UiSt"]["recall"] == 0.5 and table["UiSt"]["n"] == 2
    assert table["SiStS"]["fp"] == 1


# ---- loading saved responses and judgments; the command-line report ---------

def _write_jsonl(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def _fixture(tmp_path):
    def resp(i, text, state, cluster):
        return {"id": f"h/{i}", "benchmark_name": "HoliSafe-Bench", "response": text,
                "meta": {"state": state, "cluster": cluster}}

    def judg(i, expected, adherent, sm):
        return {"id": f"h/{i}", "expected": expected, "adherent": adherent,
                "string_match_paper": sm, "string_match_strict": sm}

    r, j = tmp_path / "responses.jsonl", tmp_path / "judgments.jsonl"
    _write_jsonl(r, [resp(1, "Sure, here you go.", "UiSt", "img1"), resp(2, "I can't help with that.", "UiSt", "img2"),
                     resp(3, "A helpful answer.", "SiStS", "img3"), resp(4, "Another answer.", "UiSt", "img4"),
                     resp(5, "Sure.", "UiUt", "img1")])
    _write_jsonl(j, [judg(1, "unsafe", False, "non_refusal"), judg(2, "unsafe", True, "refusal"),
                     judg(3, "safe", True, "non_refusal"), judg(4, "unsafe", None, "non_refusal"),
                     judg(5, "unsafe", False, "non_refusal")])
    return r, j


def test_load_joined_and_summarize_report_rates_and_exclusions(tmp_path):
    records = an.load_joined(*_fixture(tmp_path))
    assert len(records) == 5 and records[0]["cluster"] == "img1"
    table, excluded = an.summarize(records, "judge", ("benchmark", "state"), n_boot=200, seed=0)
    by = {r["state"]: r for r in table}
    assert by["UiSt"]["n"] == 2 and by["UiSt"]["rate"] == 0.5   # unparsed h/4 is excluded, not guessed
    assert by["SiStS"]["rate"] == 0.0 and excluded == 1
    table_sm, excluded_sm = an.summarize(records, "string_paper", ("benchmark", "state"), n_boot=200, seed=0)
    assert {r["state"]: r["n"] for r in table_sm}["UiSt"] == 3 and excluded_sm == 0
    assert {r["state"]: r["rate"] for r in table_sm}["UiSt"] == pytest.approx(2 / 3)


def test_main_prints_table_exclusions_csv_and_image_level_comparison(tmp_path, capsys):
    r, j = _fixture(tmp_path)
    csv_path = tmp_path / "table.csv"
    code = an.main(["--responses", str(r), "--judgments", str(j), "--csv", str(csv_path),
                    "--n-boot", "100", "--compare", "UiSt", "UiUt"])
    out = capsys.readouterr().out
    assert code == 0
    assert "UiSt" in out and "excluded" in out.lower() and "image-level" in out.lower()
    assert csv_path.read_text().splitlines()[0].startswith("benchmark,state,n,n_clusters,rate")
