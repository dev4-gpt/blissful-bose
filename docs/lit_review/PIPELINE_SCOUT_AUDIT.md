# ResearchingOS Scout — Audit on This Topic (2026-09-25)

**What was run.** Only the pipeline's **discovery stage**: `AcademicSearchService.run_combined_search`
(`ResearchingOS/backend/services/search.py`), 12 queries, `limit=8` each, no LLM involved. Raw output:
`scout_raw.json`. **Not run:** the 7-agent council, `feynman lit`, the drafting graph. Reasons:
(a) `feynman lit` only summarises papers *already in the vault* — it does no discovery;
(b) the council/drafting path needs LLM keys and contains a `generate_rich_fallback_section` fallback,
and the repo's own `HANDOFF.md` records that this pipeline previously produced fabricated citations and
numbers. I wanted a test whose every output can be checked by eye. Running the writing stage is a
reasonable follow-up **after** the discovery stage is fixed — say if you want it.

**Ground truth used.** My arXiv-verified set of 47 papers (`arxiv_verified.json`). It is *not* an
objective ground truth: I built it from my own searches, so it under-counts what the Scout got right
outside it (see "What the Scout got right").

## Results

| Metric | Value |
|---|---|
| Queries / results per query | 12 / 8 |
| Unique results | 85 |
| Of my 47 verified papers, surfaced by Scout | **9 (19%)** |
| Results I judge strongly on-topic | 13 (15%) |
| Results adjacent (background / method-adjacent) | ~6 |
| Results irrelevant to safety/VLM/continual learning | ~66 (≈78%) |
| Results with empty abstract | 32 / 85 (38%) |

Relevance labels are my manual judgment from titles; the 15% figure could move a few points either
way but not to a different conclusion.

### Not found at all
The Scout **never returned Bach et al. (2604.17215)** — the seed paper the whole project extends — nor
any of: VLGuard, MM-SafetyBench, FigStep, JailBreakV, Liu et al. (2405.13581), VLMGuard-R1, SafeAnchor,
DataShield, SQSD, Bi-Anchoring, GradSafe, Gulati & Raval, OGPSA, Unforgotten Safety, HarmBench, XSTest.
That is 38 of 47.

### What the Scout got right (the 9 overlap + 4 extras)
Overlap with my set: Qi et al. (2310.03693), CMRM (2410.09047), Continual Instruction Tuning for LMMs
(2311.16206), Model Merging & Safety (2406.14563), SafeMERGE (2503.17239), Why guardrails collapse
(2506.05346), AsFT (2506.08473), Few-Tokens (2603.07445), Audio-LLM benign FT (2604.16659).

**Four on-topic hits I did not have** — genuine additions, *not yet verified by me*:
- "Targeted Vaccine: Safety Alignment for LLMs against Harmful Fine-Tuning via Layer-wise Perturbation" (Crossref 10.1109/tifs.2025.3615412) — check the DOI resolves to the journal article; the record's `/mm1` suffix suggests a supplementary-material DOI rather than the paper itself.
- "EVA: Editing for Versatile Alignment Against Jailbreaks" (PubMed 42154710).
- "Visual Adversarial Examples Jailbreak Aligned Large Language Models" (OpenAlex W4393157467).
- "BlueSuffix: Reinforced Blue Teaming for VLMs Against Jailbreak Attacks" (arXiv 2410.20971).

So the pipeline is not useless: it has some real signal. It is unreliable as a *sole* source.

## Defects observed (with evidence)

| # | Defect | Evidence | Severity |
|---|---|---|---|
| 1 | **Failures are silent to the caller.** Semantic Scholar returned HTTP 429 on 11/12 queries; DBLP failed on 12/12 (JSON parse error, timeouts, connection resets); GitHub 403 twice; PubMed 429 once. These appear only in stderr; the returned list carries no marker that a source was down. | `scout_log.txt` | **High** — a run with 2 of the 3 CS-relevant indexes dead looks identical to a healthy run |
| 2 | **Domain mismatch.** ~half of hits come from biomedical/general indexes (EuropePMC, PubMed, PLOS, DOAJ, HAL, Crossref-SSRN) for an ML-safety topic: heart-failure decision support, elevator fault diagnosis, smart grids, underground stope mechanics, debris-flow knowledge graphs, Thai sign language. | result list | High |
| 3 | **RRF favours generic, high-citation papers.** "Training language models to follow instructions with human feedback" appears in the top 8 for 4 different queries; "A Survey of Large Language Models" for 3. | result list | Medium |
| 4 | **Query→topic drift on keyword overlap.** "safety basin fine-tuning LLM" returned "Fine-Tuning Human for LLM Projects" and "Optimizing LLM x86 Assembly Code Comprehension through Fine-Tuning". | result list | Medium |
| 5 | **Empty abstracts on 38% of results**, so downstream relevance triage / analyst steps have nothing to read for them. | `abstract` field length | Medium |
| 6 | **No recency/category control.** 2026 papers dominate raw counts (38/85) but many are off-domain; no `cs.CL/cs.CV/cs.CR` filter is applied to arXiv queries. | year histogram | Medium |
| 7 | **Date formats are inconsistent** (`2026-3-31`, `2026 Oct`, `2026`, empty) — will break any recency sort. | `published` field | Low |

Noted but not investigated: the pipeline has a `citation_relevance.py` (IDF-weighted relevance
triage per HANDOFF.md). It evidently is not applied inside `run_combined_search` — that is a strong
candidate for the first fix.

## Suggested fixes, in priority order
1. Make `run_combined_search` **return per-source status** (ok / rate-limited / error) and fail loudly, or warn in the output header, when a CS-relevant source is down.
2. **arXiv-first for CS topics**: restrict to `cs.CL, cs.CV, cs.LG, cs.CR, cs.AI`; query arXiv with title/abstract fields; then backfill with OpenAlex. De-prioritise biomedical indexes unless the topic is medical.
3. Add **backoff + API key** for Semantic Scholar; replace or repair the DBLP client.
4. Apply `citation_relevance.py` as a **post-filter**, and drop results with empty abstracts from the ranking unless they match on title.
5. **Seed-paper expansion:** given the anchor paper (here 2604.17215), pull its reference list and its citing papers (Semantic Scholar/OpenAlex "cited by") — that alone would have surfaced most of the data-selection cluster.
6. Normalise `published` to ISO-8601 at ingest.

## Comparison in one paragraph
For this topic the Claude-run search plus arXiv verification produced a checked, structured picture
(47 papers, including the closest competitors and three corrections to existing repo docs); the
Scout run produced 85 unique hits of which ~13 are on-topic, missed the seed paper, and hid its own
source failures. It is a usable *recall supplement*, not yet a *primary* literature tool. The
right next experiment is to re-run the same 12 queries after fixes 1–3 and compare recall against
the same 47-paper set — that gives you a concrete before/after number for the pipeline.

## Reproduce
```
cd ~/Developer/ResearchingOS/backend
.venv/bin/python scout_run.py out.json   # 12 queries; script copied alongside as scout_run.py
```
Queries used: continual safety alignment fine-tuning · safety alignment degradation vision-language
models fine-tuning · safety alignment vision language models · gradient-based data selection safety
fine-tuning · benign fine-tuning compromises safety alignment · catastrophic forgetting safety
vision-language models continual learning · multimodal jailbreak benchmark vision language model ·
safety basin fine-tuning LLM · LoRA safety subspace preserving alignment during fine-tuning ·
over-refusal vision language models safety · model merging safety alignment restoration ·
continual instruction tuning multimodal large language models
