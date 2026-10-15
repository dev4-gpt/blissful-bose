import re

with open("/Users/aryamandev/.gemini/antigravity/brain/97ef5727-a6d8-4482-acae-2c416f7c0d18/.system_generated/steps/605/content.md", "r") as f:
    text = f.read()

print("=== Deep Inspect PolyJailbreak ===")
print("Total characters:", len(text))

tables = re.findall(r'(Table\s+[0-9IVX]+[:\.][^\n]+(?:\n[^\n]+){1,5})', text)
print(f"\n--- TABLES FOUND ({len(tables)}) ---")
for t in tables:
    clean_t = " ".join(t.split())
    print("  * ", clean_t[:250])

figures = re.findall(r'(Figure\s+\d+[:\.][^\n]+(?:\n[^\n]+){1,5})', text)
print(f"\n--- FIGURES FOUND ({len(figures)}) ---")
for f in figures:
    clean_f = " ".join(f.split())
    print("  * ", clean_f[:250])

sections = re.findall(r'(#+\s+[^\n]+)', text)
print(f"\n--- SECTIONS FOUND ({len(sections)}) ---")
for s in sections[:25]:
    print("  * ", s)

print("\n--- DISCUSSION / LIMITATIONS / CONCLUSION ---")
m = re.findall(r'(\n#+\s*(?:Discussion|Limitations?|Conclusion)[^\n]*\n[\s\S]{1,2500})', text, re.IGNORECASE)
for snippet in m:
    print("SNIPPET:\n", snippet[:1000].strip())
    print("="*50)
