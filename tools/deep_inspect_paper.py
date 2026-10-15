import sys
import fitz
import re

paper_path = sys.argv[1]
doc = fitz.open(paper_path)
print(f"=== Deep Inspect: {paper_path} ===")
print("Total Pages:", len(doc))

full_text = ""
for i, page in enumerate(doc):
    t = page.get_text()
    full_text += f"\n<<< PAGE {i+1} >>>\n" + t

# Find all Table headings and their following lines
tables = re.findall(r'(Table\s+\d+[:\.][^\n]+(?:\n[^\n]+){1,4})', full_text)
print(f"\n--- TABLES FOUND ({len(tables)}) ---")
for t in tables:
    clean_t = " ".join(t.split())
    print("  * ", clean_t[:200])

# Find all Figure headings and captions
figures = re.findall(r'(Figure\s+\d+[:\.][^\n]+(?:\n[^\n]+){1,4})', full_text)
print(f"\n--- FIGURES FOUND ({len(figures)}) ---")
for f in figures:
    clean_f = " ".join(f.split())
    print("  * ", clean_f[:200])

# Find limitations sections
print("\n--- LIMITATIONS / CONCLUSIONS / DISCUSSIONS ---")
m = re.findall(r'(\n(?:[0-9IVX]+\.?\s*)?(?:Limitations?|Discussion|Conclusions?|Broader Impacts?)[^\n]*\n[\s\S]{1,2000})', full_text, re.IGNORECASE)
for snippet in m[:5]:
    print("MATCH:\n", snippet[:600].strip())
    print("="*50)
