# VLM Safety Alignment & Cross-Modal Conflict Presentations

This directory organizes all presentation decks across the project into dedicated folders.

---

## Directory Navigation

### [01_CURRENT_RESEARCH_PROPOSAL/](./01_CURRENT_RESEARCH_PROPOSAL/)
**The active Research Proposal deck (v2, rebuilt and checked against the source PDFs).**
- **`Cross_Modal_Signal_Conflict_Research_Proposal.pptx`** (30 slides: 25 main + 5 appendix; plain black/white Arial style)
  - Slides 1-5: project, problem, advisor constraints, variables. Slide 6: one-table map of all eight papers.
  - Slides 7-14: one slide per paper with original figures/tables cropped from the PDFs (native aspect ratio).
  - Slides 15-25: synthesis, related work to read, hypotheses, design, measurement, mechanism, feasibility, pilot status, roadmap, implications for alignment (future work).
  - Appendix: why no training (ADPO/SafeVLM) and extra figures.
- **`Cross_Modal_Signal_Conflict_Research_Proposal_Notes.md`**: plain-language speaker notes for every slide (also embedded in the .pptx).
- Rebuild: `python3 tools/build_proposal_deck_v2.py [--extract]`. The earlier unverified deck is archived in `04_INTERMEDIATE_DRAFTS/Proposal_v1_antigravity_UNVERIFIED*`.

---

### [05_PAPER_DEEP_DIVES/](./05_PAPER_DEEP_DIVES/)
**Term-by-term deep dives, for learning and explaining the papers (each with plain-language notes).**
- **`Deep_Dive_Papers_1-4_FigStep_HADES_SIUO_VLSBench.pptx`** (45 slides): ASR and PPL; Backbone/Text-only/Blank/Toxic and Typ image/T2I pointer/Opt/Adv; safe, effective and S&E rates; VSIL, R1, R2 and R1 minus R2.
- **`Deep_Dive_Papers_5-8_MMJailBench_CMRM_JailBound_SafetyReminder.pptx`** (36 slides): the four-factor grid, CASR and instruction mismatch; the shifting vector; linear probes and the I0/I1/T0/T1 grid; safety tokens and the safety-awareness classifier.
- Rebuild: `python3 tools/build_deep_dive_a.py` and `python3 tools/build_deep_dive_b.py`.

---

### [02_PREVIOUS_PRESENTED_DECKS/](./02_PREVIOUS_PRESENTED_DECKS/)
**Original presentations and materials from previous meetings.**
- **`Week1_Presented_10_Paper_Proposal.pptx`** (10.2 MB, 32 Slides)
  - *The exact deck presented to Prof. Thao Minh Le last week.*
  - Contains all 30 high-resolution pictures and notes (including Slide 32 with raw meeting notes).
- **`Week1_Initial_Draft_Presentation1.pptx`** (4.3 MB)
- **`Week1_Initial_Draft_Presentation1.pdf`** (2.5 MB)

---

### [03_EARLIER_PLANNED_EXPANSIONS/](./03_EARLIER_PLANNED_EXPANSIONS/)
**Expanded literature audits and 26-paper training proposal.**
- **`Bigger_26_Paper_Training_Proposal.pptx`** (138 KB, 30 Slides)
- **`Bigger_Proposal_Speaker_Notes.md`** (30 KB)

---

### [04_INTERMEDIATE_DRAFTS/](./04_INTERMEDIATE_DRAFTS/)
**Text-only drafts and transitional test files.**
- **`VLM_Cross_Modal_Conflict_Initial_Draft.pptx`** (85 KB)
- **`VLM_Safety_Alignment_Text_Only_Draft.pptx`** (153 KB)
- **`Earlier_Draft_Speaker_Notes.md`** (20 KB)

## 06_END_TO_END_10_SLIDES
`End_to_End_Project_Summary.pptx` (+ `_Notes.md`): ten slides covering the question, what papers 1-8 teach, the gap and three questions, design, measurement, mechanism, status and plan. Use it as the main talk; the two decks in `05_PAPER_DEEP_DIVES/` are the backup for "what does that metric mean". Built by `tools/build_end_to_end_deck.py`.

## 05_PAPER_DEEP_DIVES: compact version of papers 5-8
`Papers_5-8_In_Depth_10_Slides.pptx` (+ `_Notes.md`): ten slides, two per paper (MMJailBench, CMRM, JailBound, SafetyReminder) plus a synthesis, with native charts of the key tables. The 36-slide deck remains the row-by-row reference. Built by `tools/build_papers_5_8_in_depth.py`.

## 07_PRESENT_THIS_WEEK_14_SLIDES
`Cross_Modal_Conflict_14_Slides.pptx` (+ `_Notes.md`): the presentation to give. End-to-end story (question, literature map, gap, design, measurement, mechanism, status, plan) with five papers in depth (FigStep, VLSBench, MMJailBench, CMRM, SafetyReminder). HADES, SIUO and JailBound are one-line mentions; the decks in `05_PAPER_DEEP_DIVES/` are backup. Built by `tools/build_presentation_14.py`.

`07_PRESENT_THIS_WEEK_14_SLIDES/Cross_Modal_Conflict_14_Slides_v2.pptx`: copy of the user-edited 14-slide deck (original untouched) with exact paper figures/tables and outlined cells on slides 3-8, a question to ask on slides 4-14, and unneeded material removed. Built by `tools/build_presentation_14_v2.py`.
