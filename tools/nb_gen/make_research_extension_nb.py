"""Generate v7 compatibility plus saved-results analysis; optional CPU execution."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from vlm_saved_analysis import analyze_saved, measurement_sensitivity  # noqa: E402
from make_nb7 import build  # noqa: E402


def extension_cells():
    source_hash = hashlib.sha256((ROOT/'v6_full/results_v6.json').read_bytes()).hexdigest()
    result = analyze_saved(ROOT/'v6_full/results_v6.json')
    cells = []

    def add(kind, text):
        cell = dict(cell_type=kind, metadata={}, source=text.splitlines(True))
        if kind == 'code':
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)

    add('markdown', '# Expanded analysis of saved scientific results\n\n'
        '**Historical v6 data; exploratory, guard-labelled.** This section makes no model calls. '
        'It reconstructs paired refusal transitions and checks scoring sensitivity from numeric '
        'aggregates. It does not read private responses or reserved data. New target generations '
        'elsewhere in this notebook remain benign compatibility tests.\n\n'
        '**Question:** do small average text–image differences hide opposing changes in individual '
        'answers, and how much does scoring affect the interpretation?')
    add('code', (ROOT/'tools/vlm_saved_analysis.py').read_text())
    add('code', "from IPython.display import Markdown, display\n"
        "from datetime import datetime, timezone\n"
        "IS_COLAB_ANALYSIS = Path('/content/drive/MyDrive').is_dir()\n"
        "SOURCE_ANALYSIS = (Path('/content/drive/MyDrive/vlm_tradeoff_out_v6/results_v6.json') "
        f"if IS_COLAB_ANALYSIS else Path({str(ROOT/'v6_full/results_v6.json')!r}))\n"
        f"EXPECTED_V6_SHA = {source_hash!r}\n"
        "if hashlib.sha256(SOURCE_ANALYSIS.read_bytes()).hexdigest() != EXPECTED_V6_SHA:\n"
        "    raise ValueError('Saved scientific source differs from reviewed frozen v6 aggregates')\n"
        "saved_analysis = analyze_saved(SOURCE_ANALYSIS)\n"
        "print('Exploratory paired comparisons:', len(saved_analysis['transitions']))\n"
        "print('Scoring cells:', len(saved_analysis['scoring_sensitivity']))\n"
        "print('Source SHA256:', saved_analysis['source_sha256'])\n")
    add('markdown', '### What the source check means\n\n'
        'The input must match the reviewed v6 file byte for byte. Pair counts are reconstructed '
        'from saved McNemar discordances and paired marginal rates, with consistency checks. '
        'This reuses historical data; it is not a fresh replication. No human validation is implied.')
    add('code', "display(Markdown(transition_readout(saved_analysis)))\n"
        "fig_analysis = make_figure(saved_analysis)\n"
        "display(fig_analysis)\n"
        "import matplotlib.pyplot as plt\nplt.close(fig_analysis)\n")
    qwen = next(r for r in result['transitions'] if r['model']=='Qwen2-VL-2B' and
                r['judge']=='qwen3guard' and (r['condition_a'],r['condition_b'])==('E','C'))
    add('markdown', '### Reviewed interpretation of the paired result\n\n'
        f"In the frozen Qwen2-VL-2B/Qwen3Guard E-versus-C comparison, {qwen['a_only_refuses']} "
        f"items refuse only in text and {qwen['b_only_refuses']} only in images, among "
        f"{qwen['paired_n']} jointly valid pairs. The average difference is "
        f"{qwen['net_gap_pp']:.1f} percentage points, while {qwen['changed_refusal_pct']:.1f}% "
        'of pairs change the refusal label. Opposing changes can cancel in the mean.\n\n'
        'This does not tell us whether the non-refusal supplied harmful information or whether '
        'the model comprehended the task. The frozen NC rule and guards can be wrong. '
        'Harm/NC transition tables need verified paired labels beyond these aggregate margins. '
        'Keep this historical descriptive analysis separate from prespecified confirmatory endpoints.\n\n'
        '**Editable review:** examine every checkpoint and benchmark, including opposite directions; '
        'do not generalize the illustrative Qwen comparison to the entire panel.')
    add('code', "display(Markdown(sensitivity_readout(saved_analysis)))\n"
        "ANALYSIS_PARENT = (Path('/content/drive/MyDrive/vlm_tradeoff_analysis') "
        f"if IS_COLAB_ANALYSIS else Path({str(ROOT/'audit_work/saved_analysis')!r}))\n"
        "ANALYSIS_OUT = ANALYSIS_PARENT / datetime.now(timezone.utc).strftime('v6_saved_%Y%m%dT%H%M%S_%fZ')\n"
        "ANALYSIS_OUT.mkdir(parents=True, exist_ok=False)\n"
        "ANALYSIS_JSON = ANALYSIS_OUT/'results_saved_analysis.json'\n"
        "ANALYSIS_JSON.write_text(json.dumps(saved_analysis, indent=2, allow_nan=False))\n"
        "if json.loads(ANALYSIS_JSON.read_text()) != saved_analysis:\n"
        "    raise ValueError('Aggregate snapshot verification failed')\n"
        "make_figure(saved_analysis).savefig(ANALYSIS_OUT/'paired_transitions.png', dpi=180, bbox_inches='tight')\n"
        "plt.close('all')\n"
        "print('Verified aggregate snapshot:', ANALYSIS_JSON)\n"
        "print('No private text, images, replies, IDs or new model calls were exported.')\n")
    add('markdown', '### Reviewed interpretation and limits of scoring\n\n'
        'The displayed values come from the saved v6 run, independently for each guard. '
        'Refusal and harmful assistance are separate outcomes; NC adjustment changes the construct. '
        'Cell-valid denominator counts were not fully exported, so this section does not invent '
        'missing-label bounds from rounded rates. Human-only and corrected estimates remain pending.\n\n'
        '**Next:** verify audit sampling and pair coverage, obtain blinded human annotations and '
        'retest, freeze a reviewed estimator and uncertainty method, then compare conclusions. '
        'Save this notebook with outputs and its distinct aggregate snapshot before another stage.')
    add('markdown', '# Deeper measurement analysis\n\n'
        '**Question:** which observed contrasts depend most on the refusal rule or guard? '
        'This section uses the same frozen numeric v6 source. It does not reconstruct joint '
        'harm outcomes, fit a prediction policy or test new hypotheses. All computed cells '
        'are exported; the first two displayed tables select the largest absolute differences '
        'for readability, not for significance.')
    add('code', "measurement_analysis = measurement_sensitivity(saved_analysis)\n"
        "display(Markdown(measurement_readout(measurement_analysis)))\n"
        "print('Rule shifts:', len(measurement_analysis['scoring_rule_shifts']))\n"
        "print('Guard differences:', len(measurement_analysis['guard_differences']))\n"
        "print('Cell-mean contrasts:', len(measurement_analysis['cell_mean_contrasts']))\n")
    deeper = measurement_sensitivity(result)
    largest = max(deeper['scoring_rule_shifts'], key=lambda r:abs(r['raw_minus_nc_pp']))
    add('markdown', '### Reviewed interpretation of the deeper result\n\n'
        f"The largest raw-minus-NC refusal shift is {largest['raw_minus_nc_pp']:.2f} percentage "
        f"points for {largest['model']}, {largest['judge']}, condition {largest['condition']}. "
        'The saved raw and adjusted values use different refusal definitions; this does not '
        'show that the adjustment is correct. Guard differences identify where human review '
        'could change the conclusion, but do not select a winning judge.\n\n'
        'E/C harmfulness differences describe averages only. We still cannot count requests '
        'that are harmful only in images without verifying the exact private paired label '
        'and stimulus provenance. No missing label is treated as safe, and no nominal sign '
        'is described as statistically significant.\n\n'
        '**Editable review:** record which conclusions survive human review and which do not. '
        'Keep any future text-led allocation policy frozen before fresh evaluation.')
    add('code', "MEASUREMENT_JSON = ANALYSIS_OUT/'measurement_sensitivity.json'\n"
        "MEASUREMENT_JSON.write_text(json.dumps(measurement_analysis, indent=2, allow_nan=False))\n"
        "if json.loads(MEASUREMENT_JSON.read_text()) != measurement_analysis:\n"
        "    raise ValueError('Measurement snapshot verification failed')\n"
        "print('Verified separate measurement aggregate:', MEASUREMENT_JSON)\n"
        "print('No new inference, human labels or confirmatory outcomes were used.')\n")
    add('markdown', '### What was saved and what remains\n\n'
        'The completed notebook contains code, numeric outputs, figures and editable explanations. '
        'The historical paired/scoring aggregate and this deeper measurement aggregate are separate '
        'JSON files under the dated analysis folder. Save the executed notebook there as well. '
        'The next substantive dependency is a verified paired-label source and blinded human '
        'reference, followed by an approved fresh-data design and measured compute budget.')
    add('markdown', '# Scientific collection: staged plan and gates\n\n'
        'The owner requested expanded analysis, compatibility and new scientific collection. '
        'Only benign compatibility generation is active here. Amendment 5 still governs the core; '
        'new analysis specifications need a dated approved addendum before confirmatory use.\n\n'
        '1. Complete the remaining approved model checks and measure representative throughput.\n'
        '2. Freeze fresh exclusions, achieved panel, condition/call counts, output lengths and budget.\n'
        '3. Obtain the human reference and retest before opening reserved confirmatory data.\n'
        '4. Execute the approved scientific core, preserving failures and saving between stages.\n'
        '5. Review actual aggregates and write the supported, refuted and inconclusive findings.\n\n'
        'No untested checkpoint is described as compatible. A successful smoke is not a safety finding. '
        'The extended plan is in `docs/METHODOLOGY_REVIEW_AND_UPGRADE_PLAN.md`, section 8.')
    return cells


def generate(output, *, analysis_only=False, model='OpenGVLab/InternVL3-2B-hf'):
    output = Path(output)
    if analysis_only:
        nb = dict(cells=[], metadata=dict(kernelspec=dict(display_name='Python 3',
                  language='python', name='python3')), nbformat=4, nbformat_minor=5)
    else:
        build(output, [model], 60)
        nb = json.loads(output.read_text())
    nb['cells'].extend(extension_cells())
    output.write_text(json.dumps(nb, ensure_ascii=False)+'\n')
    return nb


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'notebooks/vlm_research_expanded.ipynb')
    parser.add_argument('--analysis-only', action='store_true')
    parser.add_argument('--execute', action='store_true', help='CPU saved analysis only; never execute GPU cells locally')
    args = parser.parse_args()
    if args.execute and not args.analysis_only:
        parser.error('Local execution is limited to --analysis-only')
    generated = generate(args.output, analysis_only=args.analysis_only)
    if args.execute:
        import nbformat
        from nbclient import NotebookClient
        notebook = nbformat.reads(json.dumps(generated), as_version=4)
        NotebookClient(notebook, timeout=120, kernel_name='python3').execute(cwd=str(ROOT))
        args.output.write_text(json.dumps(notebook, ensure_ascii=False)+'\n')
    print('Generated:', args.output, '| cells:', len(generated['cells']))
