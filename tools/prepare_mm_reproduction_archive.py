"""Export aggregate results and output-cleared completed notebooks from college Drive.

No models or judges are invoked. Raw answers and individual judgments remain private.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = 'all_three_ASR_RR_complete_20261109T034959Z_PRIVATE'
NOTEBOOKS = {
    'llava_7b.ipynb': ('llava_complete_20261108T213651Z_PRIVATE', 'completed_notebook.ipynb'),
    'instructblip.ipynb': ('instructblip_complete_20261108T111407Z_PRIVATE',
                         'mm_safetybench_instructblip_run_all.ipynb'),
    'qwen25_text.ipynb': ('qwen_complete_20261108T223517Z_PRIVATE',
                        'mm_safetybench_qwen_text_run_all.ipynb'),
    'qwen25_images.ipynb': ('qwen_complete_20261108T223517Z_PRIVATE',
                          'mm_safetybench_qwen_images_completed.ipynb'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify_snapshot(folder):
    source = folder / 'snapshot_manifest_PRIVATE.json'
    manifest = json.loads(source.read_text())
    total = 0
    for rel, info in manifest['files'].items():
        path = folder / rel
        expected = info['sha256'] if isinstance(info, dict) else info
        if sha(path) != expected:
            raise ValueError(f'Snapshot checksum mismatch in {folder.name}/{rel}')
        total += path.stat().st_size
    return dict(manifest_sha256=sha(source), verified_files=len(manifest['files']),
                verified_bytes=total)


def export_notebook(source, destination):
    notebook = json.loads(source.read_text())
    cells = []
    for cell in notebook['cells']:
        clean = dict(cell_type=cell['cell_type'], metadata={}, source=cell['source'])
        if clean['cell_type'] == 'code':
            clean.update(execution_count=None, outputs=[])
        cells.append(clean)
    cells.insert(0, dict(cell_type='markdown', metadata={}, source=[
        '# Completed MM-SafetyBench run — public source archive\n',
        '\n',
        'This is the code from a preserved completed-run notebook. Outputs, attachments and '
        'account/session metadata are cleared for public sharing. The original notebook with '
        'outputs and its raw data remain in the private college Drive snapshot.\n',
        '\n',
        'See [the archive guide](../../docs/MM_SAFETYBENCH_ARCHIVE.md) for completed counts, '
        'dependencies and historical notebook status. Execution uses GPU quota and may require '
        'the archived Drive artifacts referenced below. This export does not execute any cell.\n',
    ]))
    metadata = {k: notebook.get('metadata', {})[k] for k in ('kernelspec', 'language_info', 'accelerator')
                if k in notebook.get('metadata', {})}
    exported = dict(cells=cells, metadata=metadata,
                    nbformat=notebook['nbformat'], nbformat_minor=notebook['nbformat_minor'])
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_json(destination, exported)
    return dict(source_sha256=sha(source), exported_sha256=sha(destination),
                code_cells=sum(c['cell_type'] == 'code' for c in cells),
                outputs_cleared=True, source_code_preserved=True)


def export_csv(source, destination, expected_rows):
    with source.open() as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        fields = reader.fieldnames
    if len(rows) != expected_rows:
        raise ValueError('Unexpected aggregate table shape')
    # Explicit allowlist. Any new text-bearing field requires review before public export.
    allowed = {'model', 'cohort', 'scenario', 'condition', 'planned', 'no_response',
               'safety_judged', 'unsafe', 'ASR_among_judged', 'ASR_lower', 'ASR_upper',
               'RR_planned', 'refusal_judged', 'refused', 'RR_among_judged', 'RR_lower',
               'RR_upper', 'ASR_judged', 'RR_judged', 'ASR_pooled_among_judged_pct',
               'ASR_full_denominator_lower_pct', 'ASR_full_denominator_upper_pct',
               'ASR_macro_13_scenarios_among_judged_pct', 'RR_pooled_among_judged_pct',
               'RR_full_denominator_lower_pct', 'RR_full_denominator_upper_pct',
               'RR_macro_13_scenarios_among_judged_pct'}
    if set(fields) - allowed:
        raise ValueError('Unreviewed field in aggregate table')
    destination.write_bytes(source.read_bytes())
    return dict(rows=len(rows), source_sha256=sha(source), exported_sha256=sha(destination))


def prepare(runs):
    snapshots = runs / 'Snapshots_PRIVATE'
    final = snapshots / FINAL
    verification = verify_snapshot(final)
    generation = {name: verify_snapshot(snapshots / name)
                  for name in sorted({v[0] for v in NOTEBOOKS.values()})}
    report = dict(archive_date='2026-11-10', scope='completed_MM_SafetyBench_panel',
                  privacy='aggregate_metrics_and_output_cleared_source_only',
                  private_final_snapshot=verification,
                  private_generation_snapshots=generation, notebooks={}, tables={},
                  dataset=dict(paper='https://arxiv.org/html/2311.17600v5',
                               release_commit='b80eedea3db312c09ded2082813390f68e750ef3',
                               questions=1680, scenarios=13,
                               conditions=['TEXT', 'SD', 'TYPO', 'SD_TYPO'],
                               planned_cases_per_model=6720,
                               content_location='author_release_and_private_college_Drive'))
    for name, (folder, source) in NOTEBOOKS.items():
        dest = ROOT / 'notebooks/completed_mm_safetybench' / name
        report['notebooks'][str(dest.relative_to(ROOT))] = export_notebook(snapshots / folder / source, dest)
    for source, output, n in (
        ('ASR_RR_by_model_scenario_condition_PRIVATE.csv', 'mm_safetybench_asr_rr_by_scenario.csv', 312),
        ('ASR_RR_by_model_condition_PRIVATE.csv', 'mm_safetybench_asr_rr_by_condition.csv', 24),
    ):
        dest = ROOT / 'reports' / output
        report['tables'][str(dest.relative_to(ROOT))] = export_csv(final / 'Combined_Results_PRIVATE' / source, dest, n)
    manifest = json.loads((final / 'snapshot_manifest_PRIVATE.json').read_text())['verification']
    report.update(judge=manifest['judge'], model_counts=manifest['model_counts'],
                  metric_outcomes=manifest['metric_outcomes'],
                  cost_or_reservations_usd=manifest['total_cost_or_reservations_usd'],
                  human_validation=False, exact_historical_reproduction=False,
                  source_record_verified_utc=manifest['verified_utc'])
    write_json(ROOT / 'reports/mm_safetybench_archive_manifest.json', report)
    print(dict(notebooks=len(NOTEBOOKS), aggregate_tables=2,
               verified_private_snapshot_files=verification['verified_files'],
               raw_answers_exported=0, individual_judgments_exported=0))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=Path, default=(
        Path.home() / 'Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com'
        / 'My Drive/MM_SafetyBench_Full_20261102_PRIVATE/Runs'))
    prepare(parser.parse_args().runs)
