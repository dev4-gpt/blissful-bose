import json, copy
ns = {}
exec(open("make_nb6_part1.py").read(), ns)
exec(open("make_nb6_part2.py").read(), ns)
g = lambda k: ns[k]
C5, md, code, find5 = ns["C5"], ns["md"], ns["code"], ns["find5"]
def cell5(token):
    for c in C5:
        if c["cell_type"] == "code" and token in "".join(c["source"]): return c
    raise KeyError(token)
FOOT = r'''## Before you quote any number

1. v6 is **exploratory** until the human audit (360 rows, stimulus shown, rubric fixed in `audit_v6_RUBRIC.md`) and a confirmatory run are done. Rogan-Gladen calibration uses the audit's sensitivity/specificity per labeller.
2. Report every H21-H27 line from "PRE-SPECIFIED CHECK, AMENDMENT 4", including refuted and SPLIT ones. A cell where the two guards disagree (kappa < 0.6) is **not interpretable**, not a null.
3. "No effect" claims need the equivalence column (TOST, margin 0.10) and cannot be made in a floor cell.
4. LLaVA: 152 items, square-padded, 4-bit; do not pool with Qwen. Presence-confounded: see H22/H23.
5. Refusal is not harm: show `unsafe_rate_all` beside each refusal gap. No prompts, images or replies are to be released; never commit `audit_v6_*`.'''
cells = [md(g("HEADER")), cell5("!pip -q install"), cell5("Optional independent OCR"), code(g("cfg6")), md("## 1. Data, rendering, presence images, FigStep"), code(g("data6")),
         md("## 2. Model classes and stable-key cache (imports v3/v4/v5 generations)"), code(g("cls6")),
         md("## 3. Reference phrases"), cell5("REF_OVERRIDE_PATH ="),
         md("## 4. Condition specs"), code(g("specs")),
         md("## 5. Generation (per model, cached, failure-isolated)"), code(g("loop")),
         md("## 6. Stimulus-aware three-way labelling"), code(g("JUDGES6")),
         md("## 7. Statistics helpers"), code(g("STATS6")),
         md("## 8. Contrasts, wrapper x modality grid, presence, FigStep, legibility, noise floor, H21-H27"), code(g("ANALYSIS6")),
         md("## 9. Figure and export"), code(g("EXPORT6")),
         md("## 10. Human-audit files (keep local)"), code(g("AUDIT6")), md(FOOT)]
nb = copy.deepcopy(ns["v5"]); nb["cells"] = cells
json.dump(nb, open(ns["ROOT"] + "notebooks/vlm_modality_tradeoff_v6.ipynb", "w"), indent=1, ensure_ascii=False)
print("cells:", len(cells))
