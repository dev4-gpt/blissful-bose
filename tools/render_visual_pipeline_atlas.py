"""Render the atlas's restricted Mermaid flowcharts with Graphviz, without network/model calls.

The Markdown is the maintained source. Unknown diagram syntax fails explicitly.
Exports self-contained SVG HTML and a diagram-per-page PDF, with source citations.
"""
import argparse
import html
import io
import json
from pathlib import Path
import re
import subprocess
import textwrap

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/VISUAL_ATTACK_PIPELINE_ATLAS.md'
EDGE = re.compile(r'^(\w+)\s*(?:-->|-\.\s*(.*?)\s*\.->)\s*(\w+)$')
NODE = re.compile(r'(\w+)\[([^\]]+)\]')


def graph(source):
    nodes, edges = {}, []
    for line in source.splitlines():
        line = line.strip()
        if not line or line == 'flowchart LR':
            continue
        def replace(match):
            key, value = match.groups()
            if key in nodes and nodes[key] != value:
                raise ValueError('Conflicting node label: ' + key)
            nodes[key] = value
            return key
        normalized = NODE.sub(replace, line)
        match = EDGE.fullmatch(normalized)
        if not match:
            raise ValueError('Unsupported diagram line: ' + line)
        start, label, end = match.groups()
        edges.append((start, end, label))
    if not nodes or any(a not in nodes or b not in nodes for a, b, _ in edges):
        raise ValueError('Missing node definition')
    result = ['digraph G {', 'rankdir=LR; bgcolor="transparent";',
              'graph [pad=.25,nodesep=.35,ranksep=.55];',
              'node [shape=box,style="rounded,filled",fontname="Helvetica",',
              'fontsize=15,margin=".15,.12",color="#2d516d",fillcolor="#edf4fb"];',
              'edge [fontname="Helvetica",fontsize=11,color="#3e5870"];']
    for key, value in nodes.items():
        fill = '#edf4fb'
        if re.search(r'loss|objective|distance|gradient|optimizer', value, re.I):
            fill = '#eee7f7'
        elif re.search(r'evaluat|judge|scor|utility|review|detect', value, re.I):
            fill = '#dff3ef'
        elif 'frozen' not in value.lower() and re.search(r'variable|attacker|adversarial|candidate|optimized image', value, re.I):
            fill = '#fff0dc'
        result.append(f'{key} [label={json.dumps(textwrap.fill(value, 29))},fillcolor="{fill}"];')
    for start, end, label in edges:
        options = '' if label is None else '[style=dashed,color="#7653a7",label=' + json.dumps(label) + ']'
        result.append(f'{start} -> {end} {options};')
    result.append('}')
    return '\n'.join(result)


def sections(markdown):
    blocks = []
    pattern = re.compile(r'```mermaid\n(.*?)\n```', re.S)
    for match in pattern.finditer(markdown):
        before = markdown[:match.start()]
        heading = re.findall(r'^#{1,3} (.+)$', before, re.M)[-1]
        after = markdown[match.end():].strip()
        explanation = re.split(r'\n##?\s|\n###\s', after, maxsplit=1)[0]
        blocks.append((heading, match.group(1), explanation))
    return blocks


def plain(text):
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', text).replace('**', '').replace('`', '')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', type=Path, default=ROOT/'presentation')
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text()
    blocks = sections(source)
    if len(blocks) != 16:
        raise ValueError('Atlas diagram count changed: review export layout')
    pdf = args.out_dir/'VLM_Visual_Attack_Pipeline_Atlas.pdf'
    web = args.out_dir/'VLM_Visual_Attack_Pipeline_Atlas.html'
    book = canvas.Canvas(str(pdf), pagesize=(1191, 842))
    book.setTitle('Visual attacks: architectural atlas — 28 October 2026')
    cards = []
    for index, (title, diagram, explanation) in enumerate(blocks, 1):
        dot = graph(diagram).encode()
        svg = subprocess.run(['dot', '-Tsvg'], input=dot, capture_output=True, check=True).stdout.decode()
        png = subprocess.run(['dot', '-Tpng', '-Gdpi=120'], input=dot, capture_output=True, check=True).stdout
        # PNG exists only in memory; no stimulus or private result data are involved.
        with PILImage.open(io.BytesIO(png)) as im:
            width, height = im.size
        book.setFillColor(colors.HexColor('#f3f6fa')); book.rect(0, 0, 1191, 842, fill=1, stroke=0)
        book.setFillColor(colors.HexColor('#172e49')); book.setFont('Helvetica-Bold', 24)
        for i, line in enumerate(simpleSplit(title, 'Helvetica-Bold', 24, 1080)):
            book.drawString(48, 785-i*29, line)
        scale = min(1095/width, 420/height)
        w, h = width*scale, height*scale
        book.drawImage(ImageReader(io.BytesIO(png)), (1191-w)/2, 545-h/2, w, h, mask='auto')
        book.setFont('Helvetica', 12)
        narrative = plain(explanation)
        # Full math and source URLs remain in the maintained Markdown and HTML.
        narrative = re.sub(r'\\\(.*?\\\)', '[equation in linked Markdown]', narrative)
        y = 290
        for paragraph in narrative.split('\n\n'):
            if paragraph.startswith('|'):
                continue
            for line in simpleSplit(paragraph.replace('\n', ' '), 'Helvetica', 12, 1090):
                if y < 65:
                    break
                book.drawString(48, y, line); y -= 16
            y -= 7
        book.setFont('Helvetica', 10)
        book.drawString(48, 32, f'{index}/16 | Explanatory redraw; no new experiment. Native reproduction status: see Markdown audit.')
        book.showPage()
        svg = svg[svg.index('<svg'):]
        cards.append('<section><h2>'+html.escape(title)+'</h2>'+svg+'<p class="explanation">'+html.escape(explanation)+'</p></section>')
    book.save()
    web.write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Visual attack architectural atlas</title><style>
body{font:18px/1.6 system-ui;background:#f3f6fa;color:#172e49;max-width:1500px;margin:auto;padding:32px}
section{background:white;border:1px solid #d5dfeb;border-radius:14px;margin:32px 0;padding:25px;overflow:auto}
svg{display:block;max-width:100%;height:auto;margin:auto}h1,h2{line-height:1.2}.explanation{white-space:pre-wrap;font-size:16px}
@media print{section{break-before:page;border:0}body{padding:0;background:white}}
</style><h1>Visual attacks: structural and architectural atlas</h1>
<p>28 October 2026 · 16 source-derived explanatory diagrams · Offline, self-contained SVG.
Purple dashed edges show optimization/feedback. Orange nodes identify selected input variables;
green nodes identify evaluation. Read the Markdown atlas for the full mathematical contract,
measured-result ledger and reproduction boundaries. No new attacks were run.</p>'''+''.join(cards)+'</html>')
    print(json.dumps(dict(diagrams=len(blocks),pdf=str(pdf),html=str(web))))


if __name__ == '__main__':
    main()
