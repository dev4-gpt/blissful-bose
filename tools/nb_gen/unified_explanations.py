"""Reviewed narrative for the aggregate-only project companion; not experiment code."""

INTRO = '''# VLM safety research: one end-to-end companion

**Evidence snapshot: 20 October 2026. All scientific outcomes remain exploratory. The original human review was assisted; new window human review is pending.**

This notebook brings the version history, code map, numeric evidence and claim limits together. It is a reading and reproduction companion, not a replacement for the archived experiments. Its executable cells read an embedded allowlisted snapshot of saved aggregates and draw a figure. They make **zero target-model or guard calls**, install nothing, mount no Drive, and require no secrets. A CPU runtime is sufficient.

**Reading order:** question → version history → how the code works → historical tables → supporting diagnostics → compatibility → two separate development pilots → prior art and claim decisions → provenance. Each logical result block is followed by an editable explanation. “Run all” here recalculates displays, not model answers. The original experiment notebooks and private archives stay unchanged.

The closest existing written synthesis is `docs/STATUS_AND_PAPER_PLAN.md`. `docs/INDEX.md` locates the rest. The handoff contains historical text and must be read with its update banner. This companion is a dated generated snapshot: regenerate it when source results or code change; it does not synchronize itself with Drive.
'''

QUESTION = '''## 1. What are we trying to establish?

If a model refuses a typed request but answers a picture, which change mattered? The words may have changed, the instruction may have become more forceful, the request may have been shortened, or merely attaching an image may affect behavior. The evaluator may also mislabel the answer.

Our original “see-saw” hypothesis predicted opposing text/vision safety changes. Limited exploratory observations did not support it; they do not rule out all trade-offs or establish a shared mechanism. The current question is **which apparent typographic safety differences survive matched inputs and trustworthy measurement?**

### Vocabulary used throughout

| Symbol | What the model receives | Limit of the comparison |
| --- | --- | --- |
| A | Language backbone, original text | Different model from the VLM |
| B | VLM, original question as text | Baseline, not necessarily wrapper-matched |
| C | Benchmark image/payload and its instruction | Can differ from B in content form and wording |
| E | Benchmark payload as text and corresponding instruction | B−E is not a pure wording effect |
| F_txt / F_img | Full question, plain instruction, text/image | Referent and input serialization differ |
| G_full / W2_img (v6) | Full question under legacy strong instructions | Text wrapper is benchmark-derived; not the new matched W2 pair |
| P_txt/P_img and S_txt/S_img | New full-question plain/steps pairs | Separate development study; do not pool with legacy W2 |
| Blank/noise/natural images | Text question plus an unrelated image | Presence diagnostic, not proof of meaningful image use |

**Refusal, harmful assistance and non-comprehension are separate measurements.** Refusal can coexist with harmful content. A harmless non-answer is not automatically a refusal. Reading in a separate transcription call does not prove comprehension during answering. Smoke success establishes execution, not safety or correctness.
'''

# version, notebook filename, result source, kind, question, change, limitation
VERSIONS = [
 ('v1','vlm_modality_tradeoff.ipynb','v1_full_n30/results.json','historical',
  'Is there a text–vision gap or see-saw?',
  'Backbone/VLM comparisons A–D, correlation and refusal-direction steering.',
  'Legacy judging and stimulus differences reduce trust. Folder n30 means per-scenario selection; read actual n from the result.'),
 ('v2','vlm_modality_tradeoff_v2.ipynb','v2_run/results.json','historical',
  'Does a text payload control change the interpretation?',
  'Adds E, benign controls, stricter legacy judging and steering controls.',
  'Legacy labels are not the later guard definition. Do not pool cached generations as independent replications.'),
 ('v3','vlm_modality_tradeoff_v3.ipynb','v3_final_four_judges/results.json','historical',
  'How much depends on judges, content and reading?',
  'Multiple guards, transcription, reference phrases and gap decomposition.',
  'Two rubric judges were invalid and retired. Decomposition shares depend on path/order; final selected pass is used, not a union of passes.'),
 ('v4','vlm_modality_tradeoff_v4.ipynb','v4_smoke_n16/results_v4.json','smoke',
  'Can a larger controlled design execute?',
  'Factorial wording/content/carrier design, LLaVA, harmfulness and benign XSTest.',
  'Only a pipeline smoke was completed. Its hypothesis flags and rates are not scientific evidence.'),
 ('v5','vlm_modality_tradeoff_v5.ipynb','v5_full/results_v5.json','historical',
  'Which candidate effects persist on a larger grid?',
  'Full controlled run, noun-phrase/bare controls, font arms, interactions and audit export.',
  'Neutral-image judging used the wrong stimulus; pixel upscaling undermined small-font interpretation. Those blocks do not support the intended claims.'),
 ('v6','vlm_modality_tradeoff_v6.ipynb','v6_full/results_v6.json','historical',
  'What survives stimulus-aware labels and better controls?',
  'Frozen NC rule, actual-stimulus guards, full-question grid, presence, true-size fonts, FigStep and batch checks.',
  'Main completed historical scientific evidence. No human reference or fresh confirmation; legacy imports lack exact modern revision attestations.'),
 ('v7','vlm_modality_tradeoff_v7.ipynb',None,'compatibility',
  'Can the approved wider panel and exact provenance pipeline work?',
  'Modular native adapters, pinned revisions, exact per-item caches, development/reserved separation and explanatory cells.',
  'Eight models attempted in benign tests; failures and partial checks remain. The full fresh scientific panel has not run.'),
 ('development','vlm_development_pilot.ipynb','v7_development_core8/pilot_summary.json','development',
  'Can a small scientific development pipeline complete end to end?',
  'Qwen2-VL-2B, eight seen items, B/E/C plus readback and two guards.',
  '32 target responses; not fresh. E/C labels agree within each guard; no evidence for hidden image-only harm. Original boundary equivalence verdict is not endorsed.'),
 ('crossover','vlm_crossover_development.ipynb','v7_crossover_core8/results_crossover.json','development',
  'Can wording reverse the carrier effect within Qwen2.5-VL-3B?',
  'Matched full-question 2×2 plus two blank controls/readback, raw versus adjusted labels, timing-only tier rule.',
  'Eight seen items. Both carrier effects positive, so the selected reversal was not observed. Original assisted human review and auxiliary LLM comparison completed; new window human review pending.'),
]

FLOW = '''## 3. How the code works, end to end

```text
Hypothesis + accepted settings
    → source identity / previously seen versus reserved split
    → render and freeze exactly what each condition shows
    → model processor and native chat template
    → exact-context generation cache → private model response
    → actual stimulus + response → each guard independently
    → raw refusal / harm / NC / readback / coverage
    → matched-item contrasts with declared denominators
    → numeric export + dated code/output notebook
    → reviewed plain-English interpretation → separate human reference
```

### Follow one item through the implementation

1. **Data:** early `load_split` reads benchmark pairs. V7 `mm_identity7/load_items7` checks pinned source questions and OCR; `historical_ids7/split_items7` separates seen development from fresh candidates. Fresh here means unseen by this project's analysis, not necessarily model pretraining.
2. **Condition:** v6 `add_spec/stimulus` binds the question, image, wrapper and judged stimulus. V7 `conditions7` supplies the grid; the crossover's `specs_cx` supplies only its seven approved arms. Rendering rejects clipping instead of silently editing the question.
3. **Inference:** early `VLM/LLM` classes and `run_pair` load sequentially. V7 `Model7.generate` applies the native template, preserves integer token IDs, checks image order and records token counts, timing and precision. This layer performs model calls; this companion never invokes it.
4. **Checkpoint:** old `run_cached` could import older outputs by tag and item list. V7 `cached7` validates the full context and value hash. A changed wrapper, revision, image or decoding cap is a different generation; a matching condition name is insufficient.
5. **Labels:** v6 `Qwen3GuardJ/WildGuardJ` and v7 `Guard7` score against what was shown. The frozen `nonanswer` rule changes the refusal construct. Crossover retains raw labels and treats controversial harm as unresolved. Guards are not human reviewers.
6. **Analysis:** v6 `contrast/gee_grid/holm` implement the historical analyses. `cross_version_table.py` translates version-specific numeric schemas. `vlm_saved_analysis.py` checks reconstructible refusal transitions; it cannot invent paired harm from margins. Crossover `summarize_cx` reports scheduled/valid counts and finite-sample missingness bounds, not a confirmation test.
7. **Save and review:** generators create the experiment notebooks. `CrossoverRun.export` verifies separate aggregates and notebook snapshots; later prose must follow those saved numbers. Failures remain outcomes of execution, not evidence of safety.

### Where the source lives

| Implementation | Files to read | Why these files matter |
| --- | --- | --- |
| v1–v5 | Named notebook's code cells, indexed below | Early self-contained implementations; never execute them just to read them |
| v6 | `tools/nb_gen/make_nb6_part1.py`, `make_nb6_part2.py`, `make_nb6.py` | Part 1 embeds data/models/specs/generation; part 2 labels/analyzes/exports; assembler reuses shared v5 cells |
| v7 | `tools/vlm7_core.py`, `tools/vlm7_models.py`, `tools/nb_gen/make_nb7.py` | Core, native adapters and notebook assembly are separate |
| Qwen2 pilot | `tools/nb_gen/make_development_pilot_nb.py` | Replaces the generic configuration/data/generation with a bounded subset |
| Crossover | `tools/vlm_crossover.py`, `tools/nb_gen/make_crossover_nb.py` | Seven-arm selection, finite deadline, target/guard passes, timing tier and snapshots |
| Unified companion | `tools/nb_gen/make_unified_nb.py`, `unified_explanations.py` | Allowlisted aggregate extraction and reviewed explanations; no generation |

Notebook cell numbers below are **zero-based source cell indexes**, not execution counters such as `[8]`. Definition inventories show where code lives, not proof that its function ran. Static changes are syntax comparisons; only reviewed narratives explain scientific consequences. Local source hashes identify this checkout, not necessarily the code used in an earlier Drive execution.
'''

HISTORICAL_REVIEW = '''### What the historical tables mean — editable review

Read **within each version, checkpoint, benchmark and judge**. Different labels, questions, preprocessing and cached generations prevent a pooled “all versions” safety rate. V1/v2 legacy scores remain historical, not validated measurements. V4 smoke stays out of the scientific comparison table.

The matched E control substantially changes the apparent Qwen gap. B−E also changes content form, so it cannot isolate wording alone. LLaVA's image-presence behavior differs from the Qwens; do not present one shared explanation. Compare harmful assistance alongside refusal, separately for both guards. Historical `n` records item counts and is not always a verified valid-label denominator.

FigStep is a separate benchmark and its text-equivalent control already exists in prior work. A negative text/image difference or opposite guard direction must remain visible. Correlation and steering observations do not establish a universal shared mechanism or rule out every see-saw.
'''

DEVELOPMENT_REVIEW = '''### What the two development studies mean — editable review

The Qwen2 B/E/C pilot and Qwen2.5 matched full-question crossover answer different questions on separately selected seen items. **Do not pool them or call one an independent confirmation of the other.** The Qwen2 pilot has identical E/C labels within each guard; it provides no positive evidence for hidden image-only harmfulness.

In the completed crossover both guards give plain refusal 4/8 text versus 5/8 image, and steps refusal 5/8 versus 8/8. The image-minus-text effects are +12.5 and +37.5 percentage points. A +25-point interaction is not the required sign reversal. The crossover was not observed in this sample, without proving it impossible elsewhere. Blank controls match text-only labels; readbacks match 8/8. There are 17 capped answering responses, and the completed window run retained all automated labels; new human review is pending.

The second balanced block did not run: representative cap-length coverage failed its timing-only gate. Do not extend after seeing results. Complete execution is different from validated science. The current notebook and dated snapshots already live on college Drive; this companion embeds only numeric aggregates.
'''

CLAIMS = '''## 8. Prior art, our observations, and what remains unproved

| Topic | Prior work / status | What we may honestly say |
| --- | --- | --- |
| All-text typographic control | [FigStep v3 §6.4](https://arxiv.org/html/2311.05608v3#S6.SS4) | Our controls are replication/adaptation, not an invention |
| Framing, carriers, comprehension | [MMJailBench v1 §§3–5](https://arxiv.org/html/2608.25490v1) | Very close factorial comparator; exact joint overlap must still be checked before novelty claims |
| Human text equivalents and evaluation | [MSTS v1 §§3.4, 4.5–4.6](https://arxiv.org/html/2501.10057v1) | Human validation and equivalent prompts are known methods |
| Image attachment and checkpoint-specific directions | [The Uncontrolled Variable v2 §§2–4/S27–S29](https://arxiv.org/html/2609.26174v2) | Presence itself is not our standalone contribution |
| Within-checkpoint wording reversal | Motivated by v6; matched eight-item follow-up completed | Selected crossover not observed in new development sample; exact legacy wording and population differ |
| Hidden image-only harmful responses despite matched means | Paired-error principle is known; our first pilot provides no positive observation | Requires verified paired harm and practical consequences; no text-replacement claim |
| Consequential human measurement correction | Not measured here | Possible paper direction only if human evidence materially changes a conclusion |
| Output-window sensitivity | Completed: 32 generations, 128 guard evaluations; no automated label changes | Eight full cap hits and pending human review leave the broader conclusion unresolved |
| Held-out text-twin prediction / full modern panel | Planned, not completed scientific evaluation | No demonstrated predictor, efficiency gain or eight-model safety conclusion |

The literature register in `docs/NOVELTY_AUDIT_AND_PLAN.md` records versions, sections and reading depth. It is a scoped review, not proof of novelty from unsuccessful searches. A publishable paper still needs a consequential bounded result, human reference, fresh replication where claimed, and a comparison with the closest prior work. Refuted and inconclusive outcomes belong in the paper too.
'''

TOOLS = '''## 9. Tools that help maintain this knowledge

| Tool / connector | Useful role | What it cannot establish |
| --- | --- | --- |
| [Jupyter Book](https://github.com/jupyter-book/jupyter-book) | Turn notebooks/Markdown into a navigable research book with citations and cross-references | Does not decide whether results are scientifically valid; no site was published here |
| [Jupytext](https://github.com/jupytext/jupytext) | Pair notebook inputs with reviewable Python/Markdown files | Text pairing does not preserve outputs by itself; keep executed notebook archives |
| [nbdime](https://github.com/jupyter/nbdime) | Notebook-aware code/output diffs and merges across versions | A code diff does not establish independent replication |
| `code-documentation-code-explain` skill | Explain purpose, flow, functions and edge cases using the actual source | Explanations need result provenance and scientific review |
| Google Drive connector / college Chrome | Locate executed notebooks and archives in the correct account | Connector and browser may use different accounts; verify identity before uploading |
| GitHub connector or local Git | Browse tracked source/history and compare changes | Local edits are not necessarily pushed; no push, sharing or plugin install is performed here |

This project already generates notebooks from Python. Keep that workflow rather than introduce competing sources of truth now. Jupyter Book is a useful later presentation layer; nbdime can improve comparisons without changing experiments. No new package, plugin, paid service or external knowledge store is required to use this companion.
'''
