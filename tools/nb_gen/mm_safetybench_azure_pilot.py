"""Prepare MM-SafetyBench answer exports or explicitly run the fixed Azure pilot."""

import argparse
from collections import Counter
from decimal import Decimal
from hashlib import sha256
from http.client import HTTPSConnection, HTTPException
import json
import os
from pathlib import Path
import re
import runpy
from urllib.parse import urlsplit
from zipfile import ZipFile


REPO = Path(__file__).resolve().parents[2]
AUTHOR_SHA = "801a891382a06b7c3b29083dd3844b6da6a3e0ef31d3dfdd9086e30b323f322b"
CARRIERS = ("SD", "TYPO", "SD_TYPO")


def prepare(root, packet):
    def digest(path):
        with path.open("rb") as stream:
            return __import__("hashlib").file_digest(stream, "sha256").hexdigest()

    def key(row):
        return row["scenario"], row["id"], row["variant"]

    def manifest_hash(rows):
        return sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

    helpers = runpy.run_path(str(Path(__file__).with_name("mm_safetybench_judge_handoff.py")),
        init_globals=dict(json=json, Counter=Counter, sha256=sha256, ZipFile=ZipFile,
                          digest=digest, key=key, manifest_hash=manifest_hash,
                          AUTHOR_ZIP=root / "MM-SafetyBench-main.zip", AUTHOR_SHA=AUTHOR_SHA))
    manifest = json.loads((root / "manifest_PRIVATE.json").read_text())
    expected = {key(row): row for row in manifest}
    if len(expected) != len(manifest) or Counter(k[2] for k in expected) != dict.fromkeys(CARRIERS, 1680):
        raise ValueError("Expected 5,040 unique image cases")
    if manifest_hash(manifest) != (root / "manifest_sha256.txt").read_text().strip():
        raise ValueError("Manifest checksum mismatch")
    answers, provenance = helpers["checked_answers"](root, expected, archived=True)
    rubrics = helpers["released_rubrics"]()
    scenarios = sorted({k[0] for k in answers})
    if len(scenarios) != 13:
        raise ValueError("Expected 13 scenarios")
    rows = []
    for scenario in scenarios:
        item = min((k[1] for k in answers if k[0] == scenario), key=int)
        name = helpers["RELEASE_RUBRIC"].get(scenario[:2], "gpt_query_template_safety")
        for variant in CARRIERS:
            identity = (scenario, item, variant)
            rows.append(dict(case=identity, rubric=name,
                             prompt=rubrics[name].format(prediction=answers[identity])))
    packet.parent.mkdir(parents=True, exist_ok=True)
    with packet.open("x", encoding="utf-8") as stream:
        json.dump(dict(author_sha256=AUTHOR_SHA, source=provenance, rows=rows), stream,
                  ensure_ascii=False, indent=2)
    print(f"Verified {len(answers)} archived answers. Prepared {len(rows)} private pilot requests.")
    print(f"Packet SHA-256: {digest(packet)}")


def classify(http_status, body, labels=("safe", "unsafe")):
    if http_status != 200:
        error = body.get("error")
        error = error if isinstance(error, dict) else {}
        inner = error.get("innererror")
        inner = inner if isinstance(inner, dict) else {}
        codes = {error.get("code"), inner.get("code")}
        if http_status == 400 and codes & {"content_filter", "ResponsibleAIPolicyViolation"}:
            return "filtered", None, False
        return "api_error", None, True
    choices = body.get("choices") or []
    if not isinstance(choices, list) or len(choices) != 1:
        return "unparseable", None, False
    choice, = choices
    if not isinstance(choice, dict):
        return "unparseable", None, False
    if choice.get("finish_reason") == "content_filter":
        return "filtered", None, False
    message = choice.get("message") or {}
    if not isinstance(message, dict):
        return "unparseable", None, False
    content = message.get("content")
    label = content.strip().lower() if isinstance(content, str) else None
    if choice.get("finish_reason") != "stop" or message.get("refusal") or label not in labels:
        return "unparseable", None, False
    return "judged", label, False


class AzureJudgeError(RuntimeError):
    """A judge request did not yield a resolved release-compatible label."""


def azure_config():
    endpoint = urlsplit(os.environ["AZURE_OPENAI_ENDPOINT"])
    if (endpoint.scheme != "https" or not re.fullmatch(r"[a-z0-9-]+\.openai\.azure\.com", endpoint.netloc)
            or endpoint.path not in {"", "/"} or endpoint.query or endpoint.fragment):
        raise ValueError("Supply the HTTPS Azure OpenAI resource endpoint")
    config = dict(host=endpoint.netloc, deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
                  model_version=os.environ["AZURE_OPENAI_MODEL_VERSION"],
                  api_key=os.environ["AZURE_OPENAI_API_KEY"])
    if not all(config.values()):
        raise ValueError("Deployment, model version and authentication are required")
    return config


def post_judgment(connection, config, prompt, labels=("safe", "unsafe")):
    """One request, no retry. The returned body belongs only in private records."""
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("A nonempty released-rubric prompt is required")
    request = dict(model=config["deployment"], messages=[dict(role="user", content=prompt)],
                   temperature=0, max_completion_tokens=8)
    connection.request("POST", "/openai/v1/chat/completions", json.dumps(request),
                       {"api-key": config["api_key"], "Content-Type": "application/json"})
    response = connection.getresponse()
    body = json.loads(response.read())
    if not isinstance(body, dict):
        raise ValueError("Azure returned a non-object response")
    status, label, stop = classify(response.status, body, labels)
    return dict(status=status, label=label, http_status=response.status,
                reported_model=body.get("model"), usage=body.get("usage"),
                response_body_PRIVATE=body), stop


def get_res(prompt="", *, connection_factory=None):
    """Released evaluation.py hook: return safe/unsafe or raise, never guess.

    Calling this function sends one request and may consume Azure credit.
    Importing, exporting and preparing packets do not call it.
    """
    config = azure_config()
    factory = HTTPSConnection if connection_factory is None else connection_factory
    connection = factory(config["host"], timeout=30)
    try:
        record, _ = post_judgment(connection, config, prompt)
        if record["status"] != "judged":
            raise AzureJudgeError(f"Unresolved judge outcome: {record['status']}; HTTP {record['http_status']}")
        return record["label"]
    finally:
        connection.close()


def pilot_cost_reserve(rows, max_usd):
    """Conservative byte-based reservation at the verified GPT-4.1 Global prices.

    UTF-8 byte counts exceed ordinary text BPE token counts. Add 128 tokens per
    single-user-message request for framing; reserve all eight output tokens.
    This is a cost guard for this fixed pilot, not an Azure billing balance.
    """
    cap = Decimal(str(max_usd))
    if not cap.is_finite() or not 0 < cap <= Decimal("0.50"):
        raise ValueError("Approve a pilot cap greater than zero and at most USD 0.50")
    inputs = sum(len(row["prompt"].encode("utf-8")) + 128 for row in rows)
    reserve = (Decimal(inputs) * 2 + Decimal(len(rows) * 8) * 8) / 1_000_000
    if reserve > cap:
        raise ValueError("Conservative pilot cost exceeds the approved cap; no requests sent")
    return dict(max_usd=str(cap), reserved_usd=str(reserve), input_token_reserve=inputs,
                input_usd_per_million="2", output_usd_per_million="8",
                price_scope="gpt-4.1 2025-04-14 Global Standard; verified 2026-11-08")


def run(packet, output, approved_sha, max_usd):
    raw = packet.read_bytes()
    if sha256(raw).hexdigest() != approved_sha:
        raise ValueError("Packet differs from the approved SHA-256")
    rows = json.loads(raw)["rows"]
    if len(rows) != 39 or len({tuple(row["case"]) for row in rows}) != 39:
        raise ValueError("Only the fixed 39-case pilot may be sent")
    config = azure_config()
    if config["model_version"] != "2025-04-14":
        raise ValueError("Recheck pricing before using a different judge version")
    budget = pilot_cost_reserve(rows, max_usd)
    counts = Counter()
    connection = HTTPSConnection(config["host"], timeout=30)
    try:
        with output.open("x", encoding="utf-8") as stream:
            def save(record):
                stream.write(json.dumps(record) + "\n")
                stream.flush()
                os.fsync(stream.fileno())

            save(dict(packet_sha256=approved_sha, deployment=config["deployment"], model_version=config["model_version"],
                      max_requests=39, metric="safety", temperature=0, max_completion_tokens=8,
                      budget=budget))
            for row in rows:
                try:
                    record, stop = post_judgment(connection, config, row["prompt"])
                    status = record["status"]
                    save(dict(case=row["case"], **record))
                except (OSError, ValueError, HTTPException) as exc:
                    save(dict(case=row["case"], status="request_failed", error_type=type(exc).__name__))
                    counts["request_failed"] += 1
                    break
                counts[status] += 1
                if stop:
                    break
    finally:
        connection.close()
    print(dict(planned=39, attempted=sum(counts.values()), **counts))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("archive", type=Path)
    prep.add_argument("packet", type=Path)
    export = commands.add_parser("export", help="Offline author-schema export; no API calls")
    export.add_argument("queue", type=Path)
    export.add_argument("author_zip", type=Path)
    export.add_argument("destination", type=Path)
    export.add_argument("--model-key", required=True)
    pilot = commands.add_parser("run")
    pilot.add_argument("packet", type=Path)
    pilot.add_argument("output", type=Path)
    pilot.add_argument("--approved-sha", required=True)
    pilot.add_argument("--max-usd", required=True, help="Owner-approved pilot cap, at most 0.50 USD")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.archive, args.packet)
    elif args.action == "export":
        from mm_safetybench_judge_handoff import export_author_layout
        result = export_author_layout(args.queue, args.author_zip, args.destination, args.model_key)
        print({k: result[k] for k in ("total_cases", "nonempty_answers", "no_response")})
    else:
        run(args.packet, args.output, args.approved_sha, args.max_usd)
