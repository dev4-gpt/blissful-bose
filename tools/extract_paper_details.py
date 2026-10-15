import fitz
import json
import re
from pathlib import Path

PDF_DIR = Path("/Users/aryamandev/Developer/blissful-bose/presentation/paper_pdfs")

PAPERS = {
    "figstep": "figstep.pdf",
    "polyjailbreak": "polyjailbreak.pdf",
    "hades": "hades.pdf",
    "siuo": "siuo_acl.pdf",
    "vlsbench": "vlsbench_acl.pdf",
    "mmjailbench": "mmjailbench.pdf",
    "cmrm": "cmrm.pdf",
    "jailbound": "jailbound.pdf",
    "safetyreminder": "safetyreminder_aaai.pdf",
    "adpo": "adpo.pdf",
    "safevlm": "safevlm.pdf",
    "holisafe": "holisafe.pdf",
    "vscbench": "vscbench.pdf"
}

def analyze_pdf(key, filename):
    filepath = PDF_DIR / filename
    if not filepath.exists():
        return {"error": f"File {filename} not found"}
    
    doc = fitz.open(str(filepath))
    num_pages = len(doc)
    full_text = ""
    page_texts = []
    for i, page in enumerate(doc):
        t = page.get_text()
        page_texts.append(t)
        full_text += f"\n--- PAGE {i+1} ---\n" + t

    # Find Tables
    table_matches = re.findall(r'(Table\s+\d+[:\.\s][^\n\r]+(?:\n[^\n\r]+)?)', full_text, re.IGNORECASE)
    # Find Figures
    figure_matches = re.findall(r'(Figure\s+\d+[:\.\s][^\n\r]+(?:\n[^\n\r]+)?)', full_text, re.IGNORECASE)
    
    # Search for limitations sections
    limitations_matches = re.findall(r'(?:(?:limitations?|broader\s+impacts?|discussion|future\s+work)[\s\S]{1,1500})', full_text, re.IGNORECASE)
    
    # Extract headings / sections
    headings = re.findall(r'(\n[0-9IVX]+\.?\s+[A-Z][^\n]{3,60}\n)', full_text)

    return {
        "key": key,
        "filename": filename,
        "num_pages": num_pages,
        "headings": [h.strip() for h in headings[:25]],
        "num_tables_found": len(table_matches),
        "table_captions": [t.strip().replace('\n', ' ') for t in table_matches[:15]],
        "num_figures_found": len(figure_matches),
        "figure_captions": [f.strip().replace('\n', ' ') for f in figure_matches[:15]],
        "limitations_snippets": [l[:300].strip().replace('\n', ' ') for l in limitations_matches[:3]]
    }

results = {}
for k, v in PAPERS.items():
    print(f"Extracting {k} ({v})...")
    results[k] = analyze_pdf(k, v)

with open("/Users/aryamandev/Developer/blissful-bose/scratch_paper_meta.json", "w") as f:
    json.dump(results, f, indent=2)

print("Done! Extracted metadata saved.")
