"""Inspect saved Drive notebooks read-only; publish structure/aggregates, never replies."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DRIVE=Path('/Users/aryamandev/Library/CloudStorage/GoogleDrive-aryamandev.college@gmail.com/My Drive')
COLAB=DRIVE/'Colab Notebooks'
PLAN={
'v1':('vlm_modality_tradeoff.ipynb','vlm_modality_tradeoff.ipynb','v1_full_n30/results.json','A/B/C/D, coupling and inference-time activation steering. No training.','`analyse`, `boot_diff`, `mcnemar_exact`, `run_steering`. A is a different backbone model; B/C changes stimulus form and framing. Historical labels are not interchangeable with v6.','The tested simple see-saw is unsupported; steering can raise both channels and benign refusal.'),
'v2':('vlm_modality_tradeoff_v2.ipynb','vlm_modality_tradeoff_v2.ipynb','v2_run/results.json','Add phrase-text E, benign prompts, random items, random-direction steering control and clustered resampling.','`boot_diff_cluster`, `intents_for`, `run_steering`; retain the actual cache/label version. Baseline versus text twin is not a pure wording contrast.','Qwen2 steering strength 0.5: harmful text/image refusal 80.0%/76.7%; benign text 37.5%; not a deployable safety mitigation.'),
'v3':('vlm_modality_tradeoff_v3.ipynb','vlm_modality_tradeoff_v3.ipynb','v3_final_four_judges/results.json','Multiple judges, readback and a telescoping decomposition of the refusal gap.','`judge_qwen3guard`, `judge_wildguard`, `decompose`, `cluster_boot`, `coupling`. Algebraic components depend on the chosen path; they are not uniquely identified causal mechanisms.','Invalid early rubric judges were retired; report guard-specific results rather than a pooled consensus.'),
'v4':('vlm_modality_tradeoff_v4.ipynb','vlm_modality_tradeoff_v4_smoke.ipynb','v4_smoke_n16/results_v4.json','Introduce a larger wrapper/content/carrier grid, LLaVA, presence and harmfulness.','`generation_cache_context`, `gen_cond`, `contrast`, `unsafe_arr`. Saved notebook is a smoke run, not the full factorial scientific dataset.','Engineering/control-flow evidence only; do not interpret small smoke percentages as substantive findings.'),
'v5':('vlm_modality_tradeoff_v5.ipynb','vlm_modality_tradeoff_v5.ipynb','v5_full/results_v5.json','Full exploratory grid, font treatment, judge disagreement, Holm checks and private audit export.','`run_pair`, `judge_qwen3guard`, `judge_wildguard`, `holm`. Neutral-input judging used the wrong target context; preprocessing upscaled intended small-font images.','Preserve v5 outcomes, but use the corrected v6 context/preprocessing for the maintained interpretation.'),
'v6':('vlm_modality_tradeoff_v6.ipynb','vlm_modality_tradeoff_v6.ipynb','v6_full/results_v6.json','Stimulus-aware relabeling; true 12/20/38-pixel rendering; presence, FigStep and batch comparison.','Saved cells 15/17/19 define guards, statistics and result checks (zero-based). `contrast` uses jointly finite pairs; `gee_grid` uses exchangeable binomial GEE grouped by item. Guards slice replies to 1,500 characters.','Historical Qwen3Guard B/E/C refusal: Qwen2 66.1/18.4/15.1%; Qwen2.5 74.3/51.0/44.1%; LLaVA 45.4/37.5/2.6%. H21 false, H22 split, H23 true, H24 false, H25 true, H26 inconclusive, H27 false.'),
'v7':('vlm_modality_tradeoff_v7.ipynb','v7_completed_runs/vlm_modality_tradeoff_v7.ipynb',None,'Eight-checkpoint benign compatibility, native adapters, exact identity caches, split/gate checks, sampling and image dose/order machinery.','`Model7`, `Guard7`, `cached7`, `paired7`, `forecast7`, `human_gate7`. Implemented arms are not all executed scientific outcomes. Inspect individual preserved attempts.','Three completed benign checks, two partial, three failed before response; no eight-model scientific or fresh-confirmatory result.'),
'expanded':('vlm_research_expanded.ipynb','vlm_research_expanded.ipynb',None,'Compatibility/development runner plus no-inference historical paired-transition and scoring-sensitivity analysis.','`analyze_saved`, `paired_counts`, `transition_readout`, `sensitivity_readout`. Reconstruct refusal tables only when saved discordances and paired margins agree; never reconstruct joint harm from separate marginals.','Qwen2 E/C example: 31 text-only refusals, 21 image-only, n=304; net 3.3 pp versus 17.1% changing label. This is reused historical evidence.'),
'pilot':('vlm_development_pilot.ipynb','v7_completed_runs/2026-10-19_123518_Qwen2_CORE8_DEVELOPMENT_COMPLETED/completed_notebook.ipynb','v7_development_core8/pilot_summary.json','Eight seen OCR-verified MM items, Qwen2-VL-2B, B/E/C plus separate readback.','Exact dataset/source/response/label hashes checked by `summarize_development_pilot.py`. Eight items are purposive development coverage, not a population sample.','32 responses and 72 automated label records; no failures. E/C refusal and harmfulness labels match within each guard. Sixteen of 24 answering calls hit 256 tokens.'),
'crossover':('vlm_crossover_development.ipynb','vlm_crossover_development.ipynb','v7_crossover_core8/results_crossover.json','Pinned Qwen2.5-VL-3B FP16 greedy batch-one; eight seen full questions; 2 wrappers × 2 carriers plus 2 blank arms and readback.','`specs_cx`, `select_cx`, `paired_cx`, `summarize_cx`. OCR eligibility then fixed-seed selection; raw refusal is the primary diagnostic. The new steps wording differs from the legacy v6 pair.','56 target/96 guard calls; no failures. Plain text/image 4/8 vs 5/8; steps 5/8 vs 8/8. No crossover; 17 of 48 answering responses capped; readback 8/8.'),
'human_validation':('vlm_next_stage_human_validation.ipynb','vlm_next_stage_human_validation_2026-10-19_154115.ipynb',None,'CPU reading notebook plus optional original 48-answer private review/import analysis.','`package`, `review`, `outcomes`, `agreement`, `analyze`. Package IDs, source hashes, duplicate/missing labels and reference kind are checked; labels are not automatically adjudicated.','Saved preparation execution is not evidence that the full v6 human gate passed. Original assisted A versus auxiliary GPT-6.1-Sol comparison is descriptive; the new 64-unit review is distinct.'),
'window':('vlm_window_study.ipynb','vlm_window_study.ipynb','v7_window_core8/results_window.json','32 up-to-512-token generations from the same eight items and four core arms; derive prefix256/full512 from generated IDs.','`window_views`, `window_summary`, `WindowRun`. Verify token decode/EOS and original prefix; `Guard7` uses full selected reply without the old character slice. 64 units share 32 responses.','32 target, 64 units, 128 guard labels; zero failures/missing labels; zero prefix drift. No guard-label changes or crossover; eight full cap hits. New human review pending; broader diagnostic unresolved.'),
'companion':('vlm_project_companion.ipynb',None,None,'Portable hash-checked allowlisted cross-version snapshot, source map, tables and figures.','`make_unified_nb.collect`, `execute_cpu`; reads saved aggregates and inspects code syntax, never executes experiment bodies. Local refreshed copy is newer than earlier Drive companion snapshots.','CPU presentation/reproduction only, zero target/guard calls. This is the best reading entry point, not an additional experiment.'),
'methodology':('vlm_methodology_review.ipynb',None,None,'Literature-to-design explanation with a synthetic weighted human/autorater estimation example.','Synthetic numeric illustration; statistical assumptions and design weights are teaching material, not observed calibration of our runs.','No model downloads, no human-validation result and no new empirical VLM finding.')}


def inspect(path):
 raw=path.read_bytes();nb=json.loads(raw);cells=[];all_code=[]
 for i,c in enumerate(nb['cells']):
  if c['cell_type']!='code':continue
  source=''.join(c['source']);all_code.append(source)
  cleaned='\n'.join('' if line.lstrip().startswith(('%','!')) else line for line in source.splitlines())
  defs=[]
  try:
   defs=[n.name for n in ast.parse(cleaned).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
  except SyntaxError:pass
  outputs=c.get('outputs',[])
  # Read output structures, but retain no response or label content.
  cells.append(dict(index=i,execution=c.get('execution_count'),outputs=len(outputs),
                    errors=[o.get('ename','Error') for o in outputs if o.get('output_type')=='error'],
                    figures=sum('image/png' in o.get('data',{}) for o in outputs),definitions=defs))
 code='\n'.join(all_code)
 return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),code_sha256=hashlib.sha256(code.encode()).hexdigest(),
             code_cells=len(cells),executed=sum(c['execution'] is not None for c in cells),outputs=sum(c['outputs'] for c in cells),
             errors=[e for c in cells for e in c['errors']],cells=cells,
             historical_character_slice='r[:1500]' in code,full_reply_guard='no hidden 1500-character truncation' in code,
             explanation_headings=sum(c['cell_type']=='markdown' and any(w in ''.join(c['source']).lower() for w in ('interpret','what this','reviewed','explanation')) for c in nb['cells']))


def build():
 paths=set(COLAB.glob('vlm_*.ipynb'))|set((COLAB/'v7_completed_runs').rglob('*.ipynb'))
 paths|=set((DRIVE/'vlm_tradeoff_out_v7/development').rglob('*.ipynb'))
 paths|=set((DRIVE/'vlm_tradeoff_analysis').rglob('*.ipynb'))
 local=set((ROOT/'notebooks').glob('vlm_*.ipynb'))
 records={str(p):inspect(p) for p in sorted(paths|local)}
 private=ROOT/'audit_work/notebook_technical_audit_PRIVATE_20261022.json'
 private.write_text(json.dumps(records,indent=2)+'\n')
 doc=['# Technical notebook walkthrough for the advisor',
      '\nReviewed 22 October 2026. Read actual saved Drive notebooks as JSON, including code and output structures; no notebook was rerun, changed or interrupted. Raw outputs were not copied into this document. The 14-slide technical deck links to this audit; the maintained scientific narrative is [STATUS_AND_PAPER_PLAN.md](STATUS_AND_PAPER_PLAN.md).',
      '\n## 1. What evidence should be brought to the meeting?',
      '\nBring the paired study contract, exact input/guard protocol, estimator definition, aggregate table, failure/denominator/cap coverage, and source notebook/cell. A collection of notebook screenshots alone cannot distinguish changed prompts, scoring or reused generations. Code cells below use **zero-based notebook indices**, not execution counters.',
      f'\nRead **{len(paths)} saved Drive notebooks/archives** and **{len(local)} local notebooks**. Archives include incomplete attempts and duplicates; these are not {len(paths)} independent experiments. Local generated inputs are not substitutes for executed Drive files. Error-free notebook outputs can still contain caught model failures; inspect the saved failure aggregates.',
      '\n## 2. Technical definitions and analysis actually implemented',
      '\n- Binary refusal contrast: `Delta(a,b) = mean(R_a - R_b)` on the same jointly valid items. Report raw versus frozen-NC-adjusted definitions separately; missing parses are not negative labels.',
      '- Exact McNemar: let `b` be a-only positives and `c` b-only positives. The implementation uses the two-sided Binomial(b+c, 0.5) tail, capped at 1. This tests paired discordance symmetry, not harm severity or equivalence.',
      '- Historical scenario interval: compute one mean paired difference per represented scenario; `mean(d_s) +/- t_(k-1, .975) * sd(d_s)/sqrt(k)`. With all eight MM scenarios, df=7. Saved `diff` is pooled over valid items, while `t_ci` centers on the equal-scenario mean; missingness can make those targets differ.',
      '- Historical equivalence flag: the 90% scenario interval must lie strictly inside +/-0.10. A degenerate interval from eight all-equal pairs is not accepted as population equivalence. Holm correction is implemented for the declared test families, not blanket justification for every exploratory table.',
      '- GEE grid: `logit Pr(R_iwm=1) = beta0 + betaI*I + beta1*W1 + beta2*W2 + gamma1*I*W1 + gamma2*I*W2`. Binomial family, exchangeable working correlation, **item groups**; default robust covariance. Image log-odds are betaI, betaI+gamma1, betaI+gamma2. These are not percentage-point interactions; scenario t intervals above use a different grouping.',
      '- V6 guard input: actual stimulus plus `reply[:1500]` (characters), with separate NC rules. Qwen3Guard safety Controversial was not equivalent to missing harm under the old mapping. The newer `harm_cx` preserves Controversial as unresolved and `Guard7` receives the full selected response. Thus old and new labels differ in protocol, not merely model/version.',
      '- Matched development: `d_P = r(P_img)-r(P_txt)`, `d_S = r(S_img)-r(S_txt)`, interaction `d_S-d_P`. Chosen crossover requires `d_P<0`, `d_S>=0.15` and positive interaction. Current means are +0.125/+0.375, so the condition fails despite a +0.25 interaction.',
      '- Development/window comparisons use `paired_cx`: average paired differences within each scenario, then average over all eight scenarios; no new population confidence interval is inferred. One item per scenario makes this equal to the paired item mean when coverage is complete.',
      '- Window unit: decode generated IDs `t[0:256]` and `t[0:512]` from **one** generation, verify the full decode against the saved reply, retain EOS/cap evidence, compare prefixes to archived 256-token replies. Thirty-two answers give 64 dependent units; two guards give 128 evaluations.',
      '- Missing-label cell bounds: if k positives and u unresolved among N scheduled, rate is bounded by `[k/N,(k+u)/N]`; contrast bounds subtract opposite endpoints. These are deterministic ambiguity bounds, not confidence intervals or guarantees about annotation error.',
      '- Human/LLM agreement: `kappa=(p_o-p_e)/(1-p_e)`. Harm has observed agreement 41/48, but all-negative B implies the same chance agreement, so kappa=0. Comprehension including UNCERTAIN agrees, but the resolved-only single-class kappa is undefined. Neither annotator is automatically ground truth.',
      '\n## 3. Notebook-by-notebook explanations and saved output evidence']
 for label,(name,drive,result,design,method,finding) in PLAN.items():
  chosen=COLAB/drive if drive else ROOT/'notebooks'/name
  record=records[str(chosen)];loc=records[str(ROOT/'notebooks'/name)]
  doc+=['\n### '+label+' — '+name,
        '\n**Design / question.** '+design,
        '\n**Implementation / estimator.** '+method,
        '\n**Observed result / limit.** '+finding,
        '\n**Read the notebook:** ['+('saved Drive copy' if drive else 'current local CPU notebook')+'](<'+str(chosen)+'>). '+('Local source: ['+name+'](../notebooks/'+name+'). ' if drive else '')+('Aggregate: [`'+result+'`](../'+result+').' if result else 'Associated results are described in the maintained status; no single pooled aggregate is implied.'),
        f"\n**Saved inspection:** {record['executed']}/{record['code_cells']} code cells have execution counters; {record['outputs']} saved output blocks; {record['explanation_headings']} interpretation-related Markdown cells. Uncaught error types: {record['errors'] or 'none'}. Executed archive source equals current local code: {record['code_sha256']==loc['code_sha256']}. A mismatch is a provenance distinction, not evidence of failed results.",
        '\n**Cell map (zero-based):** '+ '; '.join(f"{c['index']}: "+(', '.join('`'+n+'`' for n in c['definitions'][:9]) or 'configuration/execution/export') for c in record['cells'])+'.',
        '\n**Notebook SHA256:** `'+record['sha256']+'`.']
 doc+=['\n## 4. Saved Drive archive inventory',
       '\nThis is an output-preservation inventory, not a claim that every stage succeeded. `Counter cells` counts execution metadata; some snapshots retain outputs after counters were reset. Late export snapshots can contain the completed preceding run but not their own export-cell output.',
       '\n| Saved Drive notebook | Counter cells | Output blocks | Uncaught errors |\n|---|---:|---:|---|']
 for p in sorted(paths):
  r=records[str(p)];doc.append(f"| `{p.relative_to(DRIVE)}` | {r['executed']}/{r['code_cells']} | {r['outputs']} | {', '.join(r['errors']) or 'none'} |")
 doc+=['\n## 5. What is already explained, what was corrected, and what not to claim',
       '\nExisting explanations are in the saved expanded/pilot/crossover/window notebooks, the local unified companion and status sections 3, 10 and 15–18. Some Drive text cells still say prepared/untested even though later outputs completed. Read the outputs and manifests before quoting those headings. This audit adds current technical interpretation alongside the source links; immutable executed notebooks are not rewritten.',
       '\n- The old v6 grid observes a reversal under legacy inputs; the new matched grid did not. They differ in wrapper wording, selected items, generation batch and label protocol. This is not an exact same-protocol replication or a contradiction to erase.',
       '- The 1,500-character guard window is verified directly in the saved v6 code. It is an additional historical limitation, not proof that it caused any result. The newer window study has no such hidden character slice. Do not treat this code difference as a new observed response-length finding.',
       '- A historical paired E/C net gap of 10/304 = 3.3 pp coexists with (31+21)/304 = 17.1% changed refusal labels. Counts come from jointly valid paired margins/discordances, not separate harm rates.',
       '- Original 48-answer labels are development material. A received LLM help; B is auxiliary GPT-6.1-Sol, user-confirmed, exact backend/settings unknown. Seven harm disputes remain unresolved. The new 64-unit human pass and delayed repeat are pending.',
       '- Broad text controls, framing, attachment effects and judge limitations have close prior work. See [the verified novelty register](NOVELTY_AUDIT_AND_PLAN.md#13-response-window-measurement-review--2026-10-20), including sections/method reading depth. A concrete paired consequence plus untouched validation is needed before a novel contribution claim.',
       '\n## 6. Professor-facing answers',
       '\n**What is the unit of analysis?** Historical item-condition responses, paired by item; GEE clusters repeated conditions by item. Scenario intervals aggregate within scenario. Window pairs share one generation; do not call them independent samples.',
       '\n**What is causal here?** Controlled input comparisons within a checkpoint, subject to serialization/content/measurement limitations. No internal mechanism is established by correlation, readback, interaction or steering alone.',
       '\n**What has actually been resolved?** Wrong-stimulus scoring, font treatment, exact cache/source identity, coverage and failure preservation, and evidence navigation. Label validity, scientific novelty and fresh generalization are not resolved by these fixes.',
       '\n**Which notebook should be run next?** None for generation. Finish the existing 64-unit private review and >=24-hour delayed repeat; analyze exact paired human/guard outcomes, then decide whether a new approved validation is justified.',
       '\n**Should we attach every notebook’s exploratory analysis?** Attach this source-and-cell walkthrough and the unified companion. Present one coherent design/result table, not a pooled average across notebook versions. Keep original archives available for questions; private replies/annotations must not be attached to a public presentation.']
 target=ROOT/'docs/TECHNICAL_NOTEBOOK_WALKTHROUGH.md';target.write_text('\n'.join(doc)+'\n')
 print('Inspected saved Drive notebooks:',len(paths),'local notebooks:',len(local),'technical document:',target)
 print('Private inspection manifest:',private)

if __name__=='__main__':build()
