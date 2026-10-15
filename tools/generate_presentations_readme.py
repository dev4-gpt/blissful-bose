from pathlib import Path

pres_dir = Path("/Users/aryamandev/Developer/blissful-bose/presentations")

readme_root = """# VLM Safety Alignment & Cross-Modal Conflict Presentations

This directory organizes all presentation decks across the project into clear, dedicated folders.

---

## Folder Structure & Guide

### [01_CURRENT_SEMINAR/](./01_CURRENT_SEMINAR/)
**The definitive seminar deck for your upcoming meeting with Prof. Thao Minh Le.**
- **`Cross_Modal_Signal_Conflict_Seminar_OptionB.pptx`** (5.1 MB, 20 Slides)
  - **Option B Implementation:** Zero training pipelines, zero defense wrappers, zero benchmark bloat.
  - **Part I (What Has Been Done):** Complete audit of 9 papers:
    - *FigStep* (Slide 5: 2 figures, 380 words notes)
    - *PolyJailbreak* (Slide 6: 2 figures, 777 words notes)
    - *HADES* (Slide 7: 2 figures, 652 words notes)
    - *SIUO* (Slide 8: 2 figures, 535 words notes)
    - *VLSBench* (Slide 9: 1 figure, 413 words notes)
    - *MMJailBench* (Slide 10: Table 3 crop from PDF)
    - *CMRM* (Slide 11: Fig 1 hidden-state geometry crop)
    - *JailBound* (Slide 12: Fig 1 boundary linear probing crop)
    - *SafetyReminder* (Slide 13: Fig 1 attention dynamics crop)
  - **Part II (What Else Can Be Done):** Zero-Training Causal Probing Methodology:
    - Slide 14: Research Gaps (Saliency unmapped, hierarchy untested, layer attribution missing)
    - Slide 15: The 3×3 Counterfactual Conflict Matrix
    - Slide 16: Three Falsifiable Hypotheses (H1 Saliency Sigmoid, H2 Hierarchy Vulnerability, H3 Early-Layer Suppression)
    - Slide 17: Causal Intervention Protocol (12–72pt font sweeps, 1.5–21:1 contrast, L0–L3 hierarchy sweeps)
    - Slide 18: Behavioral Measurement & Mechanistic Attribution (3 states, AttnRatio formula, layer-wise bifurcation)
    - Slide 19: Pilot Implementation & 3-Week Roadmap (Qwen2-VL-2B, <5 GB VRAM, Colab T4, zero training runs)
    - Slide 20: Appendix / Backup on Why Training Defenses Fail (ADPO Table 1: 11.3pt reasoning drop, OCR degradation; SafeVLM over-refusal)
- **`Cross_Modal_Signal_Conflict_Speaker_Notes.md`**: Complete word-for-word speaker script, figure walkthrough instructions, and Q&A prep for every slide.

---

### [02_PREVIOUS_PRESENTED_DECKS/](./02_PREVIOUS_PRESENTED_DECKS/)
**Original presentations and materials presented in previous meetings.**
- **`Week1_Presented_10_Paper_Proposal.pptx`** (10.2 MB, 32 Slides)
  - *The exact deck presented to Prof. Thao Minh Le last week.*
  - Contains all 30 high-resolution pictures and notes (including Slide 32 with meeting notes).
- **`Week1_Initial_Draft_Presentation1.pptx`** (4.3 MB)
  - Initial presentation draft from late September.
- **`Week1_Initial_Draft_Presentation1.pdf`** (2.5 MB)
  - Rendered PDF version of Presentation1.

---

### [03_EARLIER_PLANNED_EXPANSIONS/](./03_EARLIER_PLANNED_EXPANSIONS/)
**Expanded literature audits and 26-paper training proposal.**
- **`Bigger_26_Paper_Training_Proposal.pptx`** (138 KB, 30 Slides)
  - Comprehensive audit of 26 small-VLM papers, proposing a 6-baseline training matrix (B0–B5) and attack protocol (A0–A5).
- **`Bigger_Proposal_Speaker_Notes.md`** (30 KB)
  - Extensive speaker notes covering all 26 audited papers and baseline comparisons.

---

### [04_INTERMEDIATE_DRAFTS/](./04_INTERMEDIATE_DRAFTS/)
**Text-only drafts and transitional test files.**
- **`VLM_Cross_Modal_Conflict_Initial_Draft.pptx`** (85 KB)
- **`VLM_Safety_Alignment_Text_Only_Draft.pptx`** (153 KB)
  - The text-only draft previously stored in `presentation/`.
- **`Earlier_Draft_Speaker_Notes.md`** (20 KB)
"""

(pres_dir / "README.md").write_text(readme_root, encoding="utf-8")
print("Wrote presentations/README.md successfully.")
