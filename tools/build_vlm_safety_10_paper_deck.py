from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt


OUT = Path(__file__).resolve().parents[1] / "VLM_Safety_Alignment_10_Paper_Proposal.pptx"
if OUT.exists():
    raise SystemExit(
        f"Refusing to overwrite the saved presentation at {OUT}. "
        "Use update_vlm_short_deck_system_diagram.py for the in-place diagram update."
    )
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

NAVY = RGBColor(35, 35, 35)
INK = RGBColor(45, 45, 45)
ACCENT = RGBColor(75, 75, 75)
TEAL = GREEN = RUST = GOLD = ACCENT
MUTED = RGBColor(105, 105, 105)
PALE = RGBColor(255, 255, 255)
LINE = RGBColor(220, 220, 220)
TABLE_GRID = "000000"
TABLE_HEADER = RGBColor(242, 242, 242)
WHITE = RGBColor(255, 255, 255)


def text(slide, x, y, w, h, value, size=18, color=INK, bold=False,
         align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, font="Aptos"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(0.03)
    tf.margin_right = Inches(0.03)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = value
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return box


def notes(slide, value):
    slide.notes_slide.notes_text_frame.text = value


def base(title, section, refs=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = WHITE
    text(slide, .62, .27, 4.3, .25, section.upper(), 9, TEAL, True)
    text(slide, .62, .62, 12.0, .6, title, 25, NAVY, True)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.62), Inches(1.36), Inches(12.05), Inches(.018))
    bar.fill.solid(); bar.fill.fore_color.rgb = LINE; bar.line.fill.background()
    text(slide, .62, 7.1, 11.8, .2, refs, 8, MUTED)
    text(slide, 12.12, 7.08, .48, .22, f"{len(prs.slides):02d}", 9, MUTED, align=PP_ALIGN.RIGHT)
    return slide


def card(slide, x, y, w, h, heading, body, accent=TEAL, fs=15):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = PALE
    shape.line.color.rgb = LINE
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(.07), Inches(h))
    strip.fill.solid(); strip.fill.fore_color.rgb = accent; strip.line.fill.background()
    text(slide, x+.2, y+.15, w-.38, .34, heading, 15, accent, True)
    text(slide, x+.2, y+.58, w-.38, h-.68, body, fs, INK)


def table(slide, x, y, w, h, headers, rows, col_widths, fs=13):
    sh = slide.shapes.add_table(len(rows)+1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h))
    t = sh.table
    for i, width in enumerate(col_widths):
        t.columns[i].width = Inches(width)
    for ri in range(len(rows)+1):
        for ci in range(len(headers)):
            cell = t.cell(ri, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = TABLE_HEADER if ri == 0 else WHITE
            cell.margin_left = Inches(.08); cell.margin_right = Inches(.06)
            cell.margin_top = Inches(.04); cell.margin_bottom = Inches(.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.text = headers[ci] if ri == 0 else rows[ri-1][ci]
            tc_pr = cell._tc.get_or_add_tcPr()
            for side in ("L", "R", "T", "B"):
                tag = qn(f"a:ln{side}")
                for old_line in list(tc_pr):
                    if old_line.tag == tag:
                        tc_pr.remove(old_line)
                line = OxmlElement(f"a:ln{side}")
                line.set("w", "12700")
                solid = OxmlElement("a:solidFill")
                rgb = OxmlElement("a:srgbClr")
                rgb.set("val", TABLE_GRID)
                solid.append(rgb)
                line.append(solid)
                dash = OxmlElement("a:prstDash")
                dash.set("val", "solid")
                line.append(dash)
                tc_pr.append(line)
            for p in cell.text_frame.paragraphs:
                p.space_after = Pt(0)
                for run in p.runs:
                    run.font.name = "Aptos"
                    run.font.size = Pt(fs-1 if ri == 0 else fs)
                    run.font.bold = ri == 0 or ci == 0
                    run.font.color.rgb = INK
    grid_width = Pt(1.1)
    x_cursor = x
    for width in col_widths[:-1]:
        x_cursor += width
        edge = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(x_cursor), Inches(y), Inches(x_cursor), Inches(y + h),
        )
        edge.line.color.rgb = RGBColor(0, 0, 0)
        edge.line.width = grid_width
    y_cursor = y
    row_height = h / (len(rows) + 1)
    for _ in range(len(rows)):
        y_cursor += row_height
        edge = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(x), Inches(y_cursor), Inches(x + w), Inches(y_cursor),
        )
        edge.line.color.rgb = RGBColor(0, 0, 0)
        edge.line.width = grid_width
    for x1, y1, x2, y2 in ((x, y, x + w, y), (x, y + h, x + w, y + h),
                          (x, y, x, y + h), (x + w, y, x + w, y + h)):
        edge = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(x1), Inches(y1), Inches(x2), Inches(y2),
        )
        edge.line.color.rgb = RGBColor(0, 0, 0)
        edge.line.width = grid_width
    return sh


def bullet_list(slide, items, x=.9, y=1.8, width=11.6, gap=.86, fs=18):
    colors = [TEAL, GREEN, RUST, GOLD]
    for i, item in enumerate(items):
        yy = y + i * gap
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(yy+.11), Inches(.11), Inches(.11))
        dot.fill.solid(); dot.fill.fore_color.rgb = colors[i % len(colors)]; dot.line.fill.background()
        text(slide, x+.25, yy, width-.25, gap-.05, item, fs, INK)


def add_ref_slide(title, entries, refs):
    s = base(title, "References", refs)
    step = 5.25 / len(entries)
    font_size = 11 if len(entries) > 4 else 12
    for entry in entries:
        text(s, .85, 1.58 + entries.index(entry) * step, 11.65, step-.08, entry, font_size, INK)
    return s


# 1. Title
s = prs.slides.add_slide(prs.slide_layouts[6])
s.background.fill.solid(); s.background.fill.fore_color.rgb = WHITE
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(3.7))
band.fill.solid(); band.fill.fore_color.rgb = WHITE; band.line.fill.background()
text(s, .85, .82, 4.5, .28, "LITERATURE REVIEW", 11, ACCENT, True)
text(s, .85, 1.3, 11.6, 1.35, "Safety Alignment for\nVision-Language Models", 32, NAVY, True)
text(s, .9, 4.22, 11.4, .7, "A ten-paper route from prior evidence to a controlled evaluation protocol", 20, INK)
text(s, .9, 5.35, 11.4, .66, "Focused preliminary review • broader literature audit continues • 30 September 2026", 13, MUTED)
text(s, .9, 6.85, 11.4, .25, "Proposal, not a claim that the literature has validated one combined system", 10, TEAL, True)
notes(s, "Opening: We narrowed this presentation to ten representative papers so we can explain the evidence and evaluation design clearly. This is not the final systematic review and does not imply that all ten methods have been combined or compared under one protocol. The broader paper audit continues. Our aim today is to formulate a defensible research question, identify the key prior work, and propose a reproducible test.")

# 2. Scope and question
s = base("The question: robust safety without blanket refusal", "Research question", "Evidence base: [1]–[10]")
card(s, .85, 1.75, 3.75, 2.35, "HARM PREVENTION", "Resist unsafe requests carried by text, image text, visual semantics, or their combination.", RUST, 17)
card(s, 4.8, 1.75, 3.75, 2.35, "BENIGN ANSWERABILITY", "Continue answering safe requests, including near-neighbors that resemble risky cases.", GREEN, 17)
card(s, 8.75, 1.75, 3.75, 2.35, "VISUAL GROUNDING", "Make the safety decision depend on relevant image evidence, not only leaked text cues.", TEAL, 17)
text(s, 1.02, 4.65, 10.9, .35, "Research question", 15, TEAL, True)
text(s, 1.02, 5.05, 11.1, 1.0, "For a fixed open-weight VLM and matched data budget, which alignment intervention improves held-out visual/cross-modal attack resistance while preserving safe answer quality and image grounding?", 22, NAVY, True)
notes(s, "Define safety behavior as more than refusal. Our outcome has three parts: prevent materially harmful assistance, retain useful answers to benign requests, and demonstrate that judgments respond appropriately to the image. The experiment will compare interventions under a shared evaluation setup; it will not claim a universal best method across incomparable papers.")

# 3. VLM-specific failure model
s = base("Four input pathways create distinct failure modes", "Problem framing", "FigStep [1]; HoliSafe [8]; VLSBench [2]")
table(s, .85, 1.78, 11.65, 3.95,
      ["Carrier / composition", "Example test condition", "What it probes"],
      [["Text instruction", "Unsafe request in ordinary text", "Inherited language safety"],
       ["Text inside image", "Harmful instruction rendered as typography", "OCR / visual-text pathway"],
       ["Visual semantics", "Image depicts a risky object, act, or context", "Visual safety representation"],
       ["Cross-modal composition", "Individually safe-looking image + text; unsafe joint intent", "Joint interpretation and grounding"]],
      [2.55, 4.65, 4.45], 15)
text(s, .9, 6.0, 11.6, .62, "Evaluate each pathway separately; a single pooled ASR can hide which modality is failing.", 17, RUST, True)
notes(s, "These categories motivate stratified evaluation. FigStep is a concrete image-carried typography attack. HoliSafe explicitly covers five combinations of image and text safety, including safe-looking components that produce an unsafe joint request. VLSBench adds an evaluation-validity concern: if the text already reveals the risky content, success may not require visual understanding.")

# 4. Ten-paper evidence map
s = base("Ten papers, four jobs in the proposed study", "Literature Review", "[1] FigStep; [2] VLSBench; [3] USB; [4] PolyJailbreak; [5] VLGuard; [6] SPA-VL; [7] ADPO; [8] HoliSafe; [9] DAVSP; [10] Pragma-VL")
table(s, .8, 1.65, 11.8, 4.8,
      ["Job", "Papers", "How we use them"],
      [["Attack construction", "FigStep; PolyJailbreak", "Fixed OCR test and separately budgeted adaptive black-box tier"],
       ["Benchmark validity / coverage", "VLSBench; USB", "Leakage controls, modality strata, over-refusal reporting"],
       ["Training / preference baselines", "VLGuard; SPA-VL; ADPO", "Safety SFT, standard preference tuning, adversarial preference tuning"],
       ["Recent alignment comparators", "HoliSafe; DAVSP; Pragma-VL", "Visual guard, safety prompt, safety-helpfulness arbitration"]],
      [2.2, 3.1, 6.5], 14)
notes(s, "This table is the narrative spine. These papers have different jobs and should not be forced into one category. VLGuard is a data and safety-SFT precedent; SPA-VL provides preference data and experiments; ADPO is the direct adversarial preference-training precedent. HoliSafe combines benchmark/data and a visual guard. DAVSP and Pragma-VL represent distinct recent alignment approaches. The attack and benchmark papers define evaluation, not the intervention itself.")

# 5. Benchmarks data overview
s = base("What the core test resources actually cover", "Datasets and benchmarks", "Source counts: VLSBench [2], USB [3], VLGuard [5], SPA-VL [6], HoliSafe [8]")
table(s, .75, 1.62, 11.9, 4.95,
      ["Resource", "Scale / structure", "Use and caution"],
      [["VLGuard", "2,000 train images; ~3,000 pairs; 1,000 test images", "Safety-SFT baseline; include benign-helpfulness controls"],
       ["SPA-VL", "100,788 preference records; 6 domains; 53 subcategories", "Category count differs in abstract vs. §3.1; verify before quoting"],
       ["HoliSafe", "14,246 pairs; 10,215 train; 4,031 test QA on 1,796 images", "Five input/outcome states; benchmark plus visual guard"],
       ["VLSBench", "2,241 pairs; 1,957 images; 6 categories / 19 subcategories", "Leakless visual-safety test and image-ablation controls"],
       ["USB", "13,175 Base + 3,785 Hard; 61 categories × 4 modality combos", "Broad coverage; preserve stratum and SR/RR definitions"]],
      [1.65, 4.3, 5.95], 12)
notes(s, "Dataset size is not a safety result. For each resource, inspect split construction, label semantics, and benchmark leakage. SPA-VL is a preference dataset: each example has a question, image, chosen response, and rejected response. DPO is an optimization method that trains on such pairs; the dataset and optimizer are separate. Source-count audit: the SPA-VL abstract says 13 categories while §3.1 says 15 secondary categories; do not present one count as settled without checking the camera-ready source. HoliSafe is direct prior art for a five-state setup, so we must not claim that taxonomy as new. Its final publication is CVPR Findings 2026; verify any arXiv-selected value against the final proceedings version before formal reuse.")

# 6. Verified results with metrics
s = base("Selected results: read each value in its own metric", "Evidence snapshots", "FigStep Table 1 [1]; VLSBench Table 4 [2]; ADPO Table 1 [7]; HoliSafe Table 3 [8]")
table(s, .72, 1.62, 11.95, 4.72,
      ["Paper/table", "Reported comparison", "Metric and interpretation"],
      [["FigStep, Table 1", "82.50% FigStep vs 44.80% vanilla harmful text", "Mean ASR across six evaluated open VLMs; lower is safer"],
       ["VLSBench, Fig. 1", "LLaVA-1.5-7B: 6.6 base; 21.3 MM-SFT; 27.0 MM-DPO", "Safety rate; higher is safer. Not ASR."],
       ["ADPO, Table 1", "LLaVA ASR on VisualAdv: 64.5 base / 12.0 DPO / 5.0 ADPO", "Attack-specific ASR; lower is safer. Other columns are separate attacks."],
       ["HoliSafe, Table 3", "SafeLLaVA-7B mASR: 8.8 Claude / 15.3 GPT-4o / 15.8 Gemini", "Judge-dependent mASR; safe-pair RR with Claude: 1.3%"]],
      [2.05, 5.1, 4.8], 13)
text(s, .85, 6.48, 11.6, .38, "These are not a cross-paper leaderboard: datasets, checkpoints, judges, and metric directions differ.", 12, RUST, True)
notes(s, "These selected values are transcribed from the named paper table or figure and are included only to illustrate what each work measures. FigStep reports average ASR across its historical six-model set. VLSBench reports safety rate, where higher is better; do not call it ASR. ADPO's 5.0 is one attack column for one model, not an aggregate. HoliSafe reports different mASR values under different judges, making judge identity essential. The HoliSafe cells were checked against the revised arXiv v5 in the prior audit; the final CVPR Findings 2026 version must be checked before treating them as final. We do not rank these numbers across papers.")

# 7. Methods
s = base("Alignment methods make different commitments", "Method comparison", "VLGuard [5]; SPA-VL [6]; ADPO [7]; HoliSafe [8]; DAVSP [9]; Pragma-VL [10]")
table(s, .8, 1.7, 11.75, 4.85,
      ["Method family", "Representative work", "Core intervention", "Key question for our audit"],
      [["Safety SFT", "VLGuard", "Tune on image-conditioned safe/unsafe responses", "Does benign answerability survive?"],
       ["Preference tuning", "SPA-VL", "Optimize chosen vs rejected multimodal responses", "What are pair source and DPO recipe?"],
       ["Adversarial preference", "ADPO", "Train reference/preferences with adversarial perturbations", "Do gains transfer to held-out attack families?"],
       ["Visual guard", "HoliSafe", "Classify visual harmfulness and guide generation", "What are judge/false-refusal tradeoffs?"],
       ["Prompt / arbitration", "DAVSP; Pragma-VL", "Visual safety prompt or dynamic safety-helpfulness objective", "What are cost, units, and deployment assumptions?"]],
      [2.15, 2.25, 4.4, 2.95], 12)
notes(s, "A useful conceptual distinction: SFT teaches from labeled examples; preference optimization learns a relative preference from chosen/rejected responses. DPO is one such optimization method, not a dataset. ADPO adds adversarial training to that preference process. HoliSafe's visual guard is a modular visual classification component. DAVSP is a visual safety prompt/activation alignment approach; Pragma-VL frames safety and helpfulness arbitration. These are candidate arms or comparators, not components we assume should be stacked together.")

# 8. Attack suite
s = base("Separate attack methods from evaluation controls", "Adversarial evaluation", "FigStep [1]; HADES [11]; JailBreakV [12]; PolyJailbreak [4]; SIUO [13]; VLSBench [2]; USB [3]")
table(s, .78, 1.65, 11.8, 4.85,
      ["Role", "Resource / method", "What it tests; what it is not"],
      [["Fixed attack", "FigStep: typographic image-carried request", "Attack method; OCR/visual-text route"],
       ["Fixed attack", "HADES: typography plus semantically matched image", "Black-box semantic visual exploit; keep +Opt distinct from white-box +Adv"],
       ["Attack collection", "JailBreakV-28K transfer and image-based cases", "Many fixed attack instances; not one attack algorithm"],
       ["Adaptive attack", "PolyJailbreak black-box search", "Separate query-budget curve; not pooled with static ASR"],
       ["Evaluation controls", "SIUO, VLSBench, USB, safe pairs", "Compositionality, image dependence, coverage, calibration; not attacks"]],
      [1.7, 4.45, 5.65], 12)
notes(s, "The earlier framing mixed attack procedures with datasets and controls, so this slide now separates them. FigStep and HADES are attack constructions; JailBreakV packages many transfer/image-based cases; PolyJailbreak is an adaptive black-box method. SIUO, VLSBench, USB, and safe-neighbor sets are evaluation resources, not attack algorithms. HADES has distinct typographic-only, black-box optimized-image, and white-box adversarial-image conditions; report these separately. The next two slides specify the proposed run protocol. No harmful payload examples are shown.")

# 9. Fixed attack construction and run controls
s = base("Fixed attack procedure: build matched, locked test cases", "Proposed attack protocol", "FigStep [1]; HADES [11]; JailBreakV-28K [12]; design choices are proposed, not paper results")
table(s, .75, 1.62, 11.9, 4.95,
      ["Step", "Pre-registered operation", "Record / control"],
      [["1. Freeze source intent", "Assign each approved test intent an ID; label policy category and safe counterpart", "Source, license, label, annotator/adjudication"],
       ["2. Split before transforms", "Group by intent; reserve test intents and held-out render templates/families", "Seeded manifest; near-duplicate and image hash audit"],
       ["3. Construct fixed arms", "A0 text control; A1 FigStep-style rendered image; A2 HADES +Opt artifact", "One case per transform; never use victim output to tune fixed attacks"],
       ["4. Add attribution controls", "Run text-only, image-only where valid, original image, removed/masked/decoy image", "Same intent and wording; only the named modality changes"],
       ["5. Query frozen models", "Same system prompt, processor, decoding, and 256-token cap; one query/item", "Proposed deterministic setting; pin checkpoint and software revisions"]],
      [1.55, 6.0, 4.35], 11.2)
text(s, .9, 6.68, 11.5, .28, "Keep HADES +Opt (black-box) and +Adv (white-box) in separate result tables.", 12, ACCENT, True)
notes(s, "This is our proposed common protocol, not a claim that the source papers used identical settings. Split source intents before creating typography or image variants so transformed duplicates cannot cross train/test. A0 is the matched text control; A1 instantiates FigStep; A2 uses HADES's black-box typography-plus-optimized-image condition when released artifacts and license permit. If recreating images, freeze prompts and generation settings without consulting the target model. HADES +Adv uses white-box access and must be an optional separate tier. Freeze target checkpoint, image processor, system prompt, deterministic decoding, and the proposed 256 new-token ceiling. The protocol specification records all manifest fields and decision gates.")

# 10. Adaptive attack and scoring protocol
s = base("Adaptive red team: equal query budget, audited success", "Proposed attack protocol", "PolyJailbreak [4]; ADPO [7]; proposed cap and outcome definitions")
table(s, .75, 1.62, 11.9, 4.9,
      ["Protocol item", "Pre-registered rule"],
      [["Adaptive budget", "Per intent × target: up to 5 discovery calls + 15 optimization calls = 20 target calls; stop on first adjudicated success"],
       ["Paper-vs-proposal label", "PolyJailbreak reports T_max=15 optimization steps; our additional 5-call discovery allowance is a proposed cap, not its native setting"],
       ["Primary endpoint", "Semantic harmful-compliance rate by attack family; success requires materially enabling prohibited intent, not keyword match"],
       ["Calibration and utility", "False-refusal rate and answer quality on matched safe near-neighbors; VQA/OCR and image-ablation grounding reported separately"],
       ["Judge and uncertainty", "Freeze judge/model version and rubric; blind arm labels; human-adjudicate stratified ambiguous/disagreement sample; paired intent-cluster bootstrap CIs"],
       ["Audit trail", "Save all query counts, stop reason, seed, hashes, judge outputs, latency/cost, and versioned artifacts; do not publish harmful outputs"]],
      [2.45, 9.45], 12)
notes(s, "Run the adaptive attacker independently against each frozen target under the same 20-call ceiling. The 5 discovery plus 15 optimization split is our proposed operational budget; the PolyJailbreak paper's reported T_max=15 refers to optimization steps and must not be mislabeled as 20. Stop after the first success for the primary per-intent endpoint, but preserve every attempt so we can plot cumulative success against query count. Use a semantic rubric and a frozen judge, blind the model condition, and human-review a stratified sample. Report per-family results, safe false refusals, grounding, capability, and cost separately. Bootstrap over source intent, not individual transformed images. Keep any white-box pixel attack outside this black-box result.")

# 11. Final proposed system design
s = base("Proposed end-to-end study design", "System design", "Evidence sources [1]–[10]; proposed study protocol, not a combined prior method")

def stage(x, w, heading, body, h=3.55):
    y = 1.78
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = WHITE
    sh.line.color.rgb = RGBColor(0, 0, 0); sh.line.width = Pt(1.25)
    head = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(.56))
    head.fill.solid(); head.fill.fore_color.rgb = TABLE_HEADER
    head.line.color.rgb = RGBColor(0, 0, 0); head.line.width = Pt(1.0)
    text(s, x+.09, y+.08, w-.18, .38, heading, 13, NAVY, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    text(s, x+.14, y+.72, w-.28, h-.84, body, 11.5, INK)
    return (x, y, w, h)

stages = [
    stage(.68, 2.05, "1 | EVIDENCE + DATA", "VLGuard: safety examples\nSPA-VL: chosen/rejected pairs\nHoliSafe: image/text risk cases\nVLSBench + USB: eval design\n\nTrack source, license, image, intent, label, and safe counterpart. [2,3,5,6,8]"),
    stage(2.92, 2.18, "2 | LABEL + SPLIT", "Annotate image, text, and joint intent.\n\nSplit by source intent BEFORE paraphrase, typography, image generation, or attack transforms.\n\nTrain / validation / locked test; deduplicate images and near-duplicate intents."),
    stage(5.30, 2.55, "3 | INDEPENDENT ARMS", "B0 Native checkpoint\nB1 Text-only safety SFT\nB2 Multimodal safety SFT (VLGuard)\nB3 Standard preference tuning (SPA-VL)\nB4 ADPO-style (if reproducible)\n\nAdd at most ONE feasible comparator: HoliSafe VGM, DAVSP, or Pragma-VL. Never stack by default. [5–10]"),
    stage(8.04, 2.57, "4 | LOCKED TEST", "ATTACKS\nFixed: FigStep-style typography [1]\nAdaptive: PolyJailbreak-style [4]\n\nEVALUATION + CONTROLS\nVLSBench / USB / HoliSafe strata [2,3,8]\nSafe near-neighbors; image removed, masked, or decoy controls\n\nSame pinned inference settings for every arm."),
    stage(10.80, 1.86, "5 | SCORE + REPORT", "Safety: harmful compliance / ASR\nCalibration: benign false refusal\nHelpfulness: safe-answer quality\nGrounding: image dependence\nCapability: VQA / OCR\nCost: calls, latency, compute\n\nPaired by intent; uncertainty + human audit."),
]

for left, right in zip(stages, stages[1:]):
    x1 = left[0] + left[2] + .015
    x2 = right[0] - .015
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(3.55), Inches(x2), Inches(3.55))
    c.line.color.rgb = RGBColor(0, 0, 0); c.line.width = Pt(1.5)
    c.line.end_arrowhead = True

text(s, .82, 5.62, 11.65, .42, "Locked test intents never enter training. Attacks are procedures; benchmarks are test sets; ablations establish image dependence.", 13, INK, True, align=PP_ALIGN.CENTER)
text(s, .82, 6.13, 11.65, .42, "Compare each intervention separately; preserve metric direction, judge/version, and the paper-native vs. proposed query budget.", 12, MUTED, align=PP_ALIGN.CENTER)
notes(s, "This is the final recommended research system diagram, synthesized from the ten reviewed papers; it is not claimed as a system already evaluated by any one paper. Stage 1 separates data/method sources from evaluation sources. Stage 2 is the key anti-leakage boundary: split at the source-intent level before making rendered text, paraphrases, synthetic images, or attack variants. Stage 3 contains independent experimental arms. The core comparison is native, text-only safety SFT, multimodal safety SFT, and standard preference tuning; ADPO requires faithful reproduction, and only one of HoliSafe VGM, DAVSP, or Pragma-VL should be added after a feasibility check. Stage 4 uses the same locked test cases for every arm, separates fixed FigStep-style from adaptive PolyJailbreak-style attacks, and includes VLSBench/USB/HoliSafe coverage plus benign and image-ablation controls. Stage 5 reports safety, benign false refusal, safe-answer quality, image grounding, general capability, and cost independently with paired intent-level uncertainty. The proposed shared query budget must be labeled as ours: PolyJailbreak’s paper reports 15 optimization steps, which is not automatically the total API-call budget.")

# 12. Baseline ladder and metrics
s = base("Baseline ladder and outcome contract", "Experimental protocol", "Training precedent: [5]–[10]; evaluation precedent: [1]–[4]")
table(s, .75, 1.65, 6.0, 4.95,
      ["Arm", "Purpose"],
      [["B0 Native VLM", "Starting behavior"],
       ["B1 Text-only safety SFT", "Isolate language-only tuning"],
       ["B2 Multimodal safety SFT", "VLGuard-style baseline"],
       ["B3 Standard DPO", "Preference objective without adversary"],
       ["B4 ADPO-style", "Adversarial preference; if faithfully reproducible"],
       ["B5 One recent comparator", "HoliSafe, DAVSP, or Pragma-VL after feasibility check"]],
      [2.7, 3.3], 12)
table(s, 7.05, 1.65, 5.55, 4.95,
      ["Outcome", "Report"],
      [["Safety", "Semantic harmful-compliance / ASR by family"],
       ["Calibration", "Benign false refusal + safe-answer quality"],
       ["Grounding", "Original vs removed / masked / decoy image"],
       ["Capability", "Fixed VQA/OCR metrics, separate from safety"],
       ["Cost", "Training compute, latency, extra calls, memory"]],
      [1.55, 4.0], 12)
notes(s, "This ladder is intentionally feasible. Start with a native checkpoint, add text-only SFT, multimodal SFT, standard preference tuning, then ADPO only if the source code and recipe can be reproduced. Select one recent comparator after confirming its model and compute compatibility. Compare with same base checkpoint and matched data budget. Safety is not one scalar: include semantic safety, benign answerability, grounding controls, general capability, and cost.")

# 13. Hypothesis and challenges
s = base("The gap is in controlled transfer and attribution", "Hypothesis and challenges", "VLSBench [2]; ADPO [7]; HoliSafe [8]; USB [3]; PolyJailbreak [4]")
card(s, .85, 1.72, 5.65, 2.0, "H1 | IMAGE-CONDITIONED TRANSFER", "At matched data budget, multimodal alignment improves intent-held-out visual attack resistance over text-only safety tuning.", TEAL, 15)
card(s, 6.8, 1.72, 5.65, 2.0, "H2 | HELD-OUT MECHANISMS", "Adversarial preference training helps on trained attack families; family-held-out tests reveal transfer limits.", RUST, 15)
bullet_list(s, [
    "Leakage and attribution: did the model need the image?",
    "Metric incompatibility: ASR, RSR, safety rate, RR, judges, and units differ.",
    "Over-refusal and utility loss can make apparent safety gains misleading.",
    "Intent duplicates, judge disagreement, adaptive budgets, and model/version drift threaten reproducibility."
], x=.92, y=4.1, width=11.4, gap=.56, fs=14)
notes(s, "State the hypotheses as falsifiable predictions, not conclusions. H1 compares text-only with image-conditioned alignment at a controlled budget. H2 predicts the value and limitation of adversarial preference training under attack-family holdout. The key challenges are attribution, incompatible metrics, over-refusal, data leakage, evaluator disagreement, and changing attack/model versions. We propose paired tests and confidence intervals, plus human review of a sample of judge decisions.")

# 14. Scope/timeline
s = base("A responsible proposal has a bounded first experiment", "Study plan", "Focused paper route: docs/VLM_10_PAPER_READING_CHECKLIST.md")
table(s, .95, 1.75, 11.45, 4.5,
      ["Stage", "Deliverable", "Decision gate"],
      [["1. Paper audit", "Extract protocol, exact tables, and metrics for 10 papers", "Lock candidate methods and benchmark versions"],
       ["2. Feasibility", "Choose one open checkpoint; test artifact access and data licenses", "If ADPO/recent method is not reproducible, document exclusion"],
       ["3. Protocol freeze", "Intent-level split, attack tiers, judges, endpoints, compute budget", "Preregister before training"],
       ["4. Run + analyze", "Baseline ladder, repeated seeds, per-family safety/utility/grounding", "Report negative results and uncertainty"],
       ["5. Expand review", "Add remaining literature and adaptive/white-box tiers", "Do not claim comprehensive SOTA until audit closes"]],
      [2.0, 5.15, 4.3], 14)
text(s, 1.0, 6.48, 11.2, .35, "Today’s claim: a literature-grounded research plan, not a completed system or final leaderboard.", 13, TEAL, True)
notes(s, "This is the appropriate claim for a proposal presentation. First complete the focused primary-paper reading and table extraction. Then choose a model and baselines based on released artifacts and compute. Freeze dataset versions, splits, attack budget, and metrics before running. The full 29-paper audit remains a later workstream; this shorter selection is not presented as a comprehensive SOTA review.")

# 15-16. References
add_ref_slide("References | Attacks and evaluation", [
    "[1] Y. Gong et al., “FigStep: Jailbreaking Large Vision-Language Models via Typographic Visual Prompts,” arXiv:2311.05608, 2023; AAAI 2025 Oral. https://arxiv.org/abs/2311.05608",
    "[2] X. Hu, D. Liu, H. Li, X. Huang, and J. Shao, “VLSBench: Unveiling Visual Leakage in Multimodal Safety,” in Proc. ACL, 2025, pp. 8285–8316, doi: 10.18653/v1/2025.acl-long.405.",
    "[3] B. Zheng et al., “USB: A Comprehensive and Unified Safety Evaluation Benchmark for Multimodal Large Language Models,” in Proc. ACL, 2026, pp. 21184–21211, doi: 10.18653/v1/2026.acl-long.970.",
    "[4] X. Wang et al., “PolyJailbreak: Cross-Modal Jailbreaking Attacks on Black-Box Multimodal LLMs,” IEEE Trans. Dependable Secure Comput., 2026, doi: 10.1109/TDSC.2026.3707228.",
    "[11] Y. Li et al., “Images are Achilles’ Heel of Alignment: Exploiting Visual Vulnerabilities for Jailbreaking Multimodal Large Language Models,” in Proc. ECCV, 2024. https://arxiv.org/abs/2403.09792",
    "[12] W. Luo et al., “JailBreakV: A Benchmark for Assessing the Robustness of Multimodal Large Language Models against Jailbreak Attacks,” arXiv:2404.03027, 2024; COLM 2024.",
    "[13] S. Wang et al., “Safe Inputs but Unsafe Output: Benchmarking Cross-modality Safety Alignment of Large Vision-Language Models,” in Findings of NAACL, 2025, pp. 3563–3605, doi: 10.18653/v1/2025.findings-naacl.198."
], "Primary records [1]–[4], [11]–[13]")
notes(prs.slides[-1], "These citations are provided in compact IEEE style. PolyJailbreak is listed as the 2026 IEEE TDSC article; check its final journal version against the arXiv version before implementing the attack. USB is an ACL 2026 proceedings paper. Use the primary records for exact author lists and any final page/DOI corrections.")

add_ref_slide("References | Alignment methods", [
    "[5] Y. Zong, O. Bohdal, T. Yu, Y. Yang, and T. Hospedales, “Safety Fine-Tuning at (Almost) No Cost: A Baseline for Vision Large Language Models,” in Proc. ICML, PMLR, vol. 235, 2024.",
    "[6] Y. Zhang et al., “SPA-VL: A Comprehensive Safety Preference Alignment Dataset for Vision Language Models,” in Proc. IEEE/CVF CVPR, 2025, pp. 19867–19878.",
    "[7] F. Weng et al., “Adversary-Aware DPO: Enhancing Safety Alignment in Vision Language Models via Adversarial Training,” in Findings of EMNLP, 2025, pp. 13644–13657, doi: 10.18653/v1/2025.findings-emnlp.735.",
    "[8] Y. Lee et al., “HoliSafe: Holistic Safety Benchmarking and Modeling with Safety Meta Token for Vision-Language Model,” in Proc. IEEE/CVF CVPR Findings, 2026, pp. 5989–5998. arXiv:2506.04704.",
    "[9] Y. Zhang, J. Li, L. Cai, and G. Li, “DAVSP: Safety Alignment for Large Vision-Language Models via Deep Aligned Visual Safety Prompt,” in Proc. AAAI, vol. 40, no. 44, 2026, pp. 38111–38119, doi: 10.1609/aaai.v40i44.41149.",
    "[10] M. Wen, K. Yang, X. Chen, J. Zhang, D. Han, S. Cui, and Y. Xu, “Pragma-VL: Towards a Pragmatic Arbitration of Safety and Helpfulness in MLLMs,” in Proc. ICLR, 2026."
], "Primary records [5]–[10]")
notes(prs.slides[-1], "References 5 through 10. Several institutional pages offer full BibTeX and IEEE-style export; normalize all author lists and page ranges against the proceedings record before formal submission. The reading checklist links each primary paper and pinpoints the sections and tables to inspect. Use exact paper/table citations in any numeric claim.")

prs.save(OUT)
print(OUT)
