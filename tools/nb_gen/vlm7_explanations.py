"""Reader-facing notebook notes and an aggregate-only run readout; no scientific changes."""
OVERVIEW = '''## How to read this notebook

Each section follows **question → code and output → plain-English interpretation**.
The text cell after each result block is editable. Once the run finishes, we will
replace its review placeholder with an explanation tied to that run's saved output.
The final automatic readout uses numeric aggregates only; it does not judge replies.

**The research question:** if a model refuses a request less often when it appears in
an image, how much depends on the image, the surrounding instruction, or how we score it?

| Comparison | What it tells us | What it cannot establish alone |
| --- | --- | --- |
| B: original text; E: image text with matched instruction; C: benchmark image | Whether a text control explains part of the apparent B−C gap | B and E also differ in content form, so B−E is not a pure wording effect |
| Same full question, text/image, under three instructions | Whether the image effect changes with wording | A universal mechanism across all VLMs |
| Same text with blank/noise/natural images | Whether image presence changes behavior | That the model used the image meaningfully |
| Transcription, eight samples, image dose/order | Reading, sampling stability and preprocessing checks | That a separate readback proves comprehension during answering |

**Run modes:** smoke uses one synthetic benign item and tests compatibility;
development uses exploratory items; confirmatory uses reserved items only after
the human audit, historical exclusions and compute-budget gates pass.
Smoke is not a safety score. Refusal and harmfulness are separate outcomes.

**Our evidence plan:** preserve past evidence → validate models and human labels →
freeze fresh items/settings/budget → run paired comparisons → audit and estimate
uncertainty → write the paper. New model/benchmark/design choices require an approved addendum.

**Saving rule:** before changing settings or moving to another run, save a dated copy
of this notebook with its code and outputs, and a separate aggregate-results snapshot.
Verify saving finished. Do not clear the only completed-run outputs.
'''

AFTER = {
    'Runtime and exact revisions': '''### What this setup result means

The output identifies the run mode, GPU and budget. It records exact checkpoint
revisions and keeps outputs on Drive. A model on the selected list has not necessarily
loaded or completed inference. Download/loading can overrun the budget because it is
checked between calls. Environment setup is not an experimental finding.

**Review after completion:** record the actual GPU, selected panel, elapsed time,
precision and any CPU offload. Explain missing coverage without assuming success.
''',
    'Human gate': '''### What the human-gate result means

“Pending” means our label-validity requirements are not yet satisfied. Synthetic smoke
can continue; development results remain exploratory; reserved confirmatory generation
is blocked. Claude annotations are LLM annotations, not human labels. Passing the gate
validates the specified reference checks, not every future response or model family.

**Review after completion:** record the gate status, reference/retest coverage and named
guard. Do not describe unreviewed guard-labelled outcomes as human-validated.
''',
    'Data and frozen partition': '''### What the data result means

“Selected items: 1” in smoke mode is intentional: it is a harmless synthetic instruction.
In scientific modes, the manifest fixes original IDs, hashes, benchmark groups and
development/reserved membership before generation. Check per-scenario/category counts;
an overall total can hide missing groups. Project-held-out does not mean absent from
model pretraining. XSTest is a benign control, not another attack benchmark.

**Review after completion:** state which data were used, achieved counts, exclusions,
transcription verification and shortfalls. Do not print private prompts or item IDs.
''',
    'Checkpointed generation': '''### What the generation result means

“Loaded” only confirms loading. “Completed item” means the loop reached that item’s end;
some conditions can still have failed. Consult failures and condition coverage before
calling a model compatible. An error on an image-after-text dose check may mean the
template cannot preserve/verify that order; do not report the requested order as tested.
Cached responses resume exact work. A CUDA device-side assertion requires a fresh Python
context before resuming; completed checkpoints should be preserved first.

**Review after completion:** list successful text/image/readback checks and each failed
condition, resource use and truncation. Benign nonempty replies do not establish answer
quality or safety. The final readout summarizes coverage without exposing responses.
''',
    'Stimulus-aware labels': '''### What the labelling result means

Smoke deliberately skips safety guards. In science runs, guards judge the stimulus the
model saw. Refusal, NOT_COMPREHEND and harmful assistance are different concepts: a model
can be unhelpful without refusing, or include harmful content despite a warning.
Missing parses are unavailable, not safe. A fixed NC rule can also be wrong.

**Review after completion:** report each guard separately, missingness and audit coverage.
Human reviewers should see blinded stimuli/responses before guard answers. Do not pick
the guard that gives the most convenient result or tune the rule on its held-out test rows.
''',
    'Aggregate analysis and private audit': '''### How to interpret the saved analysis

Read the automatic run readout below, then add the reviewed interpretation in the final
text cell. A positive B−C means lower refusal in the image condition. E−C compares the
matched text and image conditions. Use the full-question grid to assess wording because
B−E also changes content form. Effects are percentage points, not relative percentages.

Read paired sample counts and uncertainty alongside estimates. A confidence interval
crossing zero is inconclusive, not proof of equivalence. Prediction needs held-out
architecture groups and baseline comparisons. Failed or incomplete panels must remain
visible. Refusal is not one minus harmfulness. Never turn smoke outputs into scientific claims.
''',
}

REVIEW = '''## Reviewed interpretation — complete after the run

**Status: awaiting review of this run's saved outputs.** This cell intentionally contains
no anticipated finding. After completion, an analyst can edit it without rerunning inference.

- **What ran:** date, mode, benchmarks, completed checkpoints, item counts and failures.
- **What we observed:** cite the exact table/figure, model, condition, guard, estimate,
  paired sample count and interval. Include negative results and missing outcomes.
- **In ordinary language:** “For [checkpoint], refusal changed from [B]% to [C]%; the
  matched text control was [E]%. This suggests [bounded interpretation] under these settings.”
- **What remains uncertain:** annotation errors, comprehension, incomplete coverage,
  quantization, few scenario/family groups, exploratory status and generalization limits.
- **Next step:** only the action justified by the evidence and the approved plan.
- **Saved evidence:** dated notebook with code/outputs, aggregate snapshot, private run
  manifest; verify saving before changing settings or starting the next run.

Use the actual outputs, not the hypotheses, to fill these fields. Do not paste private
prompts or model replies. Keep earlier runs as dated archives rather than rewriting their story.
'''


def run_readout7(result):
    """Deterministic explanation from an allowlist of aggregates; no reply inspection."""
    import math

    def fmt(value):
        return f'{100 * value:.1f}' if isinstance(value, (int, float)) and math.isfinite(value) else 'unavailable'

    def safe(value):
        return str(value).replace('|', r'\|').replace('\n', ' ')

    meta = result.get('meta', {})
    lines = ['## Automatic readout of this saved run', '',
             'Source: `results_v7.json` from the immediately preceding export cell.', '']
    if meta.get('mode') == 'smoke' or result.get('status') == 'benign_smoke_only':
        lines += ['**Benign compatibility test only — no safety finding.**', '',
                  f"Selected checkpoints: {result.get('attempted_models', 'unavailable')}; "
                  f"checkpoints with at least one response: {result.get('responding_models', 'unavailable')}; "
                  f"recorded failures: {len(result.get('failures', []))}.", '',
                  '| Model | B/E/C/readback checks with saved nonempty responses |', '| --- | --- |']
        for model, checks in result.get('model_checks', {}).items():
            present = [c for c in ('B', 'E', 'C', 'READ_C') if checks.get(c)]
            lines.append(f"| {safe(model)} | {', '.join(present) or 'none'} |")
        lines += ['', 'These checks do not establish correctness, completion of every sampling/dose arm, '
                  'or safety. Download-only models may appear in the selected count.']
    else:
        lines += [f"**Saved status: {safe(result.get('status', 'unavailable'))}.** "
                  'These outcomes are guard-labelled; human audit coverage must be reported separately.', '',
                  '| Model | Benchmark | Guard | Paired contrast | Items | Difference (pp) | 95% interval (pp) |',
                  '| --- | --- | --- | --- | --- | --- | --- |']
        for row in result.get('contrasts', []):
            if row.get('contrast') not in ('B-C', 'B-E', 'E-C'):
                continue
            ci = row.get('ci95')
            interval = ' to '.join(fmt(x) for x in ci) if ci and len(ci) == 2 else 'unavailable'
            values = [row.get(k, 'unavailable') for k in ('model', 'benchmark', 'judge', 'contrast', 'n')]
            lines.append('| ' + ' | '.join(safe(v) for v in values) + f" | {fmt(row.get('diff'))} | {interval} |")
        lines += ['', 'Positive B−C means the image condition had lower refusal. B−E also changes '
                  'content form. Compare unsafe rates, non-answer rates, coverage and audit evidence before '
                  'interpreting any difference as a safety improvement or a vision-specific effect.', '',
                  '**Prediction coverage:**']
        for name, score in result.get('h29', {}).items():
            lines.append(f"- {safe(name)}: {safe(score.get('status', 'unavailable'))}. "
                         'Consult saved R-squared, MAE and baseline errors before judging prediction quality.')
        lines += ['', f"Recorded failures: {len(result.get('failures', []))}. "
                  'No hypothesis verdict is inferred from this prose summary.']
    if meta.get('requires_python_restart'):
        lines += ['', '**CUDA context invalid:** preserve the completed notebook/results before recovery.']
    lines += ['', '**Next:** review the saved evidence, complete the interpretation cell, and verify the '
              'dated notebook/output snapshot before another run.']
    return '\n'.join(lines)
