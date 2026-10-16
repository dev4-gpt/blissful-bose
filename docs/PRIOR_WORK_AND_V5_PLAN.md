# Prior work, positioning and the v5 plan (toward a publishable paper)

**Date:** 2026-10-15 · Sources: five parallel literature agents (notes in `research_notes/Prior work limits and v4 design/`), our v3 exploratory results (`V3_RESULTS_AND_NEXT_STEPS.md`) and the pre-specified plan. **Reading guide:** the agents read mostly abstracts and search snippets through a small summarising model, so every number and arXiv ID below is *second-hand* until someone checks the PDF. Nothing here should be quoted in a paper before that check.

## 1. What the paper is now

Working claim: **in small open VLMs, most of the refusal drop on typographic (text-in-image) harmful requests is a prompt-wrapper and content effect, not an image-modality effect; reading the image is not the bottleneck; the residual image effect is model-dependent and small.** The see-saw framing (vision drops by Z, text rises by Z) is not supported: text and image refusal move together.

This is a measurement paper. It is publishable if (a) the factorial controls hold, (b) the judge validity is shown with a stratified human audit, and (c) it holds on a non-Qwen model. A workshop version is realistic by 20 Nov; ARR Jan 4, 2027 (ACL 2027) needs the confirmatory run.

## 2. What prior work did and where it stops (second-hand)

| Area | Closest work | What it does | Limit that matters to us |
|---|---|---|---|
| Rendered text vs text, framing crossed | **MMJailBench 2608.25490** (Aug 2026) | Crosses prompt framing with text vs rendered-text carrier over 16 models; framing dominates (> 40 points), rendered text not stronger than direct text | Jailbreak-style framings, not a benign procedural wrapper; no sub-3B or LLaVA-1.5; PDF unread (abstract only) |
| Same neutral template, OCR explanation | 2608.30750 (EMNLP 2026) | Uses a neutral "image shows an activity" template and attributes refusal on rendered text to OCR | No plain-text arm |
| Text vs typographic attack | 2604.12371, 2511.08367 | Compare text and typographic attacks; gap is model-dependent (GPT-4o large, Qwen3-VL-4B small) | Prompts not matched across arms |
| Blank / irrelevant image changes refusal | **2609.26174** (partial overlap) | Even a blank image changes refusal (benign borderline refused more, harmful attacked less) | No typographic payload, no comprehension gate, no decomposition |
| Image-property dissection | **2610.07009** (4 Oct 2026) | Controlled dissection of image properties in jailbreaks | Close; full read needed |
| Benchmarks that change wrapper and modality together | MM-SafetyBench 2311.17600, FigStep 2311.05608, HADES, MemeSafetyBench, Lingua-SafetyBench 2601.22737, VLSBench 2411.19939 | Typographic or meme attacks vs text or no-image arms | Wrapper and modality confounded; no read-back; VLSBench says typographic sets leak harm into the text query |
| Comprehension vs safety | MSTS 2501.10057, Azulay et al. | Some VLMs look safe only by misunderstanding | No per-item read-back conditioning on small open VLMs |
| Wording shifts refusal | SORRY-Bench 2406.14598, "Mood Matters" 2608.05409 | Phrasing and grammatical form shift text-only refusal | Text-only; no modality factor |
| Trade-offs / transfer | 2406.02575, TGA 2410.12662, 2608.30750 | Text safety transfers to images; an image can lower text refusal (one model: 90.7 -> 76.9, snippet) | No zero-sum see-saw test anywhere (agent search) |
| Judges | StrongREJECT 2402.10260, Coin Flip 2603.06594, Know Thy Judge 2503.04474, WildGuard 2406.18495, Qwen3Guard | Refusal/harm judging, reliability varies with victim-model style | Guards are text-only and unvalidated on small-VLM replies; Qwen3Guard's "Refusal" field is undefined on its card |
| Over-refusal | XSTest 2308.01263, MOSSBench 2406.17806, DUAL-Bench 2510.10846 | Over-refusal sets, some native multimodal | No typed-image XSTest found |

**Novelty, stated honestly (to our knowledge, negative-search evidence only):** no paper found runs a wrapper x content x modality factorial with per-item read-back, a prompt-matched control, a 2-3B open model and item-level text-image coupling. MMJailBench is the paper a reviewer will say we must beat or complement; our difference is the benign wrapper, read-back, sub-4B and non-Qwen models, harmfulness labels and paired item-level tests. Avoid "first" and "novel decomposition".

## 3. What reviewers will attack, and how v4/v5 answer it

| Attack (from the agents) | Answer in v5 |
|---|---|
| "P bundles wrapper, content and question form" | v4 separates wrapper (B vs G_full) from content (G_full vs E); v5 adds a noun-phrase paraphrase (`NP_*`) and a bare phrase (`Bare`) |
| "Image effect may be legibility, not modality" | `R_big` / `R_small`: our own rendering at 38 px and 18 px, read-back for each; font-size contrast (H18) |
| "Wrapper may interact with modality" | (E - C) - (N - C_neutral), all items and read-correctly items (H17) |
| "Refusal is not harm" | Qwen3Guard / WildGuard harm labels, Controversial counted strict and loose (H14, H20) |
| "Two Qwen models" | LLaVA-1.5-7B (non-Qwen, 4-bit, 152 items); still thin: say "differs by model" rather than a size law |
| "Judge story is a straw man" | Report the failed LLM-rubric judges as a documented negative result; two independent guards plus keyword |
| "Single labeller, author as annotator, thin cells, post-hoc threshold" | Stratified audit (>= 10 rows per model-condition cell), rubric fixed in `audit_v5_RUBRIC.md`, 60-row retest, 50-row second-annotator subset if a person exists; report percent agreement and AC1/PABAK with CIs; name it a "single-annotator reference" |
| "8 clusters make the bootstrap unreliable" | Primary statistics: exact item-level McNemar with Holm, scenario-level t(7) interval and sign test; bootstrap secondary |
| "No over-refusal evidence" | XSTest safe prompts as text and typed images (v4 loads the open CSV) |
| "Items reused from MM-SafetyBench" | Say so; the confirmatory run uses >= 100 items per scenario where data allow |

Remaining confounds to state: a bare phrase is out of context (may be read as a topic); length and token position differ between text and image inputs; reading the text is not the same as understanding the intent; "perform this activity" implies harm even under a neutral wrapper; judge bias on short replies.

## 4. OpenResearch decision

From the OpenResearch agent (repo read as text, nothing installed): Colab is not a backend (local, SSH, Slurm, Kubernetes, Modal, Tinker, Ray, HF Jobs, managed RunPod/Lambda); it logs only experiments it launches itself and no results-import route was found; official builds send opt-out telemetry to `api.openresearch.sh`; the installer fetches from GitHub releases, checks a SHA-256 that it skips if `sha256sum` is missing (likely on macOS), and edits your shell rc; the project is days-to-weeks old with open issues about the installer and data. **Decision: do not adopt OpenResearch now.** Use the read-only alphaXiv MCP for literature and a plain `runs.jsonl` ledger (or our `results_v*.json` plus git). Revisit only if the work moves to Hugging Face Jobs or Modal. Adding the alphaXiv MCP, any OAuth or API key, and any install is for you to approve.

## 5. v5 and the path to submission

1. **Finish v4 smoke** (running); fix anything it shows. Then run **v5 SMOKE=True** (about 20-25 min), then v5 full. v5 is a superset of v4, so the v4 full run is skipped; v3/v4 caches are reused. Models download to the Colab VM's local disk (not Drive), which is about 78 GB on a T4: v5 deletes each model's cache after use (`purge_hf_cache`) so the full run, with LLaVA and Vicuna added, does not fill the disk.
2. **Hand-label** `audit_v5_blinded.csv` (240 rows) with the fixed rubric; retest 60 rows after one day; ask one other person for the 50-row subset. Pass the judge gate (plan section 3) before any confirmatory claim.
3. **Read the two near papers in full** (2610.07009, 2609.26174), then MMJailBench; verify every second-hand figure above against the PDF.
4. **Confirmatory run**: >= 100 items per scenario, >= 3 model families, one run, thresholds unchanged.
5. **Write** (4-page workshop version first): the factorial figure, the read-back table, the judge negative result, strict/loose harm, over-refusal, limitations (Qwen-heavy, small judges, single annotator, typographic only, English only, refusal is not harm) and the ethics items (no prompts or images released, annotator exposure statement, licences, AI-assistance disclosure).
6. **Re-search** arXiv for October 2026 onward just before submission (typographic, read-back, wrapper, misunderstanding, small VLM).

| Dates | Work |
|---|---|
| Oct 16-20 | v4 smoke fixes; v5 smoke and full run |
| Oct 21-Nov 5 | Hand-label, retest (after 1 day), judge gate; read near papers |
| By Nov 20 | Workshop draft (4 pages) if the gate passes |
| Nov 21-Dec 20 | Confirmatory run, full draft |
| Jan 4, 2027 | ARR submission (ACL 2027) or TMLR |

## 6. Housekeeping

The v1 result folders already in the public repo contain raw model replies (`gen_*.jsonl`); decide whether to remove them (history rewrite needs your explicit approval). Keep every `audit_*` file and raw-generation file out of git.
