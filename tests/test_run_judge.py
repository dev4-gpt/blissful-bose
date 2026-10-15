"""Tests for the judge runner. No model, no network; judge behaviour is faked."""

import json
from pathlib import Path

import pytest

from src.eval import benchmark_loaders as bl
from src.eval import run_judge as rj


def _write_responses(path: Path, ids, state=None):
    rows = [{"id": i, "response": "Placeholder reply", "meta": ({"state": state} if state else {})} for i in ids]
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def _args(responses, out, *extra):
    return ["--responses", str(responses), "--synthetic", "--expected", "unsafe", "--out", str(out), *extra]


def test_expected_for_uses_state_when_asked():
    assert rj.expected_for({"meta": {"state": "SiStS"}}, "from-state") == "safe"
    assert rj.expected_for({"meta": {"state": "UiSt"}}, "from-state") == "unsafe"


def test_expected_for_requires_a_state_when_from_state():
    with pytest.raises(ValueError, match="state"):
        rj.expected_for({"meta": {}}, "from-state")


def test_expected_for_accepts_fixed_value_only_without_a_state():
    assert rj.expected_for({"meta": {}}, "unsafe") == "unsafe"
    with pytest.raises(ValueError, match="conflict"):
        rj.expected_for({"meta": {"state": "SiStS"}}, "unsafe")


def test_join_reports_missing_items():
    items = bl.synthetic_items()
    rows = [{"id": items[0].id, "response": "r", "meta": {}}, {"id": "ghost/1", "response": "r", "meta": {}}]
    pairs, missing = rj.join_responses(rows, items)
    assert [r["id"] for r, _ in pairs] == [items[0].id]
    assert missing == ["ghost/1"]


def test_dry_run_matches_responses_and_writes_nothing(tmp_path: Path, capsys):
    responses, out = tmp_path / "responses.jsonl", tmp_path / "judgments.jsonl"
    _write_responses(responses, [it.id for it in bl.synthetic_items()])
    assert rj.main(_args(responses, out, "--mode", "text", "--dry-run")) == 0
    assert not out.exists()
    assert "Dry run OK" in capsys.readouterr().out


def test_vision_mode_fails_fast_when_an_item_has_no_image(tmp_path: Path):
    responses, out = tmp_path / "responses.jsonl", tmp_path / "judgments.jsonl"
    _write_responses(responses, [it.id for it in bl.synthetic_items()])  # text-channel items have no image
    with pytest.raises(ValueError, match="image"):
        rj.main(_args(responses, out, "--mode", "vision", "--dry-run"))


def test_never_fabricates_judgments_when_the_model_cannot_load(tmp_path: Path, monkeypatch):
    def boom(args):
        raise RuntimeError("judge model could not be loaded")

    monkeypatch.setattr(rj, "load_judge_model", boom)
    responses, out = tmp_path / "responses.jsonl", tmp_path / "judgments.jsonl"
    _write_responses(responses, [it.id for it in bl.synthetic_items()])
    with pytest.raises(RuntimeError, match="could not be loaded"):
        rj.main(_args(responses, out, "--mode", "text"))
    assert not out.exists()


def test_writes_rows_with_parsed_label_raw_text_and_string_matches_and_resumes(tmp_path: Path, monkeypatch):
    items = bl.synthetic_items()
    ids = [it.id for it in items]
    responses, out = tmp_path / "responses.jsonl", tmp_path / "judgments.jsonl"
    _write_responses(responses, ids)
    out.write_text(json.dumps({"id": ids[0]}) + "\n")  # already judged: must be skipped
    calls = []

    def fake_loader(args):
        def judge(prompt, item):
            calls.append(item.id)
            return "<label>False</label>" if item.id == ids[1] else "no tag here"
        return judge

    monkeypatch.setattr(rj, "load_judge_model", fake_loader)
    assert rj.main(_args(responses, out, "--mode", "text")) == 0
    assert calls == ids[1:]
    rows = {json.loads(l)["id"]: json.loads(l) for l in out.read_text().splitlines() if l.strip()}
    assert set(rows) == set(ids)
    assert rows[ids[1]]["adherent"] is False and rows[ids[1]]["expected"] == "unsafe"
    assert rows[ids[2]]["adherent"] is None and rows[ids[2]]["raw"] == "no tag here"  # unparsed is kept, not guessed
    assert rows[ids[1]]["string_match_paper"] == "non_refusal" and "string_match_strict" in rows[ids[1]]
