# ResearchingOS Council Stage — Audit on This Topic (2026-09-25, updated 2026-09-27)

## 2026-09-27 update: fixes 1–3 implemented and re-run

Fixes 1–3 from below (stop truncating agent turns, feed real source text via an anchor-paper
mechanism, add a relevance gate before ingestion) are implemented in `backend/agents/council.py`,
plus the "Durable Harness Memory Refinement" prompt-label leak (F7). All 28 `tests/test_council.py`
cases and the full 269-test backend suite still pass. Diff: `council_py_after_fixes.py` in this
folder is the patched file; `git diff --stat` reports 177 insertions / 52 deletions in that one file.

**Re-run, same topic, `anchor_arxiv_ids=["2604.17215"]` (Bach et al.), `max_papers=12`, live mode.**
Evidence: `council_debate_output_v2_fixed.md`, `council_logs_v2_fixed.json`. A first attempt at this
re-run (not saved) surfaced a second, narrower bug: the anchor's own full-text budget widened the
*saved note* correctly, but `summaries_text` — what the critique agents actually read — still cut the
anchor's content at 20,000 characters, which lands before this ~5,000-word paper's own conclusion.
That bug is fixed too (a dedicated head-excerpt + tail-before-"References" excerpt, so the paper's
last paragraph reaches the critique prompt regardless of length) and confirmed by direct inspection of
the fetched text before re-running. The results below are from the second, corrected re-run.

**F3 (strawman), retested — fixed.** The Chairman's consensus section now reads: *"The paper itself
reports a '51% computational overhead.'"* The Statistician and Reviewer #2 each engage with that
number directly (e.g. Reviewer #2: *"the 51% overhead figure may be an upper bound rather than a
typical operating point"*). Nobody attributes an invented "gradients are cheap" claim to the Engineer.

**F1 (off-topic corpus), retested — improved, not solved.** The relevance gate is live and logs its
own effect (`"Relevance gate: kept 10 paper(s)... dropped 4 with none, excluded 1 GitHub repository
entry"` on this run). It reliably removes zero-overlap junk and GitHub "Repository:" rows. It does
**not** catch domain-crossing false positives that share generic vocabulary with the topic: this run
still ingested "Maternal knowledge and practice of safe infant sleep position in South Ethiopia",
"Exploring collaborative strategies to improve patient safety in healthcare organizations", and an
antiarrhythmic-drug-therapy paper — each matched on words like "safety" or "selection" alone. A lexical
overlap gate was always going to be a partial fix (see the "Fixes" list below, which already scoped it
as a pre-filter); the domain/category-aware retrieval fix (Scout audit fix #2, arXiv-category-first)
is still the real fix for this half of F1.

**F2 (seed paper starved), retested — fixed**, once the second bug above was also fixed: the anchor
note is 40KB (was 3.6KB) and both the note and the critique prompt now carry the paper's own
"51% computational overhead" sentence.

**F4 (method misdescribed), retested — no recurrence.** The Engineer's audit is now grounded in actual
reasoning about the real method (per-sample gradient-norm cost, median-based filtering), not an
invented Hessian/replay-buffer mechanism.

**F5 (citations), retested — partially outstanding.** No fake author names or GitHub-username-as-author
this run. **Not fixed:** citations are still inline `arxiv:2604.17215`-style keys, not the project's
own `[[wikilink]]` format (`AGENTS.md`'s own citation policy) — zero wikilinks in the output, same as
before. This was not in the scope of fixes 1–3 and remains open (see "Fixes" item 5 below).

**F6 (truncated cross-talk), retested — fixed.** Debate turns are no longer cut to 300–400 characters
before being handed to the next agent; the transcript shows full, mutually-responsive critiques (e.g.
Reviewer #2 quoting and individually rebutting four separate Engineer claims with specific numbers).

**F7 (prompt-label leak), retested — fixed.** No "Durable Harness Memory Refinement" or similar
internal label appears anywhere in this run's output.

**One claim in this run that needs independent checking, not model-trust:** the Statistician asserts
Bach et al. report "only single-point estimates" with "no confidence intervals... no hypothesis
tests... no p-values." This is now at least a checkable claim about the real paper (not a strawman),
but it was not verified against the paper's actual tables/appendix in this session — do that before
repeating it in the manuscript.

**Still open / out of scope for fixes 1–3:** wikilink citation enforcement (F5), and the relevance
gate's blindness to domain-crossing false positives (F1). Both were flagged as separate, lower-priority
items in the original "Fixes" list below and were not requested this round.

---

# Original audit (2026-09-25)

**Bottom line.** The council ran end-to-end and produced a well-formatted, confident, *unusable*
synthesis. Its problems are structural and traceable to specific lines in `agents/council.py`, not
random model noise. **Do not use the debate output as a literature review or as a source of claims for
the paper.** The council stage is not ready to be trusted on this project until the fixes below are made.

## What was run
`CouncilOrchestrator.run_debate_only` (Stages 1–4: discovery → ingestion → 3-agent critique → debate →
Chairman synthesis; by construction it never writes a manuscript to `04_Drafts`).

- **Topic:** "Continual safety alignment of vision-language models via gradient-based sample selection"
- **Mode:** `RESEARCHINGOS_RUN_MODE=live` (forced, so it could not silently fall back to the canned
  mock papers). Manifest confirms `"synthetic": false`.
- **Isolation:** scratch vault + scratch memory file; nothing was written to the real ResearchingOS vault.
- **Cap:** 12 papers. **Wall time:** 410 s. Providers as configured in `.env`
  (Gemini is the default provider and was used for query extraction and the logged agent calls).
- Not run: Stage 5+ (drafting), meta-review council, LaTeX export.
- Evidence: `council_debate_output.md`, `council_logs.json`, `run_council.py`.

## Findings

### F1. Ingested corpus is ~92% off-topic (1 of 12 directly relevant)
| Verdict | Papers |
|---|---|
| **On-topic** (1) | Bach et al., *Continual Safety Alignment via Gradient-Based Sample Selection* (arXiv 2604.17215) |
| Adjacent, VLM continual learning but no safety (3) | MoE Adapters for VLM CL (openalex W4402702936); IAP: Instance-Aware Prompting (europepmc 41525545); `Thunderbeee/ZSCL` GitHub repo |
| **Off-topic** (8) | "AI Safety is Stuck in Technical Terms" (governance); "Trustworthy Agentic AI" PRISMA review; `HimJoe/Governance--and-Security-by-Design…` GitHub repo; Friedman's *Greedy function approximation* (gradient boosting); "AI: Multidisciplinary perspectives…"; IoT intrusion sequential-submodular selection; Adversarial ML in Industrial IoT; EgoMotion (egocentric motion generation) |

Same root cause as the Scout audit: keyword-overlap retrieval across biomedical/general indexes with
no relevance gate. **None of the closest competitors was ingested** (LARF, DataShield, SQSD,
Bi-Anchoring, SafeAnchor, VLGuard, Gulati & Raval, …). Positive note: this time Gemini-extracted
sub-queries *did* surface the seed paper, which the raw 12-query Scout test missed — LLM query
expansion helps, but it is non-deterministic and the surrounding noise is unchanged.

### F2. The seed paper is ingested as a 3.6 KB note with none of its key numbers
`01_Papers/arxiv_2604.17215.md` contains no mention of the headline ASR results, the selection
ratio, or the paper's own stated ~51% compute overhead (the string search for `51`, `10.2`, `36.7`,
`overhead` returns nothing). Cause: content is cut to 1,500 characters before critique
(`council.py:394` full text capped at 12,000 chars, `:425` note snippet `[:1500]`, `:481`
`abstract…[:1500]` in `summaries_text`). The limitation appears in the paper's appendix, far beyond
that cut. **The council was therefore critiquing the abstract, not the paper** — and then criticising
it for things the paper states.

### F3. The debate criticises claims nobody made (verified strawman)
- The debate keeps only 400 characters of the Engineer's critique (`council.py:529`,
  `critiques["Engineer"][:400] + "..."`). In this run those 400 characters are the preamble and one
  heading for a *single, non-safety paper* (the MoE-adapter paper). The word "cheap" appears **zero
  times** in the Engineer's turn.
- The Statistician's reply (`:545`) nonetheless lists as an "Engineering Claim": *"Gradient-based sample
  selection is cheap because gradients are already computed during back-prop."* Nobody said this.
- The Chairman (`:570`) then reports as consensus that "the initial assumption of 'cheapness' was
  thoroughly debunked" and that there is "unanimous consensus" on cost being a bottleneck.
- Reality: Bach et al. state the overhead themselves (~51%, in their limitations). The council "found"
  a flaw the authors already disclosed, because the disclosure was truncated away (F2).

### F4. The method is misdescribed
The debate assumes the method stores "Hessian approximations" and "a buffer of high-gradient samples
that must be retained for replay". Bach et al.'s method uses per-sample gradient norms to *filter*
training data; it has no Hessian and no replay buffer. The critique is of a different (invented) method.

### F5. Citations in the outline do not resolve to sources
- **Zero** `[[wikilinks]]` in the whole output, contradicting the project's own rule in `AGENTS.md`
  ("all inline citations must be wikilinks matching `vault/01_Papers/`").
- "Amr et al., 2026" = the IoT intrusion-detection paper, cited as a "connection" for gradient-based
  selection in VLM safety — irrelevant.
- "HimJoe, 2025" and "Garike, 2026" cited as authors: `HimJoe` is a GitHub username for a repo, not an
  author of a paper.
- "GEM, EWC, TRADES, Focal Loss" appear as prior art but are **not in the ingested vault** — drawn
  from model memory, presented alongside vault citations with no distinction.
- Technical slip: "ViT-L/2" (no such standard model; ViT-L/16 or /14 are).

### F6. Agents speak from truncated views of each other
`:529/:545/:561` cut each turn to 400 characters for logging; `:550-551` feed Reviewer #2 only 300-char
snippets of the Engineer and Statistician. The transcript file itself contains visibly cut sentences
("…for Vision-Language..."). The Chairman's "synthesis" is a synthesis of these fragments.

### F7. Output is generic, and one prompt artifact leaks
The 8-section outline ("Critical Review of Gradient-Based Sample Selection and Future Research
Directions") would fit almost any gradient-selection topic. A heading reads "Structural Outline for
Publication: **Durable Harness Memory Refinement**" — harness/memory prompt text leaking into user-facing
output. The Chairman's own wording ("unassailable framework") is promotional.

### What is fine
Live mode works and did not mock; the provenance ledger recorded 12 sources and 12 dossiers; the
persona prompts and 3-critic fan-out run in parallel; the run is fast (410 s). The stage is a sound
skeleton whose inputs are being starved and truncated.

## Consequence for the paper
Nothing from this debate should enter the paper. Specifically, do **not** adopt its claims that
(a) selection cost was overlooked, (b) the field lacks VLM safety metrics, or (c) the novelty is
undermined by GEM/EWC/TRADES — (a) is false against the paper's own text, (b) is unsupported by the
vault content it read, (c) is unsourced. The literature review in `LITERATURE_REVIEW_CLAUDE.md` remains
the reference for prior art and risks.

## Fixes, in priority order (all in `backend/agents/council.py` unless noted)
1. **Stop truncating agent turns.** Pass full critiques into the debate and to the Chairman; keep
   truncation only for log display. (`:529, :545, :550-551, :561`)
2. **Feed real source text.** Replace `[:1500]` excerpts with section-aware chunks (abstract + method
   + limitations/appendix), especially for an *anchor paper*. (`:394, :425, :481`) Add an explicit
   `anchor_papers` input whose full text every agent receives.
3. **Relevance gate before ingestion.** Score papers against the topic (the repo already has
   `services/citation_relevance.py`) and drop those below threshold; refuse to ingest GitHub repos as
   "papers". This alone removes 8 of the 12 off-topic items here.
4. **Attribute claims only to what was said.** Have the Statistician/Reviewer quote the exact
   Engineer sentence they rebut, and have the Chairman list consensus only where ≥2 agents make the
   *same* claim in their own critique text.
5. **Enforce citation policy in the output.** Post-check that every author-year citation maps to a
   `vault/01_Papers` file via `[[wikilink]]`; flag anything else as "from model memory".
6. **Fix the Scout first** (see `PIPELINE_SCOUT_AUDIT.md`): the council's quality is capped by what it
   ingests.
7. Remove the leaked "Durable Harness Memory Refinement" heading from the Chairman prompt template.

Suggested re-test after fixes 1–3: same topic, same cap, with `arXiv:2604.17215` supplied as the anchor
paper; then check (i) fraction on-topic ingested, (ii) whether ~51% overhead is acknowledged as the
authors' own limitation, (iii) zero unresolved citations.

## Reproduce
```
cd ~/Developer/ResearchingOS/backend
.venv/bin/python -u run_council.py <out_dir> "<topic>" 12   # run_council.py is copied alongside; it sets RESEARCHINGOS_RUN_MODE=live itself
```
`run_council.py` instantiates `CouncilOrchestrator(vault_path=<out_dir>/vault,
memory_file_path=<out_dir>/memory.json)` and calls `run_debate_only`.
