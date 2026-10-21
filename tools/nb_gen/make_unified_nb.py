"""Build/execute a portable aggregate-only companion; never execute experiment source."""
import argparse
import ast
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from cross_version_table import NAMES, blocks, load, rows  # noqa: E402
from vlm_saved_analysis import analyze_saved, measurement_sensitivity  # noqa: E402
from unified_explanations import (INTRO, QUESTION, VERSIONS, FLOW, HISTORICAL_REVIEW,
                                 DEVELOPMENT_REVIEW, CLAIMS, TOOLS)  # noqa: E402

DOCS = ['docs/STATUS_AND_PAPER_PLAN.md','docs/INDEX.md','docs/NOVELTY_AUDIT_AND_PLAN.md',
        'docs/ANALYSIS_PLAN_MODALITY_SAFETY.md','docs/AMENDMENT_6_CROSSOVER_DRAFT.md',
        'docs/HANDOFF_END_TO_END.md','docs/METHODOLOGY_REVIEW_AND_UPGRADE_PLAN.md','AGENTS.md']
CODE = ['tools/cross_version_table.py','tools/vlm_saved_analysis.py','tools/vlm7_core.py',
        'tools/vlm7_models.py','tools/vlm_crossover.py','tools/nb_gen/make_nb6_part1.py',
        'tools/nb_gen/make_nb6_part2.py','tools/nb_gen/make_nb6.py','tools/nb_gen/make_nb7.py',
        'tools/nb_gen/make_development_pilot_nb.py','tools/nb_gen/make_crossover_nb.py',
        'tools/nb_gen/make_unified_nb.py','tools/nb_gen/unified_explanations.py']
EXTRA_RESULTS = ['v1_smoke_n5/results.json','v3_run1_judges_failed/results.json',
                 'v3_run2_three_judges/results.json','v5_smoke_n16/results_v5.json',
                 'v6_smoke_n16/results_v6.json']
HIST_KEYS = ('version','model','judge','n','A','B','C','D','E','gap')
CX_KEYS = ('judge','outcome','condition','scheduled','valid','positive','unresolved','observed_rate','bounds')


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def clean(value):
    if isinstance(value,float) and not math.isfinite(value):
        return None
    if isinstance(value,dict):
        return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value,list):
        return [clean(v) for v in value]
    if value is None or type(value) in (str,int,float,bool):
        return value
    raise ValueError('Non-JSON value in allowlisted aggregate')


def fields(row, names):
    return {k:clean(row[k]) for k in names}


def inventory(root, paths, role):
    out=[]
    for name in paths:
        p=root/name
        out.append(dict(path=name,role=role,available=p.is_file(),
                        sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None))
    return out


def definitions(path):
    """Inspect syntax only; no notebook outputs or source bodies are copied into the bundle."""
    nb=json.loads(path.read_text())
    found=[]
    for i,cell in enumerate(nb['cells']):
        if cell['cell_type']!='code':
            continue
        source=''.join(cell['source'])
        source='\n'.join('' if line.lstrip().startswith(('!','%')) else line for line in source.splitlines())
        try:
            tree=ast.parse(source)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
                found.append(dict(name=node.name,kind='class' if isinstance(node,ast.ClassDef) else 'function',
                                  cell_index=i,syntax_sha256=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()))
    return found


def code_deltas(maps):
    out=[]
    for a,b in zip(VERSIONS[:6],VERSIONS[1:7]):
        before={r['name']:r['syntax_sha256'] for r in maps[a[0]]}
        after={r['name']:r['syntax_sha256'] for r in maps[b[0]]}
        for status,names in [('added',after.keys()-before.keys()),('removed',before.keys()-after.keys()),
                             ('changed',{k for k in before.keys()&after.keys() if before[k]!=after[k]})]:
            out.append(dict(from_version=a[0],to_version=b[0],change=status,definitions=sorted(names),count=len(names)))
    return out


def compatibility(root, ledger):
    panel=ast.literal_eval(next(n.value for n in ast.parse((root/'tools/vlm7_core.py').read_text()).body
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PANEL7' for t in n.targets)))
    if ledger is None:
        return [dict(model=m,status='not inventoried',meaning='No operational ledger supplied; not evidence of failure') for m,_,_ in panel]
    operational=json.loads(Path(ledger).read_text())
    good=set(operational.get('verified_smoke_models',[]))
    partial=set(operational.get('partial_smoke_models',{}))
    failed=set(operational.get('failed_smoke_models',{}))
    if good&partial or good&failed or partial&failed:
        raise ValueError('Conflicting compatibility ledger categories')
    out=[]
    for m,_,_ in panel:
        status='completed benign checks' if m in good else 'partial' if m in partial else 'failed before response' if m in failed else 'not inventoried'
        meaning=('Execution only; no safety/correctness claim' if m in good else
                 'Image-after-text dose checks unsupported; retain incomplete coverage' if m in partial else
                 'First-generation numerical failure under tested configuration; not model impossibility' if m in failed else 'No ledger entry')
        out.append(dict(model=m,status=status,meaning=meaning))
    return out


def collect(root=ROOT, ledger=None):
    root=Path(root)
    historical=load(root)
    pilot=json.loads((root/'v7_development_core8/pilot_summary.json').read_text())
    cx=json.loads((root/'v7_crossover_core8/results_crossover.json').read_text())
    if cx.get('status')!='guard_labelled_exploratory' or cx.get('human_review')!='pending':
        raise ValueError('New evidence status needs reviewed companion interpretation')
    if (cx['scheduled_items'],cx['completed_target'],cx['completed_guard'],cx['cap_hits'],cx['failures'])!=(8,56,96,17,[]):
        raise ValueError('Crossover evidence changed; update reviewed explanation before rebuilding')
    expected={'P_txt':4,'P_img':5,'S_txt':5,'S_img':8,'P_blank':4,'S_blank':5}
    for judge in ('qwen3guard','wildguard'):
        for cond,n in expected.items():
            cell=next(r for r in cx['cells'] if r['judge']==judge and r['condition']==cond and r['outcome']=='refusal_raw')
            if (cell['positive'],cell['valid'])!=(n,8):
                raise ValueError('Crossover refusal interpretation is stale')
    if pilot.get('historical_pooling_permitted') is not False or pilot.get('human_validated') is not False:
        raise ValueError('Pilot evidence status changed; do not silently pool/validate it')
    saved=analyze_saved(root/'v6_full/results_v6.json')
    measured=measurement_sensitivity(saved)
    maps={v:definitions(root/'notebooks'/nb) for v,nb,*_ in VERSIONS}
    results=[p for _,_,p,*_ in VERSIONS if p]+EXTRA_RESULTS
    sources=(inventory(root,results,'saved evidence; roles distinguished in timeline')+
             inventory(root,['notebooks/'+v[1] for v in VERSIONS],'current local notebook source; not an executed archive')+
             inventory(root,CODE,'current local code')+inventory(root,DOCS,'review or accepted/draft plan'))
    if ledger:
        sources.append(dict(path='private operational ledger (not embedded)',role='compatibility summary provenance',
                            available=True,sha256=hashlib.sha256(Path(ledger).read_bytes()).hexdigest()))
    rates=[]
    for model,record in historical['v6']['results'].items():
        for judge in ('qwen3guard','wildguard'):
            for cond in ('B','E','C','F_txt','F_img','W1_txt','W1_img','G_full','W2_img','B_noise','B_nat','B_irr'):
                value=record['rates'][judge].get(cond)
                if value is not None:
                    rates.append(dict(model=NAMES.get(model,model),judge=judge,condition=cond,
                        nominal_items=record['n'],valid_label_denominator=None,
                        refusal_raw=value.get('refuse_raw'),refusal_nc_adjusted=value.get('refuse3'),
                        nc=value.get('notcomp'),unsafe=record.get('unsafe_rate_all',{}).get(judge,{}).get(cond)))
    smoke=json.loads((root/'v4_smoke_n16/results_v4.json').read_text())
    data=dict(schema='vlm-unified-companion-1',evidence_date='2026-10-20',human_validated=False,
        model_calls=0,historical=[fields(r,HIST_KEYS) for r in rows(historical)],
        v4_smoke=[dict(model=NAMES.get(m,m),nominal_items=r['n'],status='pipeline smoke only; no scientific inference')
                  for m,r in smoke['results'].items() if not m.startswith('_')],
        tables=blocks(historical,pilot),v6_cells=rates,
        v6_verdicts=[dict(hypothesis=k,original_flag=v) for k,v in historical['v6']['prespecified_check'].items()],
        pilot_counts=fields(pilot,('items','target_responses','label_records','failures','elapsed_minutes','human_validated')),
        pilot_rates=[fields(r,('model','judge','cond','n','refusal_positive','refusal_valid_n','unsafe_positive','unsafe_valid_n','nc_positive','nc_valid_n')) for r in pilot['rates']],
        pilot_pairs=[fields(r,('judge','outcome','contrast','paired_n','unresolved_pairs','a_only','b_only','both','neither','net_difference_pp','changed_pct')) for r in pilot['paired_tables']],
        crossover_counts=fields(cx,('scheduled_items','scheduled_target','scheduled_guard','completed_target','completed_guard','keyword_checks','cap_hits','unverified_image_order','readbacks','elapsed_minutes','human_review','window_robustness')),
        crossover_failure_count=len(cx['failures']),crossover_cells=[fields(r,CX_KEYS) for r in cx['cells']],
        crossover_effects=[fields(r,('judge','d_plain','d_steps','interaction','complete_guard_pattern','human_claim')) for r in cx['crossover']],
        transitions=saved['transitions'],measurement=measured,code_maps=maps,code_deltas=code_deltas(maps),
        compatibility=compatibility(root,ledger),provenance=sources,
        timeline=[dict(version=v,notebook=nb,result=result,kind=kind,question=q,change=change,limitation=limit)
                  for v,nb,result,kind,q,change,limit in VERSIONS])
    wp=root/'v7_window_core8/results_window.json'
    if wp.is_file():
        window=json.loads(wp.read_text())
        data['window_counts']=fields(window,('target_completed','units_completed','guards_completed','failures','full_cap_hits','prefix_drift','missing_guard_labels','human_review'))
        data['window_crossover']=[fields(r,('reference','window','d_plain','d_steps','classification')) for r in window['crossover']]
        data['window_changes']=[fields(r,('reference','conclusion','limitation')) for r in window['changes']]
        data['provenance']+=inventory(root,['v7_window_core8/results_window.json'],'completed exploratory window aggregates')
    return clean(data)


RUNTIME = '''import hashlib, html, json
from IPython.display import Markdown, display

def digest_companion(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()

def show_rows(records, columns=None):
    if not records:
        print('Unavailable in this saved snapshot; no result inferred.')
        return
    columns = columns or list(records[0])
    def text(value):
        if value is None: return 'unavailable'
        if isinstance(value,float): return f'{value:.6g}'
        if isinstance(value,(dict,list)): return json.dumps(value,ensure_ascii=False)
        return str(value)
    def cell(value): return html.escape(text(value)).replace('|','&#124;').replace('\\n','<br>')
    table = '| '+' | '.join(cell(c) for c in columns)+' |\\n'
    table += '| '+' | '.join('---' for _ in columns)+' |\\n'
    table += '\\n'.join('| '+' | '.join(cell(r.get(c)) for c in columns)+' |' for r in records)
    display(Markdown(table))
'''


def build(output=None, root=ROOT, ledger=None):
    data=collect(root,ledger)
    cells=[]
    def add(kind,text):
        if kind=='code':
            ast.parse(text)
        cell=dict(cell_type=kind,metadata={},source=text.splitlines(True),id=f'companion-{len(cells):03d}')
        if kind=='code':
            cell.update(execution_count=None,outputs=[])
        cells.append(cell)
    add('markdown',INTRO)
    add('markdown','## Contents\n\n'+ '\n'.join([
        '1. Question and condition glossary','2. Version timeline and individual chapters','3. End-to-end code and syntax map',
        '4. Historical results, two benchmarks and see-saw observations','5. Measurement diagnostics and original verdicts',
        '6. Compatibility attempts and failures','7. Two separate development studies','8. Prior art and claim status',
        '9. Maintenance tools','10. Source provenance and refresh instructions']))
    encoded=json.dumps(data,ensure_ascii=False,allow_nan=False)
    add('code',RUNTIME+f'\nBUNDLE = json.loads({encoded!r})\nEXPECTED_BUNDLE_SHA256 = {digest(data)!r}\n'
        'assert digest_companion(BUNDLE)==EXPECTED_BUNDLE_SHA256\n'
        "assert BUNDLE['model_calls']==0 and BUNDLE['human_validated'] is False\n"
        "print('Embedded aggregate snapshot verified. CPU-only; zero model calls; no human validation.')\n")
    review_path=root/'audit_work/window_preparation_PRIVATE_20261020/review_aggregates.json'
    if review_path.is_file():
        review=json.loads(review_path.read_text())
        if review['scheduled_answers']!=48: raise ValueError('Unexpected review scope')
        counts=[fields(r,('axis','resolved_pairs','unresolved_pairs','agreement','kappa')) for r in review['between_reviewers']]
        add('markdown','## Latest measurement review — 20 October 2026\n\nHuman A received LLM assistance on some examples. B is GPT-6.1-Sol, user-confirmed; backend/settings unknown. Labels remain separate. Seven harm disagreements are unresolved; no selective correction. The response-window GPU study completed 32 responses and 128 guard evaluations; eight responses hit the cap and new human review is pending. The original crossover was not observed.')
        add('code','print('+repr(counts)+')')
        add('markdown','Refusal agrees 48/48; harm 41/48 with all-negative B. Comprehension agrees on 48 categories including 17 uncertain; resolved-only kappa is undefined. Agreement does not establish validity. See vlm_window_study.ipynb and status section 15.')
    if 'window_counts' in data:
        add('markdown','## Completed response-window study — 20 October 2026\n\nThese are saved GPU outcomes displayed on CPU, not a new inference run.')
        add('code',"print(BUNDLE['window_counts'])\nshow_rows(BUNDLE['window_crossover'])\nshow_rows(BUNDLE['window_changes'])\n")
        add('markdown','Both guards retained every refusal, unsafe and NC label between paired windows. No crossover at either window. Eight 512-token cap hits and pending human review leave the broader diagnostic unresolved. Prefixes match the archived 256-token outputs; this is one development sample, not independent confirmation.')
    add('markdown',QUESTION)
    add('markdown','## 2. Version timeline\n\nEach row is a different design or evidence role, not another independent replication.')
    add('code',"show_rows(BUNDLE['timeline'],['version','kind','question','change','limitation'])\n")
    add('markdown','### Timeline interpretation — editable\n\nV1–v3 developed the question and exposed judge problems. '
        'V4 is a smoke pipeline. V5 has known invalid blocks. V6 is the main historical scientific run. '
        'V7 engineering checks and two small development studies do not complete its fresh eight-model hypotheses.')
    for v,nb,source,kind,q,change,limit in VERSIONS:
        add('markdown',f'### {v}: {q}\n\n**Change:** {change}\n\n**Source:** `notebooks/{nb}`; '
            f"saved evidence: `{source or 'separately archived benign stages'}`.\n\n**Status:** {kind}. {limit}")
        add('code',f"show_rows(BUNDLE['code_maps'][{v!r}],['name','kind','cell_index'])\n"+
            (f"show_rows([r for r in BUNDLE['historical'] if r['version']=={v!r}],['model','judge','n','A','B','C','D','E','gap'])\n"
             if v in ('v1','v2','v3','v5','v6') else "show_rows(BUNDLE['v4_smoke'])\n" if v=='v4' else
             "print('Evidence for this stage is shown in its separate section below; no pooled rate.')\n"))
        add('markdown',f'**Editable interpretation ({v}):** {limit} '
            'Function locations describe the current local source. Executed code/output archives remain the authority for what ran.')
    add('markdown',FLOW)
    add('code',"show_rows(BUNDLE['code_deltas'],['from_version','to_version','change','count','definitions'])\n")
    add('markdown','### Code-difference interpretation — editable\n\nA renamed function can appear as removal/addition. '
        'Shared generated cells can change many definitions at once. These are static syntax differences, '
        'not behavior tests or proof that more functions mean better science. Read the version explanations alongside them.')
    add('markdown','## 4. Historical scientific results\n\nTables below reproduce `cross_version_table.py`. '
        'Values are percentages in these rendered tables; per-version numeric tables above use fractions. '
        'No trend line or pooled effect across versions is calculated.')
    for key,title in [('cross','Cross-version A–E'),('current','V6 main MM-SafetyBench comparison'),
                      ('figstep','V6 FigStep, separate benchmark'),('coupling','Historical coupling'),('steering','Historical steering observations')]:
        add('markdown','### '+title)
        add('code',f"display(Markdown(BUNDLE['tables'][{key!r}]))\n")
        add('markdown',HISTORICAL_REVIEW if key=='current' else
            '**Editable review:** preserve version, judge, benchmark and population. '
            'Legacy/cached outcomes are not independent replications; these scores have no human reference. '
            'For steering, keep benign over-refusal costs and the limited checkpoint scope alongside any benefit.')
    add('code',"try:\n    import matplotlib.pyplot as plt\nexcept ImportError:\n    print('Optional figure unavailable; all numeric tables above remain complete.')\nelse:\n"
        "    fig, axes = plt.subplots(1,2,figsize=(13,4.5),sharey=True)\n"
        "    models = list(dict.fromkeys(r['model'] for r in BUNDLE['v6_cells']))\n"
        "    for ax, judge in zip(axes,('qwen3guard','wildguard')):\n"
        "        for offset,cond,label in [(-.24,'B','Original text'),(0,'E','Matched payload text'),(.24,'C','Benchmark image')]:\n"
        "            values = [next(r['refusal_nc_adjusted'] for r in BUNDLE['v6_cells'] if r['model']==m and r['judge']==judge and r['condition']==cond) for m in models]\n"
        "            ax.bar([i+offset for i in range(len(models))],[100*x for x in values],width=.23,label=label)\n"
        "        ax.set_xticks(range(len(models)),models,rotation=15)\n        ax.set_title(judge)\n        ax.set_ylim(0,100)\n"
        "    axes[0].set_ylabel('NC-adjusted refusal (%)')\n    axes[0].legend(fontsize=8)\n"
        "    fig.suptitle('V6 exploratory evidence only; B/E also change content form')\n    fig.tight_layout()\n    display(fig)\n    plt.close(fig)\n")
    add('markdown',HISTORICAL_REVIEW)
    add('markdown','## 5. Measurement and paired diagnostics\n\nUse saved jointly valid refusal counts only. '
        'Harmful transitions cannot be reconstructed from refusal or marginal harm means.')
    add('code',"show_rows([r for r in BUNDLE['transitions'] if r['condition_a']=='E' and r['condition_b']=='C'],"
        "['benchmark','model','judge','paired_n','a_only_refuses','b_only_refuses','net_gap_pp','changed_refusal_pct'])\n"
        "show_rows(BUNDLE['v6_cells'],['model','judge','condition','nominal_items','valid_label_denominator','refusal_raw','refusal_nc_adjusted','nc','unsafe'])\n")
    add('markdown','### Diagnostic interpretation — editable\n\nOpposing refusal changes can cancel in the mean; '
        'that arithmetic is not a new mechanism or evidence of image-only harmful help. Raw and NC-adjusted refusal '
        'are different definitions. Nominal item counts must not be passed off as verified parsed-label denominators. '
        'These repeated analyses reuse the same historical responses; they are not additional independent experiments.')
    add('code',"show_rows(BUNDLE['v6_verdicts'])\n"
        "print('Original historical flags only; exploratory, not human-validated confirmation.')\n"
        "show_rows(sorted(BUNDLE['measurement']['scoring_rule_shifts'],key=lambda r:abs(r['raw_minus_nc_pp']),reverse=True)[:10])\n")
    add('markdown','### Original verdicts — editable\n\nRetain false, SPLIT and INCONCLUSIVE flags as saved. '
        'A true program flag does not override missing human validation or prove a causal explanation. '
        'The displayed ten scoring shifts are selected by magnitude for readability, not significance; '
        'all shifts are embedded in the payload. Do not select a convenient guard or corrected definition after looking.')
    add('markdown','## 6. Benign compatibility panel\n\nSource: allowlisted operational ledger categories, '
        'whose hash appears below; private ledger content is not embedded. This is engineering evidence, not safety scoring. '
        'If no ledger was supplied, all rows explicitly say not inventoried.')
    add('code',"show_rows(BUNDLE['compatibility'])\n")
    add('markdown','### Compatibility interpretation — editable\n\nCompleted benign checks do not establish correctness. '
        'Partial order checks and constant processed image-token counts limit dose interpretation. '
        'A numerical failure applies to that tested configuration, not every possible implementation of the checkpoint. '
        'Do not retry unchanged failures or call the attempted panel a completed eight-model scientific study.')
    add('markdown','## 7. Separate development studies\n\n### Qwen2 core-eight B/E/C pilot')
    add('code',"show_rows([BUNDLE['pilot_counts']])\ndisplay(Markdown(BUNDLE['tables']['pilot']))\n"
        "show_rows([r for r in BUNDLE['pilot_pairs'] if r['contrast']=='E-C'])\n")
    add('markdown',DEVELOPMENT_REVIEW)
    add('markdown','### Qwen2.5 core-eight matched crossover')
    add('code',"show_rows([BUNDLE['crossover_counts']])\n"
        "show_rows([r for r in BUNDLE['crossover_cells'] if r['judge']!='keyword' and r['outcome'] in ('refusal_raw','unsafe')])\n"
        "show_rows(BUNDLE['crossover_effects'])\nprint('Recorded failures:',BUNDLE['crossover_failure_count'])\n")
    add('markdown',DEVELOPMENT_REVIEW)
    add('markdown',CLAIMS)
    add('markdown',TOOLS)
    add('markdown','## 10. Provenance and refresh\n\nThe following hashes identify the source bytes used at build time. '
        'Result hashes support tracing table inputs. Current source notebook hashes do **not** retrospectively attest '
        'the executed historical runtime. Private response/label records and notebook outputs from old sources are never embedded. '
        'The companion includes only selected aggregate fields, function names/cell locations and reviewed prose.')
    add('code',"show_rows(BUNDLE['provenance'])\n"
        "assert digest_companion(BUNDLE)==EXPECTED_BUNDLE_SHA256\n"
        "print('Snapshot hash:',EXPECTED_BUNDLE_SHA256)\n"
        "print('No new inference, Drive mount, remote request, training or human annotation took place.')\n")
    add('markdown','### Keep this companion current\n\nFrom the repository root:\n\n'
        '```bash\npython3 tools/nb_gen/make_unified_nb.py --execute\n```\n\n'
        'Optional local compatibility ledger input: `--compatibility-ledger audit_work/v7_autonomy_state_PRIVATE.json`. '
        'Only known model/category fields are extracted; private ledger text is not embedded. '
        'The notebook includes a frozen embedded aggregate snapshot, so it opens standalone in Colab/Jupyter '
        'without connecting to Drive. Re-running display cells does not refresh source evidence. '
        'Regenerate after updating the saved aggregate files or source code. Keep executed experiment archives unchanged.\n\n'
        '**Knowledge ownership:** `STATUS_AND_PAPER_PLAN.md` is the maintained written synthesis, '
        'this notebook is its computational reading companion, and the result files/archived manifests are evidence. '
        'Human review, fresh confirmation and any further stage retain their existing approvals/gates. '
        'Nothing in this companion launches another experiment, installs a plugin, publishes a website or pushes Git.')
    nb=dict(nbformat=4,nbformat_minor=5,cells=cells,metadata=dict(
        kernelspec=dict(display_name='Python 3',language='python',name='python3'),
        colab=dict(provenance=[]),language_info=dict(name='python'),
        companion=dict(schema=data['schema'],bundle_sha256=digest(data),evidence_date=data['evidence_date'],model_calls=0)))
    output=Path(output or ROOT/'notebooks/vlm_project_companion.ipynb')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(nb,ensure_ascii=False,allow_nan=False)+'\n')
    return nb


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'notebooks/vlm_project_companion.ipynb')
    parser.add_argument('--compatibility-ledger',type=Path)
    parser.add_argument('--execute',action='store_true',help='CPU display cells only; zero model calls')
    args=parser.parse_args()
    nb=build(args.output,ledger=args.compatibility_ledger)
    if args.execute:
        nb=execute_cpu(nb)
        args.output.write_text(json.dumps(nb,ensure_ascii=False,allow_nan=False)+'\n')
    print('Generated',args.output,'| cells:',len(nb['cells']),'| model calls: 0')


def execute_cpu(nb):
    """Execute trusted generated display cells in-process, without a socket/kernel server."""
    import base64
    import copy
    import nbformat
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    shell=InteractiveShell.instance()
    try:
        import matplotlib
        matplotlib.use('Agg',force=True)
        from matplotlib.figure import Figure
        from IPython.core.pylabtools import print_figure
        shell.display_formatter.formatters['image/png'].for_type(Figure,lambda f:print_figure(f,fmt='png'))
    except ImportError:
        pass
    notebook=copy.deepcopy(nb)
    counter=0
    for cell in notebook['cells']:
        if cell['cell_type']!='code':
            continue
        counter+=1
        with capture_output() as captured:
            result=shell.run_cell(''.join(cell['source']),store_history=False)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError('Companion display cell failed') from (result.error_before_exec or result.error_in_exec)
        outputs=[]
        if captured.stdout:
            outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr:
            outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
        for rich in captured.outputs:
            data={k:base64.b64encode(v).decode() if isinstance(v,bytes) else v for k,v in rich.data.items()}
            outputs.append(nbformat.v4.new_output('display_data',data=data,metadata=rich.metadata or {}))
        cell.update(execution_count=counter,outputs=outputs)
    nbformat.validate(nbformat.from_dict(notebook))
    return notebook


if __name__=='__main__':
    main()
