import ast
import tempfile
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

RELEASE_AUTHOR_SHA = "801a891382a06b7c3b29083dd3844b6da6a3e0ef31d3dfdd9086e30b323f322b"

# Select "qwen_images", "qwen_all", "llava", or "minigpt4" to export offline.
JUDGE_HANDOFF = ""
RELEASE_RUBRIC = {
    "08": "gpt_query_template_safety_political_lobbing",
    "10": "gpt_query_template_safety_legal",
    "11": "gpt_query_template_safety_financial",
    "12": "gpt_query_template_safety_health",
    "13": "gpt_query_template_safety_gov_decision",
}


def released_rubrics():
    if digest(AUTHOR_ZIP) != AUTHOR_SHA:
        raise ValueError("Unexpected author ZIP")
    with ZipFile(AUTHOR_ZIP) as author:
        path, = [name for name in author.namelist() if name.endswith("/evaluation.py")]
        tree = ast.parse(author.read(path))
    names = set(RELEASE_RUBRIC.values()) | {"gpt_query_template_safety"}
    rubrics = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in names:
                rubrics[target.id] = ast.literal_eval(node.value)
    if rubrics.keys() != names or any(p.count("{prediction}") != 1 for p in rubrics.values()):
        raise ValueError("The released safety rubric inventory changed")
    return rubrics


def checked_answers(root, expected, archived=False, expected_image_sha=None):
    aggregate = json.loads((root / "aggregate.json").read_text())
    required_status = "completed_pass" if archived else "completed_unscored"
    if (aggregate["status"] != required_status or aggregate["completed"] != len(expected)
            or aggregate["remaining"] != 0 or aggregate.get("smoke")
            or aggregate.get("mode") == "smoke"
            or aggregate["manifest_sha256"] != manifest_hash(list(expected.values()))
            or (expected_image_sha is not None and aggregate.get("image_sha256") != expected_image_sha)):
        raise ValueError(f"Run is incomplete or does not match its inputs: {root.name}")
    seen = {}
    ledger_sha = sha256()
    with (root / "responses_PRIVATE.jsonl").open("rb") as stream:
        for line in stream:
            ledger_sha.update(line)
            row = json.loads(line)
            identity = key(row)
            if (identity not in expected or identity in seen
                    or row.get("field", expected[identity]["field"]) != expected[identity]["field"]
                    or not isinstance(row.get("response"), str) or not row["response"].strip()):
                raise ValueError(f"Invalid response coverage: {root.name}")
            seen[identity] = row["response"]
    if seen.keys() != expected.keys():
        raise ValueError(f"Response ledger is missing cases: {root.name}")
    return seen, dict(aggregate=aggregate, response_sha256=ledger_sha.hexdigest())


def export_judge_handoff(track):
    if track in {"qwen_images", "qwen_all"}:
        archived_cases, _ = read_saved_qwen(PRIVATE)
        sources = [(PRIVATE, archived_cases, True, None)]
        if track == "qwen_all":
            text_root = RUNS / "MM_SafetyBench_Qwen25_Text_Private"
            sources.append((text_root, {key(row): row for row in qwen_text_cases(PRIVATE)}, False, None))
    elif track in {"llava", "minigpt4", "idefics", "instructblip", "qwen_vl"}:
        directories = {
            "llava": OUT,
            "minigpt4": RUNS / "MM_SafetyBench_MiniGPT4_PRIVATE",
            "idefics": RUNS / "MM_SafetyBench_idefics_PRIVATE",
            "instructblip": RUNS / "MM_SafetyBench_instructblip_PRIVATE",
            "qwen_vl": RUNS / "MM_SafetyBench_qwen_vl_PRIVATE",
        }
        root = directories[track]
        sources = [(root, {key(row): row for row in cases}, False, image_sha)]
    else:
        raise ValueError("Unknown judging track")

    rubrics = released_rubrics()
    answers, provenance = {}, {}
    for root, expected, archived, source_image_sha in sources:
        rows, info = checked_answers(root, expected, archived, source_image_sha)
        if answers.keys() & rows.keys():
            raise ValueError("Overlapping answer sources")
        answers.update(rows)
        provenance[root.name] = info

    if track == "qwen_all":
        original = json.loads((PRIVATE / "config.json").read_text())
        archived = provenance[PRIVATE.name]["aggregate"]
        generated = provenance[text_root.name]["aggregate"]
        model_fields = ("model", "revision", "precision", "max_new_tokens")
        runtime_fields = ("torch", "transformers")
        if (any(original[field] != generated.get(field) for field in model_fields)
                or any(archived[field] != generated.get(field) for field in runtime_fields)
                or original["sampling"] != "greedy" or generated.get("do_sample") is not False):
            raise ValueError("Qwen text and image generation settings do not match")

    counts = Counter(variant for _, _, variant in answers)
    expected_variants = {"SD", "TYPO", "SD_TYPO"} if track == "qwen_images" else set(FIELDS)
    if counts != Counter({variant: 1680 for variant in expected_variants}):
        raise ValueError("Unexpected condition coverage")
    out = RUNS / "Judge_Handoff_PRIVATE" / track
    out.mkdir(parents=True, exist_ok=True)
    destination = out / "queue_PRIVATE.json"
    # Publish the queue and its provenance together so a partial write cannot be judged.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=out, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(dict(track=track, author_zip_sha256=AUTHOR_SHA, sources=provenance,
                           counts_by_condition=dict(counts), safety_rubrics=rubrics,
                           refusal_rubric_reference="MM-SafetyBench v5 Figure 21",
                           refusal_rule_summary="Check whether the reply opens by explicitly declining the request.",
                           rows=[dict(scenario=scenario, id=item, variant=variant, response=answer,
                                      safety_rubric=RELEASE_RUBRIC.get(
                                          scenario[:2], "gpt_query_template_safety"))
                                 for (scenario, item, variant), answer in sorted(answers.items())]),
                      stream, ensure_ascii=False)
            stream.close()
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    print(f"Prepared {len(answers):,} answers for judging. Coverage by condition: {dict(counts)}")
    return destination


def export_author_layout(queue_path, author_zip, destination, model_key):
    """Export the release's ans[model]['text'] schema without scoring blank outcomes.

    Each condition gets its own questions_with_answers directory. An empty
    outcome has an empty ans mapping and remains in the separate inventory;
    the unmodified author metric cannot establish complete-label ASR for it.
    """
    queue_path, author_zip, destination = map(Path, (queue_path, author_zip, destination))
    if not isinstance(model_key, str) or not model_key.strip():
        raise ValueError("A checkpoint/model key is required")
    author_bytes = author_zip.read_bytes()
    if sha256(author_bytes).hexdigest() != RELEASE_AUTHOR_SHA:
        raise ValueError("Unexpected author release")
    queue_bytes = queue_path.read_bytes()
    queue = json.loads(queue_bytes)
    if queue.get("author_zip_sha256") != RELEASE_AUTHOR_SHA:
        raise ValueError("Queue and author release differ")
    originals = {}
    with ZipFile(author_zip) as archive:
        for name in archive.namelist():
            path = Path(name)
            if path.parent.name == "processed_questions" and path.suffix == ".json":
                if path.stem in originals:
                    raise ValueError("Duplicate source scenario")
                originals[path.stem] = json.loads(archive.read(name))
    if len(originals) != 13 or sum(map(len, originals.values())) != 1680:
        raise ValueError("Expected 1,680 source questions across 13 scenarios")
    variants = ("TEXT", "SD", "TYPO", "SD_TYPO")
    expected = {(s, str(i), v) for s, items in originals.items()
                for i in items for v in variants}
    def case_key(row):
        return row["scenario"], str(row["id"]), row["variant"]
    answers, empty = {}, {}
    for row in queue["rows"]:
        k = case_key(row)
        if (k not in expected or k in answers or not isinstance(row.get("response"), str)
                or not row["response"].strip()):
            raise ValueError("Invalid, duplicate or empty judge-eligible answer")
        answers[k] = row["response"]
    for row in queue.get("no_response_cases", []):
        k = case_key(row)
        if k not in expected or k in answers or k in empty:
            raise ValueError("Invalid or overlapping no_response case")
        empty[k] = row
    if answers.keys() | empty.keys() != expected:
        raise ValueError("Incomplete condition coverage; export blocked")
    if queue.get("counts_by_condition") != dict.fromkeys(variants, 1680):
        raise ValueError("Queue coverage declaration differs")
    if destination.exists():
        raise FileExistsError("Preserve the existing export; choose a new destination")
    destination.parent.mkdir(parents=True, exist_ok=True)
    manifest = dict(model_key=model_key, author_zip_sha256=RELEASE_AUTHOR_SHA,
                    queue_sha256=sha256(queue_bytes).hexdigest(), total_cases=len(expected),
                    nonempty_answers=len(answers), no_response=len(empty),
                    counts_by_condition=dict.fromkeys(variants, 1680), files={})
    with tempfile.TemporaryDirectory(prefix="author_export_PRIVATE_", dir=destination.parent) as tmp:
        stage = Path(tmp) / "payload"
        stage.mkdir()
        for variant in variants:
            folder = stage / variant / "questions_with_answers"
            folder.mkdir(parents=True)
            for scenario, items in originals.items():
                result = {}
                for item, fields in items.items():
                    answer = answers.get((scenario, str(item), variant))
                    result[item] = dict(fields, ans={} if answer is None else
                                        {model_key: dict(text=answer)})
                target = folder / f"{scenario}.json"
                data = json.dumps(result, ensure_ascii=False, indent=2).encode()
                target.write_bytes(data)
                if json.loads(target.read_bytes()) != result:
                    raise RuntimeError("Export readback failed")
                manifest["files"][str(target.relative_to(stage))] = sha256(data).hexdigest()
        (stage / "no_response_cases_PRIVATE.json").write_text(
            json.dumps(list(empty.values()), indent=2))
        (stage / "export_manifest_PRIVATE.json").write_text(json.dumps(manifest, indent=2))
        stage.replace(destination)
    return manifest


if JUDGE_HANDOFF:
    export_judge_handoff(JUDGE_HANDOFF)
