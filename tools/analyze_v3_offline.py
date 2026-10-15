"""Offline checks on the saved v3 judge labels (no GPU).

Uses only the two independent guard classifiers (Qwen3Guard-Gen-4B, WildGuard): their labels need no
refusal-cue gate. The two LLM-rubric judges are not used here because they label ~85-90% of replies
REFUSE in every condition (see docs/V3_RESULTS_AND_NEXT_STEPS.md).

Layout assumption (checked in the notebook): items are scenario-major blocks of 38; the label list is
per model: A, Aben, B, C, D, E, Bben, Dben (harmful n=304, benign n=48).

Run: python3 -I tools/analyze_v3_offline.py [bundle_dir]
"""
import json, sys
from math import comb
from pathlib import Path
import numpy as np
import statsmodels.api as sm
from statsmodels.genmod.cov_struct import Exchangeable

D = Path(sys.argv[1] if len(sys.argv) > 1 else "v3_final_four_judges")
MODELS = ["Qwen/Qwen2-VL-2B-Instruct", "Qwen/Qwen2.5-VL-3B-Instruct"]
ORDER = ["A", "Aben", "B", "C", "D", "E", "Bben", "Dben"]
N = {c: (48 if c.endswith("ben") else 304) for c in ORDER}
BLOCK = 38


def load(judge):
    labs = json.load(open(D / f"lab_{judge}.json"))
    out, pos = {}, 0
    for m in MODELS:
        for c in ORDER:
            seg = labs[pos:pos + N[c]]
            pos += N[c]
            out[(m, c)] = np.array([1.0 if x == "REFUSE" else 0.0 for x in seg])
    assert pos == len(labs)
    return out


def mcnemar_exact(x, y):
    b = int(((x == 1) & (y == 0)).sum())
    c = int(((x == 0) & (y == 1)).sum())
    n = b + c
    if n == 0:
        return b, c, 1.0
    k = min(b, c)
    p = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    return b, c, p


def kappa(x, y):
    po = (x == y).mean()
    pe = x.mean() * y.mean() + (1 - x.mean()) * (1 - y.mean())
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def sign_test(vals):
    pos, neg = sum(v > 0 for v in vals), sum(v < 0 for v in vals)
    n = pos + neg
    if n == 0:
        return pos, neg, 1.0
    k = min(pos, neg)
    return pos, neg, min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def gee_odds(rB, rE, rC):
    """Logistic GEE, refusal ~ condition (B ref), exchangeable within item. Returns OR and CI for E vs B and C vs E."""
    n = len(rB)
    y = np.concatenate([rB, rE, rC])
    cond = np.repeat([0, 1, 2], n)
    X = sm.add_constant(np.column_stack([cond == 1, cond == 2]).astype(float))
    grp = np.tile(np.arange(n), 3)
    fit = sm.GEE(y, X, groups=grp, family=sm.families.Binomial(), cov_struct=Exchangeable()).fit()
    b, ci = np.asarray(fit.params), np.asarray(fit.conf_int())
    cvar = np.asarray(fit.cov_params())
    d = b[2] - b[1]  # contrast C vs E
    se = float(np.sqrt(cvar[2, 2] + cvar[1, 1] - 2 * cvar[1, 2]))
    return {"E_vs_B_OR": (float(np.exp(b[1])), float(np.exp(ci[1][0])), float(np.exp(ci[1][1]))),
            "C_vs_E_OR": (float(np.exp(d)), float(np.exp(d - 1.96 * se)), float(np.exp(d + 1.96 * se)))}


def main():
    judges = ["qwen3guard", "wildguard"]
    L = {j: load(j) for j in judges}
    cl = np.repeat(np.arange(8), BLOCK)
    report = {}
    for m in MODELS:
        report[m] = {}
        for j in judges:
            R = {c: L[j][(m, c)] for c in ORDER}
            B, E, C = R["B"], R["E"], R["C"]
            g_sc = [float(B[cl == s].mean() - C[cl == s].mean()) for s in range(8)]
            p_sc = [float(B[cl == s].mean() - E[cl == s].mean()) for s in range(8)]
            i_sc = [float(E[cl == s].mean() - C[cl == s].mean()) for s in range(8)]
            report[m][j] = {
                "rates": {c: round(float(R[c].mean()), 3) for c in ORDER},
                "mcnemar_B_vs_E_prompt": mcnemar_exact(B, E),
                "mcnemar_E_vs_C_image": mcnemar_exact(E, C),
                "mcnemar_B_vs_C_gap": mcnemar_exact(B, C),
                "per_scenario_G": [round(v, 3) for v in g_sc],
                "per_scenario_P": [round(v, 3) for v in p_sc],
                "per_scenario_I": [round(v, 3) for v in i_sc],
                "sign_test_P_pos_neg_p": sign_test(p_sc),
                "sign_test_I_pos_neg_p": sign_test(i_sc),
                "gee": gee_odds(B, E, C),
            }
        report[m]["guard_kappa"] = {c: round(kappa(L["qwen3guard"][(m, c)], L["wildguard"][(m, c)]), 3)
                                    for c in ["A", "B", "C", "D", "E"]}
    out = D / "offline_analysis.json"
    json.dump(report, open(out, "w"), indent=1, default=list)
    print(json.dumps(report, indent=1, default=list))
    print("saved", out)


if __name__ == "__main__":
    main()
