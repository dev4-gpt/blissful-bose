"""Generate notebooks/eva_harmbench_judge_pilot.ipynb.

Project convention (AGENTS.md section 6): edit this generator, not the notebook JSON.
Regenerate with::

    python3 tools/nb_gen/make_eva_judge_pilot_nb.py

The notebook runs the judge-comparison pilot specified in
docs/EVA_REPRODUCTION_CONTRACT.md sections P2.6-P2.10: rescore saved, unedited LLaVA-1.5-7B
MM-SafetyBench answers with the HarmBench classifier and report paired agreement against the
existing Azure GPT-4.1 labels on the same cases.

It does NOT edit any model, download LLaVA, or produce an edited checkpoint. It needs only the
classifier and answers already on the college Drive.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "notebooks" / "eva_harmbench_judge_pilot.ipynb"

ANSWERS_REL = (
    "MM_SafetyBench_Full_20261102_PRIVATE/Runs/Judge_Handoff_PRIVATE/"
    "Azure_Preparation_20261108T153750Z_PRIVATE/Full_Metrics_20261108_PRIVATE/"
    "llava/safety/author_results_PRIVATE"
)
ARCHIVE_CHECKPOINT = "liuhaotian/llava-v1.5-7b"
GATE_SCRIPT = "tools/mm_safetybench_harmbench_gate.py"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text.strip("\n").splitlines(True)}


CELLS: list[dict] = [
    md(f"""
# EVA judge-comparison pilot — HarmBench classifier vs Azure GPT-4.1

Contract: `docs/EVA_REPRODUCTION_CONTRACT.md` sections P2.6-P2.10.

**What this does.** Rescores a frozen sample of our **already-saved, unedited** LLaVA-1.5-7B
MM-SafetyBench answers with EVA's native endpoint (`cais/HarmBench-Llama-2-13b-cls`) and reports
**paired agreement and disagreement against our existing Azure GPT-4.1 labels on the same cases**.

**What this is not.** No weight edit. No LLaVA download. No new generation. No edited checkpoint.

**Why.** EVA's Table III reports LLaVA-1.5-7B SD+TYPO ASR = 37.0 using the HarmBench classifier.
MM-SafetyBench's own Table 3 reports 72.14 for the same model and condition, and our Azure panel
measures 73.88 macro. The paired comparison measures how much of that spread is the instrument,
and it depends on none of EVA's unknowns.

**Framing.** Results describe *agreement between these two scoring setups on our archived answers*.
EVA's 37.0 is a **published reference point, not a target**: its exact classifier checkpoint,
prompt template and evaluation subset are unverified (EVA-27, EVA-23), and our archive used a
different LLaVA repository (E8 — manifest `model_key` is `{ARCHIVE_CHECKPOINT}`, while EVA pins
`llava-hf/llava-1.5-7b-hf`).

**Hypothesis under test, not a conclusion.** That the classifier's "benign generations do not count"
rule collapses the advice scenarios (10-Legal_Opinion, 11-Financial_Advice, 12-Health_Consultation)
which the MM-SafetyBench rubric saturates near 100%. The per-scenario disagreement profile is the
evidence.

**Runtime.** The classifier loads in NF4 4-bit, so a single T4 is enough. 624 frozen cases at
`--per-cell 12`.
"""),
    md("""
## 1. GPU check and dependencies
"""),
    code("""
import subprocess
print(subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total',
                      '--format=csv,noheader'], capture_output=True, text=True).stdout.strip()
      or 'NO GPU VISIBLE - set Runtime > Change runtime type > GPU')
"""),
    code("""
# bitsandbytes is required for the NF4 4-bit classifier load.
!pip -q install -U "transformers>=4.44" accelerate bitsandbytes
"""),
    md("""
## 2. Mount Drive and verify the export

The manifest is checked **before** the classifier loads, so a wrong path or a checkpoint mismatch
fails in seconds rather than after a ~26 GiB download.
"""),
    code(f"""
from google.colab import drive
drive.mount('/content/drive')

import json, pathlib
DRIVE = pathlib.Path('/content/drive/MyDrive')
ANSWERS = DRIVE / {ANSWERS_REL!r}

manifest_path = ANSWERS / 'judged_export_manifest_PRIVATE.json'
assert manifest_path.exists(), f'export manifest not found under {{ANSWERS}}'
manifest = json.loads(manifest_path.read_text())

print('model_key        :', manifest['model_key'])
print('total_cases      :', manifest['total_cases'])
print('nonempty_answers :', manifest['nonempty_answers'])
print('no_response      :', manifest['no_response'])
print('metric/population:', manifest['metric'], '/', manifest['population'])
print('counts_by_condition:', manifest['counts_by_condition'])

assert manifest['model_key'] == {ARCHIVE_CHECKPOINT!r}, manifest['model_key']
for cond in ('TEXT', 'SD', 'TYPO', 'SD_TYPO'):
    n = len(list((ANSWERS / cond / 'questions_with_answers').glob('*.json')))
    print(f'  {{cond:8s}} {{n}} scenario files')
    assert n == 13, f'{{cond}}: expected 13 scenario files, found {{n}}'
"""),
    md("""
## 3. Get the harness

`mm_safetybench_harmbench_gate.py` carries the verified judge identity, the pinned HarmBench
template with integrity checks, the corrected behaviour field and label parsing, and the paired
statistics. It is kept on Drive next to this notebook, so no upload is needed.
"""),
    code(f"""
import pathlib, shutil
GATE = pathlib.Path({GATE_SCRIPT!r})
GATE.parent.mkdir(parents=True, exist_ok=True)

# Preferred: copy from Drive, next to this notebook.
drive_copy = DRIVE / 'Colab Notebooks' / 'mm_safetybench_harmbench_gate.py'
if not GATE.exists() and drive_copy.exists():
    shutil.copy2(drive_copy, GATE)
    print('copied harness from Drive:', drive_copy)

# Fallback: upload it by hand.
if not GATE.exists():
    from google.colab import files
    uploaded = files.upload()                # choose mm_safetybench_harmbench_gate.py
    for name, data in uploaded.items():
        GATE.write_bytes(data)

assert GATE.exists(), 'harness not available'
print('harness present:', GATE.resolve())
"""),
    code(f"""
# CPU self-test first: 15 checks, no model load. Must pass before judging.
!python3 {GATE_SCRIPT} --self-test
"""),
    md("""
## 4. Run the pilot

Outputs go to a **dated private Drive folder** so they survive a runtime reset. The frozen
selection and its hash are written before the classifier loads; re-running with a different sample
against an existing freeze is refused.
"""),
    code(f"""
import datetime, subprocess
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
OUT = DRIVE / f'MM_SafetyBench_Full_20261102_PRIVATE/Runs/HarmBench_Judge_Pilot_{{stamp}}_PRIVATE'
OUT.mkdir(parents=True, exist_ok=True)
print('output folder:', OUT)

subprocess.run([
    'python3', {GATE_SCRIPT!r}, '--run',
    '--answers-root', str(ANSWERS),
    '--checkpoint', {ARCHIVE_CHECKPOINT!r},
    '--out-root', str(OUT),
    '--per-cell', '12',
], check=True)
"""),
    md("""
## 5. Read the result

Report the paired numbers, not a single rate. `paired_diff_azure_minus_hb` with its interval and
the exact McNemar p-value is the measurement; `hb_asr` is one side of it.
"""),
    code("""
import json, glob
summary = sorted(glob.glob(str(OUT / 'harmbench_gate_summary_*.json')))[-1]
s = json.loads(open(summary).read())
for key in ('submitted', 'hb_judged', 'hb_unresolved', 'hb_pooled_asr', 'hb_pooled_asr_wilson',
            'paired_cases', 'paired_agreement', 'discordant_hb_unsafe_azure_safe',
            'discordant_azure_unsafe_hb_safe', 'pooled_paired_difference_azure_minus_hb'):
    print(f'{key:42s} {s.get(key)}')
print()
print('reference points (NOT targets):', s['reference_points'])
print()
print('interpretation limits:')
for line in s['interpretation_limits']:
    print('  -', line)
"""),
    code("""
# Per-scenario profile for the advice-scenario hypothesis: do 10/11/12 collapse under HarmBench?
import glob, csv
agg = sorted(glob.glob(str(OUT / 'harmbench_gate_paired_*.csv')))[-1]
rows = [r for r in csv.DictReader(open(agg)) if r['condition'] == 'SD_TYPO']
print(f"{'scenario':26s}{'hb_asr':>8s}{'azure':>8s}{'agree':>8s}{'diff':>8s}{'mcnemar_p':>11s}")
for r in sorted(rows, key=lambda x: x['scenario']):
    print(f"{r['scenario']:26s}{r['hb_asr']:>8s}{r['azure_asr_on_paired']:>8s}"
          f"{r['agreement']:>8s}{r['paired_diff_azure_minus_hb']:>8s}{r['mcnemar_exact_p']:>11s}")
"""),
    md("""
## 6. Before quoting anything

- These are **two scoring setups on our archived answers**, not a reproduction of EVA's number.
- EVA's 37.0 stays a reference point. A result away from it has several live explanations: the
  checkpoint/stack difference (E8), EVA's unrecoverable template choice (EVA-27), and its unstated
  denominator and subset (EVA-23).
- The advice-scenario mechanism is a **hypothesis** this pilot tests.
- An edited-versus-unedited claim additionally requires resolving E8 — either establishing
  equivalence with `llava-hf/llava-1.5-7b-hf` or regenerating the unedited control on it.
- Raw answers and per-case labels stay private. Only aggregates may leave Drive.
"""),
]

NB = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "accelerator": "GPU",
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(NB, indent=1))
    n_code = sum(1 for c in CELLS if c["cell_type"] == "code")
    print(f"wrote {OUT}")
    print(f"  cells: {len(CELLS)} ({n_code} code, {len(CELLS) - n_code} markdown)")


if __name__ == "__main__":
    main()
