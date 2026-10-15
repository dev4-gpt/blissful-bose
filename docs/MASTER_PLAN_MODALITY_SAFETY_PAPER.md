# Master Plan: From Pilot Results to a First Paper

**Date:** 2026-10-14 · Author: Aryaman Singh Dev · Advisor: Prof. Thao Minh Le (PSU)
**Inputs:** `bundle (1)/` (full run), `bundle/` (smoke run), three agent reports (literature, audit, venues), `PLAN_MODALITY_SAFETY_TRADEOFF.md`, `PAPER_ROADMAP_MODALITY_SAFETY.md`.
**Rule for this document:** everything is labelled **verified** (I checked it), **agent-reported** (a subagent opened the source; I have not), or **unverified**.

## 1. What we have

- **Experiment:** frozen open models, no training. MM-SafetyBench, 8 harmful scenarios x 30 items = 240 items per condition. Conditions: A LLM-backbone text, B VLM text, C VLM typographic image + generic prompt, D VLM text + blank image. Judge: Qwen2.5-3B-Instruct. Steering: text-derived difference-of-means refusal direction, Qwen2-VL-2B only.
- **Two model pairs:** Qwen2-VL-2B (vs Qwen2-1.5B-Instruct) and Qwen2.5-VL-3B (vs Qwen2.5-3B-Instruct).
- **Reported numbers (judge as run):**

| Refusal rate | A text LLM | B text VLM | C vision | D blank image |
|---|---|---|---|---|
| Qwen2-VL-2B | 0.796 | 0.721 | 0.521 | 0.842 |
| Qwen2.5-VL-3B | 0.812 | 0.821 | 0.613 | 0.821 |

## 2. What the audit found (critic agent, then cross-checked by me)

**Verified by me on the raw data:** in condition C the judge labels REFUSAL on 90 of 125 Qwen2-VL-2B responses and 40 of 147 Qwen2.5-VL-3B responses that contain no refusal phrase in the first 150 characters. In conditions A, B, D the judge and a refusal-phrase check agree within a few points. So **condition C numbers are not trustworthy**.

**Agent-reported, plausible, not re-checked by me:** most of those C responses are step-by-step compliance; a crude reference puts true C refusal near 0.15 (2B) and 0.47 (3B), i.e. a vision gap of about 0.55 and 0.35, not 0.20. These are *proxy* values, not ground truth.

**Other flaws ranked by damage to reviewer trust (agent-reported):**
1. No human-validated judge, and the judge fails on C.
2. C uses a different text prompt from B ("phrase in image, list steps"), so the gap mixes modality, OCR and prompt wording. Missing control: same generic prompt with the phrase pasted into the text.
3. Refusal treated as safety with no benign controls; EconomicHarm and Sex are partly benign.
4. Steering has no random-direction control, a 24-prompt benign set, and the held-out ids come from the same dataset.
5. A is not the true backbone of the VLM; a text drop between A and B mixes training differences.
6. Items are clustered in 8 scenarios but tests treat them as independent; scenario-level Spearman uses n=8.
7. max_new_tokens=128 truncates 81% of 2B-C answers; judge sees only 900 characters.
8. Only Qwen models, one steered model.

**Blank-image result (agent-reported, partly checked):** blank image raised Qwen2-VL-2B refusal 0.72 -> 0.84 mainly by switching it to a short canned "I'm sorry, but I can't assist" mode (187 of 240 D responses), not by discriminating better. Do **not** claim "visual context improves safety".

## 3. Where we stand against the literature (lit-hunter agent; I verified one paper)

- **Already published:** text-derived refusal directions transfer to image inputs (MARS, arXiv 2606.31876, **verified by me**); safety degradation after adding vision (CMRM 2410.09047, VLGuard, Learning-to-See); typographic images weaker than text (FigStep, Text2VLM, TGA); over-refusal from global steering (CR-VLM, Arditi et al.). Blank/noise-image controls exist on LLaVA (CMRM).
- **Possibly open (search not exhaustive):** per-item and per-scenario coupling between text and vision refusal of the same request; the typographic/OCR channel inside refusal-direction transfer; model-specific blank-image behaviour on Qwen-VL; a refusal-gain vs over-refusal cost curve.
- **Consequence:** do not sell steering as the contribution. It is a replication/extension. The defensible story is a **careful measurement study**: how coupled are the two channels, how large is the gap once measured correctly, and what does steering cost.

## 4. What we may claim (claims ladder)

| Claim | Status |
|---|---|
| Typed-in-image harmful requests are refused far less than the same request as text, in both Qwen-VL models | Supported in direction (agent-reported magnitude 0.35-0.55 after correction). Magnitude must be re-measured. |
| Text and vision refusal are positively coupled, not a see-saw | Plausible; also explained by topic difficulty alone. Needs item-level analysis after re-judging and a topic-difficulty control. |
| Adding vision lowers text safety | Mixed: significant in 2B, null in 3B. Report as model-dependent. |
| Blank image changes refusal style (canned refusals) | Supported; do not frame as improved safety. |
| Text-derived steering transfers to vision | Not novel (MARS); our evidence lacks controls. Report only with controls. |
| Safety and over-refusal trade off along the steering strength | Supported in pilot; strengthen with n>=100 benign prompts. |

## 5. The fix list (experiment queue, free GPU)

| # | Experiment | Why | Cost |
|---|---|---|---|
| 1 | Hand-label ~100 items per condition; re-judge with a rubric that treats "provides steps" as compliance; add a second judge; report Cohen's kappa | The whole result depends on it | No GPU; ~1 evening |
| 2 | Condition E: generic TYPO prompt with the phrase pasted into the text; plus OCR read-back check | Separates modality from prompt/OCR | ~10 min per model |
| 3 | Benign twins (~100 harmless questions) through A-E | Measures over-refusal; resolves the blank-image question | ~15 min |
| 4 | Steering controls: random and orthogonal directions, n>=100 benign, activation-norm-scaled c, refusal-gain vs over-refusal plot | Makes the steering claim credible | ~1 h |
| 5 | n up to 100 per scenario (random ids), max_new_tokens>=256, cluster bootstrap by scenario, batch size 1 for final | Statistics a reviewer accepts | ~1-1.5 h per model |
| 6 | Third model family (e.g. LLaVA-1.5-7B in 4-bit or InternVL) | Not only Qwen | Kaggle/Colab |
| 7 | Reproduce one baseline: MM-SafetyBench/FigStep text-vs-typographic gap with their public code | Pipeline credibility | ~1-2 h |

## 6. Where to submit (venue-scout agent; official pages opened by it)

- **Best target: ACL 2027 via ARR, deadline Jan 4, 2027 AoE** (agent-reported; the ARR dates page did not list that cycle, so re-confirm). 4-page short or 8-page long; Responsible NLP checklist and Limitations section required.
- **Early feedback option:** AAAI-27 workshops, deadline **Nov 20, 2026**, non-archival: Deployable AI (4-page short papers), LLM Agents Under Threat (7 pages, single-blind). None is dedicated to VLM safety. Submit only if experiments 1-3 are done by then.
- **No-deadline option:** TMLR, rolling; reviews correctness, allows arXiv.
- **Not recommended:** CVPR Nov 16, 2026 (reviewer duty, ~4.5 weeks); FAccT (needs a sociotechnical angle).
- **Still to appear:** ICLR 2027 and NAACL 2027 workshop lists (~Feb 1/5, 2027); ICML 2027 (unverified third-party estimate Jan 22).

## 7. Timeline (assuming advisor agrees this week)

| Dates | Work |
|---|---|
| Oct 15-18 | Hand-label ~100 items per condition; fix judge; add conditions E and benign twins to the notebook; present pilot honestly as a pilot tomorrow |
| Oct 19-Nov 5 | Rerun with fixes on both Qwen pairs; steering controls; first draft of method + results |
| Nov 6-20 | Third model family; baseline reproduction; decide on a 4-page workshop submission (Nov 20) |
| Nov 21-Dec 20 | Full experiments at n=100 per scenario; related work from fully read papers; figures; paper draft |
| Dec 21-Jan 3 | Advisor review; Limitations/ethics; checklist; template compliance |
| Jan 4 | ARR submission for ACL 2027 |

## 8. First-time-author checklist (venue-scout)

- Register on arXiv with the PSU address; ask Prof. Le to endorse before first upload (info.arxiv.org/help/endorsement.html).
- Use the official LaTeX style files for the target venue; do not modify them.
- Ethics: state defensive purpose, show harmful outputs only in aggregate or redacted form, do not release copy-paste jailbreak artifacts, include a Limitations and risks paragraph, notify model vendors if a new vulnerability is found.
- Settle authorship order and advisor sign-off before submitting; complete OpenReview profiles; disclose generative-AI assistance.
- Expect double-blind review, ~3 reviewers, one short author response, and possibly reviewer duty.

## 9. Skills repos you pasted (not installed)

Read-only review by venue-scout: `fcakyon/phd-skills` (MIT; runs hooks and shell scripts automatically), `imbad0202/academic-research-skills` (CC BY-NC 4.0; needs an API key and costs per run; README warns of hallucinated citations), `lingzhi227/agent-research-skills` (no licence found; runs a post-install script). None is installed. Review any script before installing; the agents already used here cover literature search, audit and venue lookup. Verify every citation by hand regardless of tool.

## 10. Decisions needed

1. Approve the fix list in section 5 (steps 1-3 first).
2. Pick the target: ACL 2027 short paper (recommended) vs TMLR, with an optional Nov 20 workshop version.
3. Advisor meeting: claim framing (coupling + typographic channel, not steering novelty), authorship, whether non-training steering fits the "no heavy training" rule.
4. Who hand-labels the audit items (you, plus one other person if possible, to estimate agreement).
