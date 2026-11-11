"""Build the approved reference runner that records empty completions explicitly."""
import ast
from pathlib import Path


def with_no_response(runtime):
    replacements = {
        'or not row["response"].strip() or row.get("identity_sha256") != fingerprint(identity)':
        'or row.get("response_status") != ("answer" if row["response"].strip() else "no_response") '
        'or row.get("identity_sha256") != fingerprint(identity)',
        'if not isinstance(answer, str) or not answer.strip():\n                raise ValueError("Empty model completion")':
        'if not isinstance(answer, str):\n                raise TypeError("Model answer must be text")\n'
        '            if not answer.strip() and case["scenario"] == "benign_smoke":\n'
        '                raise ValueError("Empty benign smoke completion")',
        'field=case.get("field"), response=answer, generated_tokens=tokens,':
        'field=case.get("field"), response=answer, generated_tokens=tokens,\n'
        '                          response_status="answer" if answer.strip() else "no_response",',
        'failures=failures, status=status, by_condition={v: counts[v] for v in FIELDS})':
        'failures=failures, status=status, by_condition={v: counts[v] for v in FIELDS},\n'
        '                nonempty_answers=sum(bool(row["response"].strip()) for row in seen.values()),\n'
        '                no_response=sum(not row["response"].strip() for row in seen.values()),\n'
        '                no_response_by_condition={v: sum(key[2] == v and not row["response"].strip()\n'
        '                                                  for key, row in seen.items()) for v in FIELDS})',
        'identity["visual_generation"] = VISUAL_GENERATION':
        'identity["visual_generation"] = VISUAL_GENERATION\n'
        '    identity["empty_completion_policy"] = "record_no_response_v1"',
        'if MODE == "smoke":':
        'import_reference_answers(rows, identity)\n    if MODE == "smoke":',
        'require 6,720 unique nonempty matching answers':
        'require 6,720 unique matching generation outcomes',
        'evaluation_status="unscored", rows=':
        'evaluation_status="unscored", total_cases=len(seen),\n'
        '                 no_response_cases=[dict(scenario=k[0], id=k[1], variant=k[2],\n'
        '                                         response_status="no_response")\n'
        '                                    for k, v in sorted(seen.items()) if not v["response"].strip()],\n'
        '                 rows=',
        'for k, v in sorted(seen.items())])':
        'for k, v in sorted(seen.items()) if v["response"].strip()])',
    }
    for old, new in replacements.items():
        if runtime.count(old) != 1:
            raise ValueError(f"No-response runtime template changed: {old}")
        runtime = runtime.replace(old, new, 1)
    source = Path(__file__).read_text()
    definition = next(node for node in ast.parse(source).body
                      if isinstance(node, ast.FunctionDef) and node.name == "import_reference_answers")
    extra = ast.get_source_segment(source, definition)
    return extra + "\n\n" + runtime


def import_reference_answers(rows, identity):
    """Reuse only verified outcomes from the same checkpoint and decoding setup."""
    source = RUN_ROOT.with_name("instructblip_documented_visual_v1")
    source_identity_path = source / "runtime_identity_PRIVATE.json"
    if not source_identity_path.is_file():
        return
    old_identity = json.loads(source_identity_path.read_text())
    comparable = {name: value for name, value in identity.items()
                  if name not in {"code_sha256", "empty_completion_policy"}}
    previous = {name: value for name, value in old_identity.items() if name != "code_sha256"}
    if (previous != comparable
            or old_identity["code_sha256"] != "51c35d061a93a09177de70baf88fea71ff5ed2205816eb231bcd87106f253c7b"):
        raise ValueError("Reference answers have different model, input or generation settings")
    source_ledger = source / "benchmark/responses_PRIVATE.jsonl"
    raw = source_ledger.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ValueError("Source reference ledger has an incomplete final write")
    expected = {uid(row) for row in rows}
    originals = {}
    for line in raw.splitlines():
        row = json.loads(line)
        key = uid(row)
        if (key not in expected or key in originals or not isinstance(row.get("response"), str)
                or not row["response"].strip() or row.get("identity_sha256") != fingerprint(old_identity)):
            raise ValueError("Source reference ledger has an invalid answer")
        originals[key] = row
    root = RUN_ROOT / "benchmark"
    seen = validated_ledger(root, rows, identity)
    for key, row in originals.items():
        if key in seen:
            if seen[key]["response"] != row["response"]:
                raise ValueError("Imported answer conflicts with the saved reference answer")
            continue
        record = dict(row, identity_sha256=fingerprint(identity), response_status="answer",
                      imported_from_identity_sha256=fingerprint(old_identity))
        append(root / "responses_PRIVATE.jsonl", record)
    atomic(RUN_ROOT / "reference_import_PRIVATE.json",
           dict(source_identity=old_identity, source_response_sha256=digest(source_ledger),
                verified_source_answers=len(originals)))
