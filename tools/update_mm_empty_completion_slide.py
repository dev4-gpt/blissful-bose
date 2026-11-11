"""Update the existing weekly deck using verified aggregate counts only."""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import csv
import shutil

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / 'presentation/MM_SafetyBench_Today_2026-11-05.pptx'
BLUE, BLACK = '143054', '171717'
EMPTY_TITLE = 'What does an empty completion tell us?'


def text(shape, value, size=22, color=BLACK, bold=False):
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(0.03)
    frame.margin_top = frame.margin_bottom = Inches(0.02)
    for i, line in enumerate(value.split('\n')):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
        paragraph.text = line
        paragraph.font.name = 'Arial'
        paragraph.font.size = Pt(size)
        paragraph.font.bold = bold
        paragraph.font.color.rgb = RGBColor.from_string(color)
        paragraph.space_after = Pt(13)
    return shape


def box(slide, x, y, w, h, value, size=22, color=BLACK, bold=False):
    return text(slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)),
                value, size, color, bold)


def heading(slide, title, subtitle):
    text(slide.shapes[0], title, 27, BLUE, True)
    text(slide.shapes[1], subtitle, 16)


def update():
    original = DECK.read_bytes()
    with (ROOT / 'reports/activation_safety_baseline.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    full = [r for r in rows if r['cohort'] == 'full' and r['scope'] == 'ALL_13']
    for model, nonempty, safety, refusal, empty in (
        ('qwen25', 6720, 6549, 6603, 0),
        ('llava', 6720, 6414, 6478, 0),
        ('instructblip', 5922, 5773, 5782, 798),
    ):
        selected = [r for r in full if r['model'] == model]
        assert len(selected) == 4
        assert sum(int(r['planned']) for r in selected) == 6720
        assert sum(int(r['no_response']) for r in selected) == empty
        assert 6720 - empty == nonempty
        assert sum(int(r['safety_judged']) for r in selected) == safety
        assert sum(int(r['refusal_judged']) for r in selected) == refusal

    prs = Presentation(DECK)
    assert 8 <= len(prs.slides) <= 9
    snapshot = ROOT / 'audit_work/presentation_snapshots_PRIVATE' / datetime.now().strftime('%Y%m%dT%H%M%S')
    snapshot.mkdir(parents=True, exist_ok=False)
    shutil.copy2(DECK, snapshot / DECK.name)

    slide = prs.slides[3]
    heading(slide, 'Qwen2.5 now has all four input conditions',
            'Saved generation and GPT-4.1 evaluation completed on 8 November')
    text(slide.shapes[3],
         '1,680 underlying questions across 13 scenarios\n'
         '5,040 image cases = SD + typography + SD plus typography\n'
         '1,680 additional text-only cases\n'
         '6,720 unique nonempty answers saved across all four conditions', 25)
    text(slide.shapes[4], 'ASR and RR are saved separately, with judge filtering recorded.', 19)
    slide.notes_slide.notes_text_frame.text = (
        'The original image run produced three answers for each underlying benchmark question, '
        'one for each image condition. That accounts for 5,040 cases. The text-only run adds '
        'one answer per question, bringing this model to 6,720 unique cases. All are nonempty. '
        'We then evaluated the saved answers using Azure GPT-4.1, version 2025-04-14, with '
        'separate safety and refusal prompts. The safety pass resolved 6,549 labels and the '
        'refusal pass resolved 6,603 labels. The remaining requests were filtered. Those are '
        'evaluation outcomes, while an empty completion happens earlier at target-model generation. '
        'Qwen2.5-VL-3B is our checkpoint adaptation. The original paper used the earlier Qwen-VL. '
        'Our result therefore carries that model difference and the updated judge version.'
    )

    slide = prs.slides[4]
    heading(slide, 'All three generation runs have finished',
            '6,720 planned cases per model across all 13 scenarios and four conditions')
    slide.shapes[3].top = Inches(1.8)
    text(slide.shapes[3],
         'Qwen2.5-VL-3B    6,720 nonempty answers; 0 empty\n'
         'LLaVA-1.5-7B       6,720 nonempty answers; 0 empty\n'
         'InstructBLIP          5,922 nonempty answers; 798 empty\n'
         'All three have completed GPT-4.1 safety and refusal passes.\n'
         'Empty outputs and filtered judgments remain explicitly recorded.', 24)
    slide.notes_slide.notes_text_frame.text = (
        'Each generation run visited the full planned set of 6,720 cases. Qwen and LLaVA '
        'produced visible answer text for every case. InstructBLIP completed the case traversal '
        'but produced an empty decoded result on 798 cases. This leaves 5,922 nonempty answers '
        'for its two judging passes. Calling a run finished describes execution coverage. '
        'It does not imply that every case produced an answer or received a label. The six '
        'judging passes finished, and the answer ledgers, labels and aggregate reports were saved. '
        'An empty output alone cannot tell us whether the model failed to understand, stopped '
        'early, experienced a decoding problem or exhibited safety behavior. We report the '
        'observed output and leave that causal question unresolved.'
    )

    slide = prs.slides[6]
    slide.notes_slide.notes_text_frame.text = (
        'The benchmark release supplies processed questions, carrier images and evaluation rubrics. '
        'Our first stage checks their versions and fingerprints. The second stage constructs '
        'one case per question and condition, preserving the released prompt mapping. The third '
        'stage uses an inference adapter for each model to load its pretrained checkpoint, format '
        'the inputs, generate and decode. The fourth stage saves every outcome immediately with '
        'its case key and settings, including an explicit marker for empty decoded text. The '
        'fifth stage verifies coverage and sends nonempty answers to Azure GPT-4.1 with the '
        'separate safety and refusal rubrics. We have now completed those two passes for all '
        'three models. Filtered judgments and empty generations remain visible in coverage '
        'reports. We calculate ASR and RR separately because refusing language can coexist '
        'with harmful assistance. Our checkpoint choices, prompt-mapping discrepancies and '
        'updated judge are documented implementation differences.'
    )

    slide = prs.slides[7]
    heading(slide, 'GPT-4.1 judging and saved results',
            'Resolved labels from two separate passes over the nonempty answers')
    slide.shapes[3].top = Inches(1.85)
    text(slide.shapes[3],
         'Qwen2.5-VL-3B    6,549 safety labels; 6,603 refusal labels\n'
         'LLaVA-1.5-7B       6,414 safety labels; 6,478 refusal labels\n'
         'InstructBLIP          5,773 safety labels; 5,782 refusal labels\n'
         'ASR, RR and coverage are saved by scenario and condition.\n'
         '1,125 filtered metric outcomes; 798 empty InstructBLIP cases.', 24)
    slide.notes_slide.notes_text_frame.text = (
        'The safety and refusal rubrics each produce their own label. That is why a model '
        'can have different numbers of resolved labels in the two passes. Across all three '
        'models, Azure filtered 1,125 metric outcomes. A single answer can have one resolved '
        'metric and one filtered metric. Separately, InstructBLIP has 798 generation cases '
        'with no visible answer. Those cases were excluded from both judge inputs and retained '
        'in the planned-case denominator accounting. We report rates among judged answers, '
        'label coverage and lower and upper bounds across all planned cases. The bounds '
        'assign unresolved outcomes both possible labels and are sensitivity bounds, rather '
        'than confidence intervals. Full and released-tiny readouts are saved, with the tiny '
        'set selected from the same judgments. These observations describe the completed '
        'three-model panel and its measurement limits.'
    )

    existing = [s for s in prs.slides if s.shapes and s.shapes[0].has_text_frame
                and s.shapes[0].text == EMPTY_TITLE]
    slide = existing[0] if existing else prs.slides.add_slide(prs.slides[3].slide_layout)
    for shape in list(slide.shapes):
        shape._element.getparent().remove(shape._element)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255)
    box(slide, .65, .35, 12, .5, EMPTY_TITLE, 27, BLUE, True)
    box(slide, .67, .95, 12, .35,
        'A generation result with no visible answer after decoding', 17)
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.67), Inches(1.37),
                                 Inches(11.95), Inches(.025))
    rule.fill.solid()
    rule.fill.fore_color.rgb = RGBColor.from_string(BLUE)
    rule.line.fill.background()
    box(slide, .72, 1.62, 11.8, .65,
        'Generation returns → special tokens removed → no visible text → saved as no_response', 21)
    box(slide, .72, 2.4, 5.45, .4, 'What we observed', 22, BLUE, True)
    box(slide, .72, 2.95, 5.45, 1.6,
        'InstructBLIP    798 / 6,720 empty\n'
        'Qwen2.5-VL      0 / 6,720 empty\n'
        'LLaVA-1.5         0 / 6,720 empty', 22)
    box(slide, 6.6, 2.4, 5.65, .4, 'How we interpret it', 22, BLUE, True)
    box(slide, 6.6, 2.95, 5.65, 1.65,
        'Possible causes include early stopping, token handling or failed understanding.\n'
        'An empty string cannot establish the model’s reason.', 21)
    box(slide, .72, 4.9, 11.8, .35, 'InstructBLIP empty outputs by condition', 21, BLUE, True)
    table = slide.shapes.add_table(2, 4, Inches(.75), Inches(5.45), Inches(11.8), Inches(.88)).table
    values = [('Text-only', 'SD', 'Typography', 'SD + typography'),
              ('1 / 1,680', '119 / 1,680', '491 / 1,680', '187 / 1,680')]
    for row, items in enumerate(values):
        for col, value in enumerate(items):
            cell = table.cell(row, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255)
            cell.text = value
            for para in cell.text_frame.paragraphs:
                para.font.name = 'Arial'
                para.font.size = Pt(18)
                para.font.bold = row == 0
                para.font.color.rgb = RGBColor.from_string(BLUE if row == 0 else BLACK)
    box(slide, .72, 6.6, 11.8, .5,
        'Recorded separately; safety and refusal labels remain unresolved for these cases.', 19)
    slide.notes_slide.notes_text_frame.text = (
        'An empty completion means the generation call returned a result but the answer field '
        'contained no visible text after decoding and whitespace removal. It does not establish '
        'that the model consciously chose silence. It also does not establish failed '
        'understanding. A model may terminate immediately, return only special tokens, or '
        'encounter a mismatch in stopping or decoding conventions. Incorrect extraction can '
        'also erase a response. Each is a hypothesis that requires checking the generated '
        'token IDs, effective stopping settings, processor inputs and decoding path.\n\n'
        'For one early InstructBLIP typography case, an empty result recurred. The source '
        'audit found differences between token IDs in the checkpoint generation configuration '
        'and tokenizer conventions. That is a diagnostic lead. We have no completed saved '
        'token trace establishing that it caused the empty outputs, or that one cause explains '
        'all 798 cases. An exception such as GPU out of memory is a separate execution failure '
        'and cannot be inferred from an empty answer string.\n\n'
        'In the final archived run, InstructBLIP completed all 6,720 cases, with 5,922 nonempty '
        'answers and 798 empty outcomes. The empty counts are one for text-only, 119 for SD, '
        '491 for typography and 187 for SD plus typography. This concentration in typography '
        'is descriptive evidence. It cannot on its own prove an OCR failure or safety mechanism. '
        'Qwen2.5 and LLaVA produced zero empty completions in these saved runs.\n\n'
        'We retained every empty case with its ID and condition. The judge received the '
        'nonempty answers. An empty case has no safety or refusal label. We show the judged '
        'denominator and the all-planned bounds, so missing outputs cannot create an apparent '
        'improvement in safety. Azure filtering occurs later, when GPT-4.1 evaluates an '
        'already generated answer, and has its own inventory. The explanation I can defend '
        'is that no visible answer was produced under the recorded generation configuration, '
        'with the cause still unresolved.'
    )
    assert DECK.read_bytes() == original, 'Deck changed concurrently. Inspect before replacing.'
    temp = DECK.with_name(DECK.stem + '.updating.pptx')
    prs.save(temp)
    temp.replace(DECK)
    print({'slides': len(prs.slides), 'empty_slide': 9, 'backup': str(snapshot),
           'before_sha256': sha256(original).hexdigest(),
           'after_sha256': sha256(DECK.read_bytes()).hexdigest()})


if __name__ == '__main__':
    update()
