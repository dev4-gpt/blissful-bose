"""Compose historical aggregates, teaching mathematics and the private GPU lab.

Regenerate from source; never copy raw outputs from historical experiment notebooks.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

import nbformat
import make_unified_nb as history
import make_visual_attacks_nb as teaching
import make_visual_suite_nb as laboratory

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'notebooks/vlm_research_unified.ipynb'

INTRO = """# Unified VLM research: evidence, mathematics and visual attacks
**25 October 2026 — standalone research workbook.**

This brings together completed historical evidence, executable CPU lessons, the
paper-derived visual attack laboratory, and prospective contribution designs.
Historical tables are saved exploratory outcomes. CPU tests are software checks.
One separate synthetic PGD feasibility case has completed on pretrained Qwen2.5-VL-3B/T4;
its saved aggregate record is `visual_t4_profile_20261025/profile_aggregate_status.json`.
The two-model synthetic development panel has also completed; it is integration evidence.
External integrity and broader safety benchmarks remain separate, with human validation pending.
Novelty remains an open question; this workbook cannot manufacture novel results.

## Reading and execution route

1. **Part A — completed work:** v1–v7 timeline, tables, failures, measurement limits and provenance.
2. **Part B — mathematics:** VLM pipeline, FGSM, PGD, patch and trust boundaries; harmless CPU demonstrations.
3. **Part C — real visual attack lab:** paper coverage, objectives, frozen Qwen adapter,
   private data contract, acceptance checks and optional bounded T4 run.
4. **Part D — contribution decision:** falsifiable designs, comparison rules and milestones.

Default **Run all** displays aggregates and executes CPU checks. The only GPU switch
is `RUN_GPU` in Part C. Nothing in Parts A/B launches the older experiments.
Use the table of contents to jump directly to Part C when preparing a GPU run.
The full paper dossier appears once, at the end of Part C.

### T4 execution card

Select **Runtime → Change runtime type → T4 GPU** in Colab. A selectable T4 is not
proof that a runtime is allocated or that this model's optimization fits its memory.
Start with one method and a reviewed private development manifest, not the whole panel.
The prepared first scope is Qwen2.5-VL-3B, pinned revision, FP16, batch one,
224-square images, at most four development cases, ten PGD steps (one for FGSM),
and at most thirty wall minutes including install/download/load. No training occurs.

Before enabling Part C, accept draft Amendment 8 and its exact manifest/config/source
hash, choose a new PRIVATE college-Drive output folder, then set the explicit compute,
Drive and installation controls. These are owner decisions under the project brief.
Save the completed notebook with outputs and a separate aggregate status snapshot
before changing configurations. No faithful paper reproduction or T4 fit is promised.
"""

CONTRIBUTIONS = r"""## Part D — from reproduction to a defensible contribution

### What this workbook establishes today

The historical chapters document the prior exploratory work and failed predictions.
The CPU chapters demonstrate constrained optimization and runner control flow.
They do not supply measured visual jailbreak rates, defense improvements or a new
scientific contribution. Paper coverage in Part C distinguishes implemented adaptations
from original configurations still awaiting reproduction.

### Candidate decision register — prospective, editable

| Candidate | Falsifiable prediction | Necessary controls | Primary proposed comparison | Stop/claim rule |
|---|---|---|---|---|
| Delivered-image preprocessing and transfer | Saving/resizing changes attack outcomes at the same declared delivered budget | Same requests/images, exact reloaded pixels, clean and random controls, fixed decoding | Paired outcome change across prespecified deployment paths, clustered by request | Reject a novelty claim if close prior art already covers the design; no claim from loss alone |
| Defense generalization across mechanisms | A defense's benefit differs between pixel, patch and injection cases at matched benign utility and cost | Clean/defended clean, matched task populations, query accounting, defense-aware optimization | Prespecified attack-by-defense contrast with utility and latency reported alongside it | No robustness claim without adaptive coverage; report incomplete adaptation |
| Reproduction discrepancy | A verified implementation detail materially changes an original conclusion | Original supported checkpoint/config, changed-one-factor comparison, artifact checks | Original endpoint with the same denominator and scoring protocol | Label changed-model work adaptation; publish negative replication evidence honestly |

These are candidate designs, not verified novelty. Search the closest primary papers
and their subsequent citations before selecting one. The dossier records reading depth;
an abstract or survey citation cannot establish an original experimental result.

### Outcomes and mathematics for the eventual analysis

For request $i$, attack $a$ and defense $d$, retain outcomes separately:
$U_{iad}$ (unsafe assistance), $J_{iad}$ (unauthorized instruction deviation),
$C_{iad}$ (task correctness), refusal, comprehension, cap hits and execution failure.
None can be inferred solely from target loss or from another outcome.

The paired safety estimand for one prespecified condition is
$\Delta_{ad}=N^{-1}\sum_i(U_{iad}-U_{i,clean,d})$ when fully observed.
For $H$ resolved unsafe cases and $M$ unresolved among $N$ attempted cases,
report $H/N$, unresolved $M/N$, and identification bounds
$[H/N,(H+M)/N]$. Report paired missingness too; do not silently use a different
complete-case population for each method.

Resample underlying requests as clusters for paired intervals, keeping related images,
paraphrases and variants together. Shared universal artifacts induce additional dependence:
one optimized image is not $N$ independent attack replications. With one artifact, inference
is conditional on that artifact. Prespecify the primary contrast family and Holm adjustment.
Freeze sample sizes after measured cost and a justified effect threshold, before outcomes.

Two independent reviewers should label a probability sample blinded to model/condition,
with the image and legitimate task visible where needed. Keep disagreement-selected
diagnostic rows separate or use known selection weights. Report agreement before
adjudication and unresolved judgements; automatic labels are not human validation.
This statistical/human-review analysis is a design here, not an implemented scorer.

### Concrete sequence and deliverables

| Gate | Deliverable | Evidence required to advance |
|---|---|---|
| By Oct 28 | Advisor dossier, this notebook, reviewed paper/data access inventory | Source-traceable claims; original results versus ours separated; unresolved access listed |
| First T4 stage | One bounded development method, private paired outputs and cost status | Image gradients, native inference parity, budget after reload, frozen weights, timing/VRAM |
| By Nov 4 | Selected faithful/reduced-scale baseline and proposed contribution | Prior-art exclusion, feasible held-out protocol, accepted amendment and fixed splits |
| Nov 5–18 | Core panel, transfer/defense/adaptive checks and human validation | Fixed rubric, controls, failures and utility; no sample shrinking after outcomes |
| Nov 19–Dec 1 | Traceable analysis and manuscript revision | Tested results, documented deviations, limited claims; venue chosen by owner |

### Advisor decision record — editable

- Closest verified prior study and exact section/table:
- What has actually been reproduced, on which checkpoint:
- Remaining implementation or data obstacles:
- Chosen prediction, primary endpoint and minimum meaningful effect:
- Fresh split identity, overlap exclusions and human-review allocation:
- Measured seconds/peak VRAM per case and projected approved budget:
- Owner acceptance/date and final novelty decision:

Regenerate with `python3 tools/nb_gen/make_research_unified_nb.py --execute`.
This rebuilds from current source/aggregate files; it does not refresh model evidence.
Keep dated executed Colab archives separately. All benchmark text, images, raw model
outputs and reviewer annotations remain outside public Git.
"""


def build(output=OUTPUT, execute=False):
    cells = [nbformat.v4.new_markdown_cell(INTRO)]
    # Rebuild the sanitized historical view; do not embed arbitrary old outputs.
    with tempfile.TemporaryDirectory(prefix='vlm_unified_') as temporary:
        work = Path(temporary)
        historical = history.build(work/'history.ipynb')
        teaching.build(False, work/'teaching.ipynb')
        laboratory.build(work/'lab.ipynb', False)
        chapters = [('A', 'Completed historical evidence', historical),
                    ('B', 'Worked mathematics and harmless demonstrations',
                     nbformat.read(work/'teaching.ipynb', as_version=4)),
                    ('C', 'Real visual attack laboratory and T4 stage',
                     nbformat.read(work/'lab.ipynb', as_version=4))]
        for part, title, notebook in chapters:
            cells.append(nbformat.v4.new_markdown_cell(f'## Part {part} — {title}'))
            for original in notebook['cells']:
                cell = nbformat.from_dict(original)
                source = cell['source']
                if isinstance(source, list):
                    source = ''.join(source)
                # The lab supplies the current complete dossier once.
                if part == 'B' and source.startswith('## 6. Portable dossier'):
                    break
                if part in ('B', 'C') and cell['cell_type'] == 'markdown':
                    lines = source.splitlines()
                    nonempty = [line for line in lines[1:] if line.strip()]
                    if nonempty and sum(line.startswith('    ') for line in nonempty) > len(nonempty)/2:
                        source = '\n'.join(line[4:] if line.startswith('    ') else line
                                           for line in lines)+'\n'
                cell['source'] = source
                if cell['cell_type'] == 'code':
                    ast.parse(source)
                    cell['execution_count'] = None
                    cell['outputs'] = []
                cells.append(cell)
    cells.append(nbformat.v4.new_markdown_cell(CONTRIBUTIONS))
    cells.append(nbformat.v4.new_markdown_cell('''## Part E — two-model development and external diagnostic workflows

These appendices embed the additional Smol/Idefics3 adapter, common 448-canvas panel,
directional transfer, private review packet and the frozen external integrity protocol.
All launch/export switches default off. Historical/CPU display execution never launches
these processes. Native-system instructions and benchmark scope are preserved.
Use a reviewed new run identity; completed or changed identities are never overwritten.
External inference follows preservation of the completed synthetic run. See Amendments 9/10.
The notebook does not provide independent human labels or a novel contribution automatically.'''))
    cells.append(nbformat.v4.new_code_cell('RUN_PANEL_GPU = False\nRUN_EXTERNAL_GPU = False\nEXPORT_PANEL_AFTER_FINISH = False\n'))
    with tempfile.TemporaryDirectory(prefix='vlm_panel_appendices_') as temporary:
        for external in (False, True):
            path=Path(temporary)/('external.ipynb' if external else 'panel.ipynb')
            command=[sys.executable,str(ROOT/'tools/nb_gen/make_visual_panel_nb.py'),'--output',str(path)]
            if external:command.append('--external')
            subprocess.run(command,check=True,capture_output=True)
            appendix=nbformat.read(path,as_version=4)
            code_index=0
            for cell in appendix.cells:
                if cell.cell_type=='code':
                    code_index+=1
                    if code_index>1:
                        switch='RUN_EXTERNAL_GPU' if external else 'RUN_PANEL_GPU'
                        if not external and code_index==4:switch+=' and EXPORT_PANEL_AFTER_FINISH'
                        cell.source='if '+switch+':\n'+textwrap.indent(cell.source,'    ')+'\nelse:\n    print("Optional stage disabled; no new model calls.")\n'
                        ast.parse(cell.source)
                cells.append(cell)
    for index, cell in enumerate(cells):
        cell['id'] = f'unified-{index:03d}'
    source_paths = ['tools/nb_gen/make_research_unified_nb.py',
                    'tools/nb_gen/make_unified_nb.py',
                    'tools/nb_gen/make_visual_attacks_nb.py',
                    'tools/nb_gen/make_visual_suite_nb.py',
                    'tools/nb_gen/make_visual_panel_nb.py',
                    'tools/vlm_visual_panel.py','tools/vlm_visual_smol_adapter.py']
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths}
    notebook = nbformat.v4.new_notebook(cells=cells, metadata=dict(
        kernelspec=dict(display_name='Python 3', language='python', name='python3'),
        language_info=dict(name='python'), colab=dict(provenance=[]),
        unified=dict(date='2026-10-25', source_hashes=hashes, default_gpu=False)))
    nbformat.validate(notebook)
    if execute:
        notebook = nbformat.from_dict(history.execute_cpu(notebook))
    nbformat.validate(notebook)
    Path(output).write_text(json.dumps(notebook, ensure_ascii=False, allow_nan=False)+'\n')
    print(f'Unified workbook: {output}; {len(cells)} cells; CPU executed={execute}; GPU OFF')
    return notebook


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    build(args.output, args.execute)
