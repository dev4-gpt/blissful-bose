"""Tests for benchmark loaders and the resume-safe VLM runner.

All rows are synthetic placeholders with neutral text; no real benchmark data,
no GPU, no network.
"""

import json
from pathlib import Path

import pytest
from PIL import Image

from src.eval import benchmark_loaders as bl
from src.eval import run_vlm_eval as rv


def _img():
    return Image.new("RGB", (8, 8), (200, 200, 200))


# ---- MM-SafetyBench -------------------------------------------------------

def test_mmsafety_rows_map_to_items_with_channel_metadata():
    rows = [{"id": str(i), "question": f"Placeholder question {i}", "image": _img()} for i in range(3)]
    items = bl.mmsafety_rows_to_items(rows, scenario="Fraud", variant="TYPO")
    assert len(items) == 3
    assert len({it.id for it in items}) == 3
    assert all(it.benchmark_name == "MM-SafetyBench" for it in items)
    assert items[0].metadata["channel"] == "image_typo"
    assert items[0].metadata["scenario"] == "Fraud"
    assert items[0].image is not None


def test_mmsafety_text_only_variant_has_no_image():
    rows = [{"id": "0", "question": "Placeholder question", "image": None}]
    items = bl.mmsafety_rows_to_items(rows, scenario="Fraud", variant="Text_only")
    assert items[0].image is None
    assert items[0].metadata["channel"] == "text"


def test_mmsafety_unknown_variant_raises():
    with pytest.raises(ValueError, match="variant"):
        bl.mmsafety_rows_to_items([], scenario="Fraud", variant="NOT_A_VARIANT")


# ---- VLSBench -------------------------------------------------------------

def test_vlsbench_rows_map_to_items():
    rows = [{"instruction_id": i, "instruction": f"Placeholder instruction {i}", "image": _img(),
             "category": "cat", "sub_category": "sub", "source": "src"} for i in range(2)]
    items = bl.vlsbench_rows_to_items(rows)
    assert [it.id for it in items] == ["vlsbench/0", "vlsbench/1"]
    assert items[0].metadata["category"] == "cat"
    assert items[0].benchmark_name == "VLSBench"


# ---- HoliSafe: schema is unverified (gated), so mappings must be explicit ---

COLMAP = {"id": "uid", "prompt": "query", "image": "img", "state": "label", "category": "cat"}
STATEMAP = {"a": "UiUt", "b": "UiSt", "c": "SiUt", "d": "SiStU", "e": "SiStS"}


def _holi_row(i, label="a"):
    return {"uid": f"h{i}", "query": f"Placeholder query {i}", "img": _img(), "label": label, "cat": "c1"}


def test_holisafe_maps_with_explicit_column_and_state_maps():
    items = bl.holisafe_rows_to_items([_holi_row(0, "b")], COLMAP, STATEMAP)
    assert items[0].metadata["state"] == "UiSt"
    assert items[0].id == "holisafe/h0"


def test_holisafe_missing_column_raises_naming_the_column():
    row = _holi_row(0)
    del row["label"]
    with pytest.raises(KeyError, match="label"):
        bl.holisafe_rows_to_items([row], COLMAP, STATEMAP)


def test_holisafe_unknown_state_label_raises_instead_of_guessing():
    with pytest.raises(ValueError, match="state"):
        bl.holisafe_rows_to_items([_holi_row(0, "zzz")], COLMAP, STATEMAP)


def test_holisafe_state_map_must_target_canonical_states():
    with pytest.raises(ValueError, match="canonical"):
        bl.holisafe_rows_to_items([_holi_row(0)], COLMAP, {"a": "not-a-state"})


# ---- Stratified sampling and manifests -----------------------------------

def _items(n_per_state=10):
    rows = []
    for s_label in STATEMAP:
        for i in range(n_per_state):
            rows.append(_holi_row(f"{s_label}{i}", s_label))
    return bl.holisafe_rows_to_items(rows, COLMAP, STATEMAP)


def _key(it):
    return it.metadata["state"]


def test_stratified_sample_is_deterministic_and_balanced():
    items = _items()
    s1, short1 = bl.stratified_sample(items, _key, n_per_stratum=4, seed=7)
    s2, _ = bl.stratified_sample(items, _key, n_per_stratum=4, seed=7)
    s3, _ = bl.stratified_sample(items, _key, n_per_stratum=4, seed=8)
    assert [i.id for i in s1] == [i.id for i in s2]
    assert [i.id for i in s1] != [i.id for i in s3]
    assert short1 == {}
    counts = {}
    for it in s1:
        counts[_key(it)] = counts.get(_key(it), 0) + 1
    assert set(counts.values()) == {4} and len(counts) == 5


def test_stratified_sample_reports_shortfall_instead_of_silently_shrinking():
    items = _items(n_per_state=3)
    sample, short = bl.stratified_sample(items, _key, n_per_stratum=5, seed=0)
    assert len(sample) == 15
    assert short == {s: 2 for s in ["UiUt", "UiSt", "SiUt", "SiStU", "SiStS"]}


def test_manifest_roundtrip_hash_and_no_prompt_text(tmp_path: Path):
    items = _items(2)
    path = tmp_path / "manifest.jsonl"
    bl.write_manifest(items, path, _key)
    rows = bl.read_manifest(path)
    assert [r["id"] for r in rows] == [i.id for i in items]
    assert rows[0]["stratum"] == _key(items[0])
    raw = path.read_text()
    assert "Placeholder query" not in raw  # manifest holds ids only, never prompt text
    h1 = bl.manifest_sha256(path)
    bl.write_manifest(items, path, _key)
    assert bl.manifest_sha256(path) == h1


# ---- Runner ---------------------------------------------------------------

def test_done_ids_reads_resume_file(tmp_path: Path):
    out = tmp_path / "responses.jsonl"
    assert rv.done_ids(out) == set()
    out.write_text(json.dumps({"id": "a"}) + "\n\n" + json.dumps({"id": "b"}) + "\n")
    assert rv.done_ids(out) == {"a", "b"}


def test_build_messages_with_and_without_image():
    with_img = bl.mmsafety_rows_to_items(
        [{"id": "0", "question": "Placeholder question", "image": _img()}], "Fraud", "SD")[0]
    no_img = bl.mmsafety_rows_to_items(
        [{"id": "0", "question": "Placeholder question", "image": None}], "Fraud", "Text_only")[0]
    m1 = rv.build_messages(with_img, system_prompt="Be helpful.")
    assert m1[0]["role"] == "system"
    assert {"type": "image"} in m1[-1]["content"]
    m2 = rv.build_messages(no_img)
    assert m2[0]["role"] == "user"
    assert all(c["type"] == "text" for c in m2[-1]["content"])


def test_dry_run_with_synthetic_items_needs_no_gpu_or_data(tmp_path: Path, capsys):
    out = tmp_path / "responses.jsonl"
    code = rv.main(["--synthetic", "--dry-run", "--out", str(out)])
    assert code == 0
    assert not out.exists()  # dry run writes nothing
    assert "Dry run OK" in capsys.readouterr().out


def test_runner_never_fabricates_responses_when_model_cannot_load(tmp_path: Path, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("model could not be loaded")

    monkeypatch.setattr(rv, "load_model", boom)
    out = tmp_path / "responses.jsonl"
    with pytest.raises(RuntimeError, match="could not be loaded"):
        rv.main(["--synthetic", "--model", "any/model", "--out", str(out)])
    assert not out.exists()  # no simulated or partial output is ever written


# ---- cluster / pairing keys ----------------------------------------------

def test_mmsafety_items_carry_a_question_level_cluster_and_pair_key():
    rows = [{"id": "7", "question": "Placeholder question", "image": None}]
    a = bl.mmsafety_rows_to_items(rows, "Fraud", "Text_only")[0]
    b = bl.mmsafety_rows_to_items(rows, "Fraud", "TYPO")[0]
    assert a.metadata["cluster"] == b.metadata["cluster"] == "Fraud/7"
    assert a.metadata["pair_key"] == "Fraud/7"


def test_vlsbench_cluster_uses_image_path_when_present_else_the_item_id():
    with_path = bl.vlsbench_rows_to_items(
        [{"instruction_id": 1, "instruction": "p", "image": None, "image_path": "imgs/a.png", "category": "c"}])[0]
    without = bl.vlsbench_rows_to_items(
        [{"instruction_id": 2, "instruction": "p", "image": None, "category": "c"}])[0]
    assert with_path.metadata["cluster"] == "imgs/a.png"
    assert without.metadata["cluster"] == "vlsbench/2"


def test_holisafe_cluster_comes_from_the_optional_cluster_column_else_the_item_id():
    cmap = {**COLMAP, "cluster": "img_path"}
    row = {**_holi_row(0), "img_path": "a/b.png"}
    assert bl.holisafe_rows_to_items([row], cmap, STATEMAP)[0].metadata["cluster"] == "a/b.png"
    assert bl.holisafe_rows_to_items([_holi_row(1)], COLMAP, STATEMAP)[0].metadata["cluster"] == "holisafe/h1"
    with pytest.raises(KeyError, match="img_path"):
        bl.holisafe_rows_to_items([_holi_row(2)], cmap, STATEMAP)


def test_runner_keeps_cluster_and_pair_key_in_saved_metadata():
    assert {"cluster", "pair_key"} <= set(rv.KEPT_META)
