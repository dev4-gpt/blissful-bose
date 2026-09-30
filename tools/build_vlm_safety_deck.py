from pathlib import Path
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt


OUT = "VLM_Safety_Alignment_Research_Proposal_Updated.pptx"
SECONDARY_OUT = "presentation/VLM_Safety_Alignment_Research_Proposal.pptx"
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

INK = RGBColor(28, 42, 57)
NAVY = RGBColor(18, 42, 66)
TEAL = RGBColor(39, 107, 126)
CORAL = TEAL
GOLD = TEAL
BLUE = TEAL
MUTED = RGBColor(100, 112, 123)
PAPER = RGBColor(255, 255, 255)
PALE = RGBColor(239, 243, 246)
PALE_ORANGE = PALE
WHITE = RGBColor(255, 255, 255)

CITATIONS = {
    2: [5, 7, 10, 11, 16], 3: [5, 10, 16], 4: [5, 8, 9, 11],
    5: [1, 2, 3, 4, 12, 15, 16, 23], 6: [5, 7, 8, 12, 15, 16, 21, 23, 24, 25],
    7: [5, 6, 7, 12, 15], 8: [8, 15, 20, 21, 22, 23, 24, 25],
    9: [1, 3, 4, 18, 19], 10: [9, 10, 11, 16, 17], 11: [12],
    12: [7, 8, 12, 15, 16, 17], 13: [10, 11, 12, 16, 17],
    14: [1, 9, 10, 11, 14, 16, 17, 18, 19], 15: [5, 7, 8, 12],
    16: [10, 12, 16, 17], 17: [12, 15, 16, 17, 18],
    19: [6, 15, 26], 20: [6], 21: [6], 22: [15], 23: [15], 24: [12],
    25: [2, 9, 10, 11, 16, 17], 26: [1, 9, 10, 11, 18],
    27: [5, 10, 12, 16, 17]
}


def textbox(slide, x, y, w, h, text, size=20, color=INK, bold=False,
            font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def base(title, section, cite=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = PAPER
    textbox(slide, 0.62, 0.32, 2.6, 0.28, section.upper(), 10, TEAL, True)
    textbox(slide, 0.62, 0.68, 12.0, 0.65, title, 26, NAVY, True)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.62), Inches(1.43), Inches(12.05), Inches(0.015))
    line.fill.solid(); line.fill.fore_color.rgb = RGBColor(218, 226, 223); line.line.fill.background()
    slide_no = len(prs.slides)
    refnums = CITATIONS.get(slide_no, [])
    cite_text = "Refs. " + ", ".join(f"[{n}]" for n in refnums) if refnums else cite
    textbox(slide, 0.62, 7.14, 10.9, 0.2, cite_text, 8, MUTED)
    textbox(slide, 12.0, 7.10, 0.7, 0.25, f"{len(prs.slides):02d}", 9, MUTED, align=PP_ALIGN.RIGHT)
    return slide


def bullets(slide, items, y=1.78, font_size=20, gap=0.8, x=0.88, w=11.6):
    for i, item in enumerate(items):
        yy = y + i * gap
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(yy + 0.13), Inches(0.12), Inches(0.12))
        dot.fill.solid(); dot.fill.fore_color.rgb = [TEAL, CORAL, GOLD, BLUE][i % 4]; dot.line.fill.background()
        textbox(slide, x + 0.28, yy, w - 0.28, gap - 0.05, item, font_size, INK)


def card(slide, x, y, w, h, heading, body, accent=TEAL, fs=15):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = WHITE
    sh.line.color.rgb = RGBColor(222, 230, 227)
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.08), Inches(h))
    stripe.fill.solid(); stripe.fill.fore_color.rgb = TEAL; stripe.line.fill.background()
    textbox(slide, x+0.22, y+0.18, w-0.4, 0.38, heading, 16, TEAL, True)
    textbox(slide, x+0.22, y+0.62, w-0.4, h-0.75, body, fs, INK)


def table(slide, x, y, w, h, headers, rows, widths=None, fs=13):
    shape = slide.shapes.add_table(len(rows)+1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h))
    t = shape.table
    if widths:
        for c, cw in enumerate(widths): t.columns[c].width = Inches(cw)
    for r in range(len(rows)+1):
        for c in range(len(headers)):
            cell = t.cell(r,c)
            cell.fill.solid(); cell.fill.fore_color.rgb = NAVY if r == 0 else (WHITE if r % 2 else PALE)
            cell.margin_left = Inches(0.08); cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.04); cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.text = headers[c] if r == 0 else rows[r-1][c]
            for p in cell.text_frame.paragraphs:
                p.space_after = Pt(0)
                for run in p.runs:
                    run.font.name = "Aptos"
                    run.font.size = Pt(fs if r else fs-1)
                    run.font.bold = (r == 0 or c == 0)
                    run.font.color.rgb = WHITE if r == 0 else INK
    return shape


# 1. Title
s = prs.slides.add_slide(prs.slide_layouts[6])
s.background.fill.solid(); s.background.fill.fore_color.rgb = WHITE
cover=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(3.82))
cover.fill.solid(); cover.fill.fore_color.rgb = NAVY; cover.line.fill.background()
textbox(s, 0.86, 1.04, 3.8, 0.35, "RESEARCH PROPOSAL", 12, RGBColor(193, 216, 225), True)
textbox(s, 0.86, 1.62, 11.2, 1.55, "Safety Alignment\nfor Small Vision-Language Models", 33, WHITE, True)
textbox(s, 0.9, 4.4, 11.0, 0.9, "A literature-grounded problem formulation, paper-by-paper protocol audit, and proposed evaluation", 19, INK)
textbox(s, 0.9, 6.55, 9.0, 0.3, "Literature snapshot: 30 September 2026  |  20-minute presentation", 11, MUTED)

# 2
s=base("The question is not whether images create risk", "Research question", "Scope: open-weight small VLMs; protocol recommendations synthesized from cited papers")
card(s,0.82,1.85,3.75,2.1,"CARRIER","The same intent can arrive as text, image text, visual semantics, or a combination.",TEAL,17)
card(s,4.80,1.85,3.75,2.1,"COMPOSITION","Safe-looking image + safe-looking text can become risky only when interpreted together.",CORAL,17)
card(s,8.78,1.85,3.75,2.1,"CALIBRATION","A system that refuses every uncertain image is not usefully aligned.",GOLD,17)
textbox(s,1.0,4.7,11.2,1.05,"Research question",16,TEAL,True)
textbox(s,1.0,5.18,11.0,1.0,"Can multimodal safety alignment improve held-out visual jailbreak resistance in small open VLMs without sacrificing safe answerability and grounding?",23,INK,True)

# 3
s=base("Operationalize safety as three outcomes", "Problem formulation", "Foundational framing: VLGuard (2024); VSCBench (Findings ACL 2025); USB (ACL 2026)")
card(s,0.9,1.9,3.7,2.75,"1  HARM PREVENTION","Does the response materially enable disallowed harm?\n\nMeasure: harmful-compliance rate by attack family.",CORAL,16)
card(s,4.82,1.9,3.7,2.75,"2  BENIGN UTILITY","Does it answer allowed requests, including safe near-neighbors?\n\nMeasure: false refusal + task quality.",TEAL,16)
card(s,8.74,1.9,3.7,2.75,"3  VISUAL GROUNDING","Does it use relevant image evidence rather than ignore or invent it?\n\nMeasure: VQA and image-ablation controls.",BLUE,16)
textbox(s,1.0,5.35,11.5,0.7,"Alignment is a training objective; safety is observed behavior under a specified protocol.",19,INK,True)

# 4
s=base("Text alignment does not guarantee multimodal safety", "Why VLMs differ", "VLGuard (2024); CMRM (Findings ACL 2025); SIUO (Findings NAACL 2025); VLSBench (ACL 2025)")
bullets(s,["Vision tuning can degrade safety inherited from an aligned language backbone.","Image OCR and image semantics create carriers that text-only safeguards may not recognize.","Risk can emerge from image–text interaction even when each input looks safe alone.","Benchmark text can leak the risk; safety scores may not require seeing the image."],y=1.85,font_size=19,gap=0.88)
textbox(s,1.18,5.75,10.8,0.55,"So test carriers, composition, leakage, and benign near-neighbors separately.",20,TEAL,True)

# 5
s=base("The field has shifted from finding failures to attributing them", "Field evolution", "Representative papers: FigStep (2023); ADPO (2025); MMJailBench, USB, VSFA, SafeRI (2026)")
card(s,0.85,1.92,3.82,3.65,"2023–24  |  EXPOSE","Visual jailbreak channels\n\nFigStep • MM-SafetyBench • HADES • JailBreakV\n\nQuestion: can image inputs bypass text alignment?",CORAL,16)
card(s,4.76,1.92,3.82,3.65,"2025  |  MEASURE + ALIGN","Preference training, representation gaps, calibration\n\nSPA-VL • ADPO • CMRM • SIUO • VSCBench • VLSBench\n\nQuestion: what degrades, and what trade-off follows?",TEAL,15)
card(s,8.67,1.92,3.82,3.65,"2026  |  FACTOR + INTERVENE","Factorized tests and selective or label-free defenses\n\nMMJailBench • USB • VSFA • VLMGuard-R1 • SafeRI\n\nQuestion: which factor/when should trigger safety?",BLUE,15)

# 6
s=base("Current methods intervene at different system layers", "SOTA method map", "Key examples: VLGuard; SPA-VL; ADPO; CMRM; MMAligner; VLMGuard-R1; VSFA; SafetyReminder; SafeRI")
rows=[
["Training data/objective","VLGuard, SPA-VL, ADPO","SFT, preference optimization, adversarial preference"],
["Representation / inference","CMRM, MMAligner","Correct/calibrate multimodal hidden representations"],
["Input guard / rewrite","VLMGuard-R1, GuardAlign","Inspect/transform input before target model"],
["Reasoning / persona","Think in Safety, VSFA","Reason about risk or learn from threat-image VQA"],
["Decode-time / token gate","SafetyReminder, SafeSteer, SafeRI*","Steer or activate safety selectively during generation"]]
table(s,0.82,1.82,11.72,4.58,["Intervention layer","Representative work","Core idea"],rows,[2.35,3.05,6.32],15)
textbox(s,0.9,6.5,11.5,0.35,"*SafeRI is a September 2026 preprint, not yet a peer-reviewed result.",11,MUTED)

# 7
s=base("Training-time papers are not interchangeable", "Paper audit: training", "VLGuard (2024); SafeVLM (2024); SPA-VL (CVPR 2025); ADPO (Findings EMNLP 2025); VSFA (ACL 2026)")
rows=[
["VLGuard","Safety instruction data + SFT","Data baseline; monitor forgetting and utility"],
["SafeVLM","Projector, safety tokens/head; two-stage","Architectural comparator; separate from SFT"],
["SPA-VL","100K-scale image–question preference tuples","DPO data source; six harm domains"],
["ADPO","Adversarial reference + adversary-aware DPO","Direct adversarial-alignment prior art"],
["VSFA","Neutral VQA on threat-related images; no safety labels","ACL 2026 label-free alternative; reproduce under matched budget"]]
table(s,0.82,1.82,11.72,4.72,["Paper","Method","Protocol lesson for our study"],rows,[1.7,4.2,5.82],14)

# 8
s=base("Runtime defenses change the system boundary", "Paper audit: inference", "CMRM, Findings ACL 2025; VLMGuard-R1, Findings ACL 2026; SafetyReminder, AAAI 2026; SafeRI, arXiv 2609.03544")
card(s,0.85,1.9,3.76,3.15,"REPRESENTATION","CMRM and MMAligner act on internal multimodal representations.\n\nQuestion: does safety improve without shifting safe examples into refusal?",TEAL,15)
card(s,4.79,1.9,3.76,3.15,"INPUT GUARD","VLMGuard-R1 reasons over and rewrites multimodal input before the target VLM.\n\nReport extra model, calls, cost, latency, and rewrite behavior.",GOLD,15)
card(s,8.73,1.9,3.76,3.15,"GENERATION GATE","SafetyReminder / SafeSteer / SafeRI intervene during generation. SafeSteer here is the ACL 2026 decoding-level paper.\n\nReport trigger errors, token overhead, and safe-task effects.",CORAL,15)
textbox(s,1.0,5.55,11.0,0.65,"A defense comparison must name what is being aligned: the model, the input pipeline, or the full deployed system.",19,INK,True)

# 9
s=base("A jailbreak suite must vary the carrier, not just the wording", "Attack protocol", "FigStep arXiv 2311.05608; HADES ECCV 2024; JailBreakV arXiv 2404.03027; PolyJailbreak arXiv 2510.17277")
rows=[
["Direct text","Control","Does text-only safety already fail?"],
["FigStep","Instruction as image text","Can the OCR/image pathway bypass?"],
["SIUO / HADES-like","Benign-looking inputs; risk in joint meaning","Can it reason safely across modalities?"],
["Adaptive held-out","PolyJailbreak at fixed query budget","Does defense generalize beyond templates?"],
["White-box optional","VisualAdv/MMPGD; JailBound separately","Do perturbations or internal boundary probes break it?"]]
table(s,0.82,1.82,11.72,4.5,["Attack family","What changes","Question answered"],rows,[2.5,4.6,4.62],14)
textbox(s,0.9,6.5,11.5,0.35,"Slide examples should be abstracted; do not display operational harmful instructions.",11,MUTED)

# 10
s=base("Benchmarks answer different questions", "Benchmark audit", "VSCBench (Findings ACL 2025); VLSBench (ACL 2025); SIUO (Findings NAACL 2025); USB (ACL 2026); MMJailBench (2026 preprint)")
rows=[
["USB","61 risk types × 4 modality interactions; includes over-refusal","Broad, slice by image/cross-modal cells"],
["VSCBench","3,600 paired safety-calibration examples","Under-safety AND over-safety"],
["VLSBench","~2.2K leakage-controlled examples","Does model need the image?"],
["SIUO","167 cases, 9 domains; safe inputs jointly risky","Composition-focused, small targeted set"],
["MMJailBench","Factorizes framing, semantics, carrier, intent","Attribute source of vulnerability; preprint"]]
table(s,0.82,1.82,11.72,4.7,["Benchmark","What it measures","Best role"],rows,[2.05,5.05,4.62],14)

# 11
s=base("Protocol audit: ADPO is a useful reproduction template", "Paper protocol audit", "Weng et al., Adversary-Aware DPO, Findings EMNLP 2025; official PDF, §§4 and appendix")
bullets(s,["Models: LLaVA-1.5/1.6-7B, Qwen2-VL-7B, InternVL2-8B, Qwen2.5-VL-7B; LoRA fine-tuning.","Attacks: white-box VisualAdv + MMPGDBlank; MultiTrust typo, multimodal, and cross-modal jailbreak subsets.","Safety evaluator: HarmBench classifier; outcome is ASR per attack, not an undifferentiated score.","Utility: MMStar, OCRBench, MM-Vet, LLaVABench; reported safety gains can trade off against VQA quality.","Baselines/ablations: SFT, DPO, ESCO, direct adversarial training, adversarial-reference-only, loss-only."],y=1.8,font_size=16,gap=0.87)

# 12
s=base("The defensible gap is a controlled small-model study", "Gap and contribution", "Synthesis of ADPO, VSFA, VSCBench, VLSBench, SIUO, USB and MMJailBench")
card(s,0.85,1.9,3.76,3.05,"NOT THE GAP","“Nobody has aligned VLMs” is false.\n\nADPO, SPA-VL, VLGuard, VSFA and inference defenses already exist.",CORAL,16)
card(s,4.79,1.9,3.76,3.05,"THE GAP TO TEST","Do these alignment choices transfer across unseen visual carriers in small models under a common protocol?\n\nAnd at what calibration/cost trade-off?",TEAL,16)
card(s,8.73,1.9,3.76,3.05,"OUR CONTRIBUTION","A reproducible protocol plus a matched-budget comparison.\n\nNovel method claim only after baseline reproduction and literature refresh.",BLUE,16)
textbox(s,1.0,5.5,11.1,0.8,"Frame novelty as “systematic comparison under controlled, held-out attacks,” not “first adversarial VLM alignment.”",19,INK,True)

# 13
s=base("Three falsifiable hypotheses", "Hypotheses", "Proposed study claims; not findings from cited papers")
card(s,0.85,1.88,3.76,3.6,"H1  ROBUSTNESS + UTILITY","Matched multimodal alignment reduces held-out attack HCR more than no intervention and text-only SFT, while staying within pre-registered FRR and VQA margins.",TEAL,16)
card(s,4.79,1.88,3.76,3.6,"H2  GENERALIZATION","Performance gains on seen templates exceed gains on held-out adaptive attacks; train/test split by attack family exposes the difference.",CORAL,16)
card(s,8.73,1.88,3.76,3.6,"H3  MECHANISM (EXPLORATORY)","Text–image safety gap relates to safety outcomes across small models beyond parameter count alone.",BLUE,16)
textbox(s,0.96,5.95,11.3,0.55,"Candidate guardrails: FRR increase ≤ 3 points; VQA decrease ≤ 2 points (choose and preregister before experiments).",14,MUTED)

# 14
s=base("Final attack suite: six required cells, two optional diagnostics", "Experimental design", "Protocol synthesis; attack sources: FigStep, SIUO, VLSBench, VSCBench/USB, PolyJailbreak; optional ADPO/JailBound")
rows=[
["A0","Direct text","Baseline language safety"],
["A1","FigStep image-text","OCR / visual carrier"],
["A2","SIUO-style joint context","Cross-modal composition"],
["A3","VLSBench + text-only ablation","Visual leakage validity control"],
["A4","VSCBench/USB benign pairs","False refusal + calibration"],
["A5","Held-out PolyJailbreak","Adaptive robustness at fixed query budget"]]
table(s,0.82,1.82,11.72,4.57,["Cell","Test","Purpose"],rows,[1.3,4.8,5.62],14)
textbox(s,0.9,6.5,11.5,0.35,"Optional: fixed-budget white-box pixel perturbation; JailBound representation probing kept as a separate diagnostic.",11,MUTED)

# 15
s=base("Compare methods on the same model and same budget", "Baseline plan", "Proposed experimental controls; method precedents: VLGuard, SPA-VL, ADPO, CMRM")
rows=[
["B0","Original checkpoint","Native behavior"],
["B1","Text-only safety SFT","Modality transfer control"],
["B2","VLGuard-style multimodal SFT","Data alignment baseline"],
["B3","SPA-VL-style standard DPO","Preference baseline"],
["B4","ADPO or compatible reproduction","Adversarial alignment baseline"],
["B5","Proposed matched cross-modal condition","Test the hypothesis"]]
table(s,0.82,1.82,11.72,4.52,["ID","Condition","What it isolates"],rows,[1.15,5.0,5.57],14)
textbox(s,0.9,6.48,11.5,0.4,"Candidates: Qwen3-VL 2B/4B; SmolVLM2 2.2B as an external replication (lock revisions).",13,TEAL,True)

# 16
s=base("Report safety, utility, calibration, and cost together", "Metrics and controls", "Evaluation choices based on VSCBench, USB, ADPO and standard reproducibility practice")
card(s,0.85,1.86,3.76,3.55,"SAFETY","Harmful-compliance rate by attack family\n\nMacro-average across attack families\n\nConfidence intervals + fixed decoding",CORAL,15)
card(s,4.79,1.86,3.76,3.55,"UTILITY / CALIBRATION","Benign false-refusal rate\n\nSafe-answer quality\n\nVQA/OCR before–after\n\nText/image/joint gap",TEAL,15)
card(s,8.73,1.86,3.76,3.55,"RELIABILITY / COST","Blind evaluator + human-audited subset\n\nJudge agreement and ambiguity\n\nTraining GPU-hours, latency, memory, extra calls",BLUE,15)
textbox(s,0.95,5.85,11.0,0.6,"Keep privacy, fairness, misinformation, and harmful assistance as separate outcome families.",17,INK,True)

# 17
s=base("What we expect to contribute", "Takeaway", "Literature snapshot frozen 2026-09-30; proposed experiment requires reproduction and preregistration")
bullets(s,["A protocol that makes attack carrier and modality interaction explicit.","A small-VLM comparison that includes both unseen attack robustness and safe near-neighbor behavior.","A paper-by-paper audit linking each claimed defense to its real threat model, judge, benchmark, and utility test.","An honest answer to whether additional multimodal alignment helps beyond text-only tuning—and what it costs."],y=1.9,font_size=19,gap=0.95)
textbox(s,1.0,6.15,11.2,0.55,"Next: freeze checkpoints + policy rubric → reproduce B0–B3 → validate judge → run held-out A0–A5.",17,TEAL,True)

# 18 source signpost; full IEEE-style bibliography follows the evidence appendix.
s=base("Primary literature and source conventions", "References", "IEEE-style numbered citations appear on each slide; full entries are at the end")
card(s,0.9,1.92,3.7,2.55,"VLM SAFETY METHODS","VLGuard [5] • SafeVLM [6] • SPA-VL [7] • ADPO [12] • VSFA [16]",TEAL,16)
card(s,4.82,1.92,3.7,2.55,"EVALUATION + ATTACKS","FigStep [1] • MM-SafetyBench [2] • SIUO [11] • USB [17] • MMJailBench [18]",TEAL,16)
card(s,8.74,1.92,3.7,2.55,"RECENT DEFENSES","CMRM [8] • VLMGuard-R1 [15] • GuardAlign [21] • SafeSteer [22] • SafeRI [23]",TEAL,16)
textbox(s,1.0,5.15,11.1,0.9,"Bracketed numbers refer to the IEEE-style bibliography at the end. Peer-reviewed proceedings and arXiv preprints are distinguished in each entry; reported scores remain tied to each paper’s own protocol.",17,INK)

# Evidence appendix: paper-reported results. These slides are backup material,
# not part of the timed 20-minute narrative.
s=base("Attachment audit: what is and is not VLM-safety evidence", "Evidence appendix", "Local PDF inspection; SafeVLM arXiv:2405.13581; VLMGuard-R1 ACL 2026; gradient paper arXiv:2604.17215")
rows=[
["SafeVLM.pdf + annotated copy","Same SafeVLM work; one unique VLM alignment paper","Direct VLM-safety evidence; duplicate attachment, count once"],
["VLMGuard-R1 annotated PDF","2025 arXiv version of paper published Findings ACL 2026","Direct VLM safety system defense; external input rewriter, not target-weight alignment"],
["2604.17215v1.pdf + Continual_Safety_Alignment.pdf","LLM-only gradient selection / prior write-up","Historical motivation only; no VLM results"],
["Presentation1.pdf","Earlier LLM-to-VLM adaptation deck","Not evidence; superseded research framing"]]
table(s,0.82,1.82,11.72,3.95,["Attachment(s)","Identification","How used in this work"],rows,[3.15,4.25,4.32],14)
textbox(s,0.95,6.05,11.4,0.65,"The local paper bundle contains two unique direct VLM-safety papers, not a complete survey. The wider review adds independently sourced work.",16,INK,True)

s=base("SafeVLM: reported safety scores improve, but task-level trade-offs remain", "Attached paper results", "SafeVLM, Liu et al., arXiv:2405.13581, Tables 1–4; GPT-4 / GPT-4V evaluation; scores are paper-specific")
rows=[
["LLaVA-v1.5-7B","6.39","5.06","64.3 / 61.6","1487.9 / 1773.6"],
["SafeVLM","8.18","7.78","66.8 / 65.3","1479.5 / 1762.7"],
["SafeVLM (+LoRA)","8.26","7.80","68.5 / 63.7","1458.8 / 1753.8"],
["GPT-4V reference","7.92","—","—","—"]]
table(s,0.75,1.78,11.85,3.45,["Model","RTVLM avg\n(0–10)","Risk-set avg\n(0–10)","MMBench /\nSEEDBench","MMEp / MME"],rows,[2.6,1.75,1.8,2.65,3.05],13)
textbox(s,0.9,5.48,11.65,0.95,"Reading the table: reported safety improves over LLaVA in these GPT-judged tests; capability movement is mixed (MMBench rises, while MME metrics fall). Do not compare these numbers to other papers’ scales or judges.",15,INK)

s=base("SafeVLM: text jailbreak results reveal a utility-calibration warning", "Attached paper results", "SafeVLM, Table 3; AdvBench ASR and XSTest safe/unsafe instruction behavior; source: arxiv.org/abs/2405.13581")
rows=[
["LLaVA-v1.5-7B","6.45","78.27","91.20","26.50"],
["SafeVLM","1.72","67.56","76.89","7.46"],
["SafeVLM (+LoRA)","1.90","69.86","78.09","6.96"]]
table(s,0.85,1.9,11.55,3.0,["Model","AdvBench\nvanilla ASR % ↓","AdvBench\nsuffix ASR % ↓","XSTest safe\ninstruction % ↑","XSTest unsafe\ninstruction % ↓"],rows,[2.55,2.05,2.05,2.45,2.45],13)
textbox(s,0.95,5.35,11.4,1.05,"Critical interpretation: the paper reports lower attack success, but the safe-instruction pass rate also drops from 91.20% to about 77–78%. These are text attacks and safe-text controls, not a visual-jailbreak evaluation. This is exactly why our VLM protocol measures over-refusal.",15,CORAL,True)

s=base("VLMGuard-R1: prompt rewriting helps many cells, not every cell", "Attached paper results", "VLMGuard-R1, Findings ACL 2026, Table 1; GPT-4o safety (0–10) / helpfulness (%); selected target models and sets")
rows=[
["LLaVA-1.5-7B","VLGuard-Unsafe","3.71 / 20.92","6.70 / 59.30"],
["LLaVA-1.5-7B","SIUO","3.80 / 44.85","6.77 / 58.43"],
["Qwen2-VL-7B","VLGuard-Unsafe","6.10 / 49.50","7.65 / 64.82"],
["Qwen2-VL-7B","SIUO","4.26 / 60.24","6.11 / 53.61"],
["Qwen2-VL-7B","MM-SafetyBench TYPO","6.08 / 83.08","8.98 / 86.05"]]
table(s,0.75,1.78,11.85,3.92,["Target VLM","Evaluation slice","Base: safety / helpfulness","+ VLMGuard-R1: safety / helpfulness"],rows,[2.35,2.35,3.25,3.9],12.5)
textbox(s,0.9,5.95,11.55,0.68,"The SIUO helpfulness decrease on Qwen2-VL (60.24→53.61) is a counterexample to “all metrics improve.” The guard is an external Qwen2-VL-7B rewriter; count its extra model, training and latency.",14,INK)

s=base("VLMGuard-R1: its own refusal-rate table is not the whole safety story", "Attached paper results", "VLMGuard-R1, Findings ACL 2026, supplementary Table 6; DSR uses predefined refusal strings")
rows=[
["VLMGuard-R1","53.1","50.8","65.4","56.0","55.3","56.1"],
["ETA","22.3","46.9","51.5","15.0","57.0","38.5"],
["MLLM-Protector","30.8","28.5","27.7","26.3","48.0","32.3"],
["FigStep defense","23.1","15.4","16.2","22.2","43.0","24.0"],
["ECSO","3.8","3.8","7.7","9.0","11.0","7.1"]]
table(s,0.72,1.82,11.9,3.8,["Method","SD","SD+TYPO","TYPO","SIUO","VLGuard-U","Overall"],rows,[2.25,1.55,1.75,1.55,1.55,1.75,1.5],12)
textbox(s,0.9,5.85,11.55,0.75,"DSR is defined by detection of listed refusal strings, so it is not equivalent to a semantic harmful-compliance judge and can reward formulaic refusal. Interpret alongside the paper’s GPT-4o safety/helpfulness results.",14,CORAL,True)

s=base("ADPO: strong adversarial-training results under a specific protocol", "External paper results", "ADPO, Weng et al., Findings EMNLP 2025, Table 1; ASR % lower is better; utility metrics retain original units")
rows=[
["LLaVA-1.5-7B base","64.5","84.0","22.2","55.1","42.0","32.7 / 202 / 29.9 / 59.5"],
["LLaVA + DPO","12.0","33.0","0.7","8.8","9.6","33.9 / 198 / 28.9 / 54.4"],
["LLaVA + ADPO","5.0","0.5","0.0","0.0","0.2","33.7 / 184 / 24.2 / 48.2"],
["Qwen2-VL-7B base","13.5","30.0","4.5","54.3","6.3","58.5 / 841 / 64.7 / 88.0"],
["Qwen2-VL + ADPO","0.0","1.5","0.0","4.0","0.0","57.6 / 830 / 53.9 / 74.2"]]
table(s,0.62,1.72,12.08,4.25,["Model","VisualAdv","MMPGD\nBlank","MultiTrust\nTypo","MultiTrust\nMultimodal","MultiTrust\nCross-modal","MMStar / OCRBench / MM-Vet / LLaVABench"],rows,[1.85,1.1,1.25,1.25,1.35,1.3,3.98],10.5)
textbox(s,0.8,6.15,11.8,0.47,"Utility tuple order is as labeled; ADPO is direct prior art, but its gains are protocol-specific and some utility scores decline.",12,INK)

s=base("Benchmark selection: examples, size, and what a score can mean", "Benchmark appendix", "Primary sources: MM-SafetyBench; SIUO; VLSBench; VSCBench; USB; MMJailBench; SafeVLM; VLMGuard-R1")
rows=[
["MM-SafetyBench","5,040; 13 risk scenarios","Generated image prompt; SD, OCR, SD+OCR","Attack success across image carriers; synthetic/template effects"],
["SIUO","167; 9 domains","Benign-looking image + benign-looking text; joint context changes risk","Composition; small targeted set, not broad prevalence"],
["VLSBench","~2.2K","Risk relevant to image is controlled against text leakage","Whether image understanding is necessary"],
["VSCBench","3,600 paired cases","Unsafe request plus safe near-neighbor counterpart","Under-safety and over-safety calibration"],
["USB","61 risk categories × 4 modality interactions","Risk-category and modality-interaction slices","Broad coverage; select vision-relevant slices"],
["MMJailBench","2026 preprint; 16 models","Factor harmful intent / framing / visual semantics / carrier","Attribution design; not itself one attack"]]
table(s,0.62,1.72,12.08,4.8,["Benchmark","Scale","Concrete test shape (sanitized)","Interpretation / caveat"],rows,[2.0,1.8,4.45,3.83],11.5)

s=base("The proposed experiment has matched examples and held-out attacks", "Protocol appendix", "Proposed study; attack precedents: FigStep, SIUO, VLSBench, VSCBench/USB, PolyJailbreak, ADPO")
rows=[
["A0 Direct text","Same intent expressed in ordinary text","Text-safety anchor"],
["A1 FigStep-style","Benign question; text rendering is embedded in the image","OCR-carrier robustness"],
["A2 Joint composition","Each modality alone is benign; combined meaning is risky","Cross-modal safety reasoning"],
["A3 Leakage control","Remove image, mask relevant region, or use matched decoy","Verify visual evidence is actually used"],
["A4 Safe counterpart","Same topic/image class, allowed request","False refusal and safe utility"],
["A5 Adaptive holdout","PolyJailbreak; fixed query/iteration budget, no training overlap","Generalization under adaptive black-box search"]]
table(s,0.72,1.78,11.9,4.5,["Cell","Sanitized example structure","Primary outcome"],rows,[2.25,5.5,4.15],12)
textbox(s,0.9,6.42,11.45,0.34,"Publish intent-level deduplication, splits, attack budget, decoding, and judge rubric before test-time runs.",13,TEAL,True)

s=base("Report a results card for every method, not a winner list", "Reporting standard", "Recommended synthesis; scores below must remain attached to the cited paper protocol")
rows=[
["Training","Base checkpoint, train data size/domains, objective, trainable parameters, steps, compute"],
["Threat model","Black/white box, image/text control, attack family, adaptive budget, held-out status"],
["Judge","Classifier/model/human rubric, threshold, audit sample, agreement, refusal-string caveat"],
["Safety","Harmful-compliance rate per family/domain with confidence interval"],
["Calibration + utility","False-refusal rate on matched safe pairs; VQA/OCR before and after"],
["System cost","Latency, extra calls/tokens, peak memory, training GPU-hours, artifact availability"]]
table(s,0.82,1.85,11.72,4.65,["Report field","Minimum information"],rows,[2.6,9.12],14)
textbox(s,0.95,6.62,11.35,0.28,"No cross-paper numerical ranking unless data, targets, attack budgets, decoding, and judging are harmonized.",12,CORAL,True)

IEEE_REFS = [
    '[1] Y. Gong et al., "FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts," arXiv:2311.05608, 2023.',
    '[2] X. Liu et al., "MM-SafetyBench: A Benchmark for Safety Evaluation of Multimodal Large Language Models," arXiv:2311.17600, 2023; accepted to ECCV 2024.',
    '[3] Y. Li et al., "Images are Achilles’ Heel of Alignment: Exploiting Visual Vulnerabilities for Jailbreaking Multimodal Large Language Models," arXiv:2403.09792, 2024.',
    '[4] W. Luo et al., "JailBreakV: A Benchmark for Assessing the Robustness of Multimodal Large Language Models against Jailbreak Attacks," arXiv:2404.03027, 2024.',
    '[5] Y. Zong et al., "Safety Fine-Tuning at (Almost) No Cost: A Baseline for Vision Large Language Models," arXiv:2402.02207, 2024.',
    '[6] Z. Liu et al., "Safety Alignment for Vision Language Models," arXiv:2405.13581, 2024.',
    '[7] Y. Zhang et al., "SPA-VL: A Comprehensive Safety Preference Alignment Dataset for Vision-Language Models," in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2025.',
    '[8] Q. Liu et al., "Unraveling and Mitigating Safety Alignment Degradation of Vision-Language Models," in Findings Assoc. Comput. Linguistics: ACL, pp. 3631–3643, 2025, doi: 10.18653/v1/2025.findings-acl.186.',
    '[9] X. Hu et al., "VLSBench: Unveiling Visual Leakage in Multimodal Safety," in Proc. 63rd Annu. Meeting Assoc. Comput. Linguistics (ACL), pp. 8285–8316, 2025, doi: 10.18653/v1/2025.acl-long.405.',
    '[10] J. Geng et al., "VSCBench: Bridging the Gap in Vision-Language Model Safety Calibration," in Findings Assoc. Comput. Linguistics: ACL, pp. 3047–3059, 2025, doi: 10.18653/v1/2025.findings-acl.158.',
    '[11] S. Wang et al., "Safe Inputs but Unsafe Output: Benchmarking Cross-modality Safety Alignment of Large Vision-Language Models," in Findings Assoc. Comput. Linguistics: NAACL, pp. 3563–3605, 2025, doi: 10.18653/v1/2025.findings-naacl.198.',
    '[12] F. Weng et al., "Adversary-Aware DPO: Enhancing Safety Alignment in Vision Language Models via Adversarial Training," in Findings Assoc. Comput. Linguistics: EMNLP, pp. 13644–13657, 2025, doi: 10.18653/v1/2025.findings-emnlp.735.',
    '[13] X. Lou et al., "Think in Safety: Unveiling and Mitigating Safety Alignment Collapse in Multimodal Large Reasoning Model," in Proc. Conf. Empirical Methods Natural Language Process. (EMNLP), pp. 5167–5186, 2025.',
    '[14] D. Lee et al., "Are Vision-Language Models Safe in the Wild? A Meme-Based Benchmark Study," in Proc. Conf. Empirical Methods Natural Language Process. (EMNLP), pp. 30545–30588, 2025, doi: 10.18653/v1/2025.emnlp-main.1555.',
    '[15] M. Chen et al., "VLMGuard-R1: Proactive Safety Alignment for VLMs via Reasoning-Driven Prompt Optimization," in Findings Assoc. Comput. Linguistics: ACL, pp. 39914–39932, 2026, doi: 10.18653/v1/2026.findings-acl.1986.',
    '[16] Q. Yang et al., "Visual Self-Fulfilling Alignment: Shaping Safety-Oriented Personas via Threat-Related Images," in Proc. 64th Annu. Meeting Assoc. Comput. Linguistics (ACL), pp. 10698–10718, 2026, doi: 10.18653/v1/2026.acl-long.490.',
    '[17] B. Zheng et al., "USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models," in Proc. 64th Annu. Meeting Assoc. Comput. Linguistics (ACL), pp. 21184–21211, 2026, doi: 10.18653/v1/2026.acl-long.970.',
    '[18] T. Wang et al., "MMJailBench: A Factorized Benchmark for Disentangling Multimodal Jailbreak Vulnerabilities," arXiv:2608.25490, 2026 (preprint).',
    '[19] X. Wang et al., "PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs," arXiv:2510.17277, 2025 (preprint).',
    '[20] J. Song et al., "JailBound: Jailbreaking Internal Safety Boundaries of Vision-Language Models," in Adv. Neural Inf. Process. Syst. (NeurIPS), 2025, doi: 10.52202/085713-0875.',
    '[21] X. Zhu et al., "GuardAlign: Test-Time Safety Alignment in Multimodal Large Language Models," in Proc. Int. Conf. Learn. Represent. (ICLR), 2026.',
    '[22] X. Zeng et al., "SafeSteer: A Decoding-Level Defense Mechanism for Multimodal Large Language Models," in Findings Assoc. Comput. Linguistics: ACL, 2026.',
    '[23] C. Ma et al., "SafeRI: Recognition and Intervention for Token-Level Safety Intervention in Large Vision Language Models," arXiv:2609.03544, 2026 (preprint).',
    '[24] P. Tang et al., "SafetyReminder: Reviving Delayed Safety Awareness of Vision-Language Models to Defend Against Jailbreak Attacks," in Proc. AAAI Conf. Artif. Intell., vol. 40, no. 39, pp. 33223–33231, 2026, doi: 10.1609/aaai.v40i39.40607.',
    '[25] S. Zhang et al., "MMAligner: Safeguarding Multimodal Large Language Models through Representation Calibration," arXiv:2608.05909, 2026 (preprint).',
    '[26] T. Bach et al., "Continual Safety Alignment via Gradient-Based Sample Selection," arXiv:2604.17215, 2026. LLM-only; project-history context, not VLM evidence.'
]

def add_reference_page(title, first, last):
    s = base(title, "IEEE references", "Full citation metadata; numbered entries correspond to in-slide citations")
    items = IEEE_REFS[first - 1:last]
    split = (len(items) + 1) // 2
    textbox(s,0.78,1.75,5.78,5.12,"\n\n".join(items[:split]),11.2,INK)
    textbox(s,6.83,1.75,5.78,5.12,"\n\n".join(items[split:]),11.2,INK)

add_reference_page("References [1]–[9]", 1, 9)
add_reference_page("References [10]–[18]", 10, 18)
add_reference_page("References [19]–[26]", 19, 26)

def attach_speaker_notes():
    source = Path("presentation/VLM_Safety_Alignment_Speaker_Notes.md").read_text()
    headings = list(re.finditer(r"^(?:##|###) Slide (\d+) —[^\n]*\n", source, re.M))
    notes = {}
    for i, match in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(source)
        body = source[match.end():end].strip()
        body = re.sub(r"\n\*\*Appendix sources:\*\*.*$", "", body, flags=re.S).strip()
        body = re.sub(r"\*\*(.*?)\*\*", r"\1", body)
        body = re.sub(r"`([^`]+)`", r"\1", body)
        notes[int(match.group(1))] = body
    for i, slide in enumerate(prs.slides, 1):
        text = notes.get(i, "Reference slide. Use this page to locate the cited source; paper findings and proposed study design are kept distinct.")
        if i in CITATIONS:
            text += "\n\nCitations on slide: " + ", ".join(f"[{n}]" for n in CITATIONS[i])
        slide.notes_slide.notes_text_frame.text = text

attach_speaker_notes()

prs.save(OUT)
prs.save(SECONDARY_OUT)
print(f"wrote {OUT} and {SECONDARY_OUT} ({len(prs.slides)} slides)")
