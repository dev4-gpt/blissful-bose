"""Steer2Edit rank-1 edit mathematics: CPU reference implementation and validators.

Transcribed from the official repository at pinned commit
86382c2f44fdfda2bafe80faf09634e6d729562c (2026-09-30), files
``safety_alignment/edit.py`` (edit construction) and
``safety_alignment/evaluate.py`` (edit application).

Purpose. Give the project a CPU-checkable, dependency-light copy of the exact
released arithmetic so that shapes, orientation, rank, degenerate-input
handling, precision and restoration can be validated before any GPU run and
before the method is adapted to a vision-language model.

This module reproduces released behaviour, including choices that differ from
the paper text. Each such choice is marked DEVIATION with the paper location it
departs from. It does not repair them; repairs are a separate recorded decision.

Published rule (paper v4, Section 3.5):

    dW_i  = sign(g_i) * max(|g_i| - rho*alpha, 0) / (rho*(1-alpha)) * vhat_i khat_i^T
    vhat_i = v_i / ||v_i||_2
    khat_i = W_i^T v_i / ||W_i^T v_i||_2
    g_i    = cos(v_i, W_i mu_i)

Run ``python3 tools/steer2edit_edit_math.py`` for the validation suite.
No network, no model download, no GPU.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import torch
import torch.nn.functional as F

# Released edit.py uses eps=1e-12 in its own l2_normalize helper.
L2_EPS = 1e-12


# ---------------------------------------------------------------------------
# Released primitives
# ---------------------------------------------------------------------------
def l2_normalize(x: torch.Tensor, eps: float = L2_EPS) -> torch.Tensor:
    """Released ``edit.py:l2_normalize``.

    Degenerate path: for x == 0 this returns 0/eps == 0 silently rather than
    raising, although Theorem 3.1 assumes v_i != 0.
    """
    return x / (x.norm(p=2) + eps)


def elastic_net_lambda(g: torch.Tensor, rho: float, alpha: float) -> torch.Tensor:
    """Released ``edit.py:elastic_net_lambda`` -- the Theorem 3.3 closed form.

    ``rho <= 0`` is the released sentinel for "do not edit this block";
    ``edit.sh`` passes ``-1.0``.
    """
    if rho is None or rho <= 0:
        return torch.zeros_like(g)
    num = torch.clamp(g.abs() - rho * alpha, min=0.0)
    den = rho * (1.0 - alpha)
    return torch.sign(g) * (num / den)


def mu_from_directions(pos_mean: torch.Tensor, neg_mean: torch.Tensor) -> torch.Tensor:
    """Mean input activation mu_i exactly as the released code forms it.

    DEVIATION. Paper v4 Section 3.4 defines mu_i = E[h_i] over the input
    distribution. ``edit.py`` lines 97-100 use the unweighted midpoint
    0.5*(pos_mean + neg_mean) of the two probing-set means. These agree only
    when the two sets are equally sized and weighted. In the released safety
    pipeline both are 100 examples, so they coincide there by construction
    rather than by definition.
    """
    return 0.5 * (pos_mean + neg_mean)


# ---------------------------------------------------------------------------
# Edit construction
# ---------------------------------------------------------------------------
@dataclass
class EditPack:
    """Compact rank-1 factors, mirroring the released saved dict."""

    attn: dict = field(default_factory=dict)  # (layer, head) -> {lambda, k_hat}
    mlp: dict = field(default_factory=dict)  # (layer, neuron) -> {lambda}
    meta: dict = field(default_factory=dict)

    def n_edits(self) -> tuple[int, int]:
        return len(self.attn), len(self.mlp)


def compute_attn_edits(
    w_o: torch.Tensor,
    v_attn: torch.Tensor,
    mu_attn: torch.Tensor,
    num_heads: int,
    rho_attn: float,
    alpha: float,
    layer: int = 0,
) -> dict:
    """Per-head rank-1 factors for one attention output projection.

    ``w_o`` carries torch Linear orientation ``[d_out, d_in] = [hidden, hidden]``;
    head ``j`` owns *input* columns ``[j*head_dim, (j+1)*head_dim)``.
    ``mu_attn`` is the mean *input* to ``o_proj``, sliced per head.
    """
    hidden = w_o.shape[0]
    head_dim = hidden // num_heads
    vhat = l2_normalize(v_attn)
    mu_heads = mu_attn.view(num_heads, head_dim)

    out: dict = {}
    for j in range(num_heads):
        c0, c1 = j * head_dim, (j + 1) * head_dim
        w_block = w_o[:, c0:c1]  # [hidden, head_dim]
        g = F.cosine_similarity(vhat, w_block @ mu_heads[j], dim=0)
        lam = elastic_net_lambda(g.view(1), rho_attn, alpha).item()
        if lam == 0.0:
            continue
        k_vec = w_block.T @ vhat  # [head_dim]
        k_norm = k_vec.norm(p=2).item()
        if k_norm == 0.0:
            continue  # released guard: skip rather than divide by zero
        out[(layer, j)] = {"lambda": float(lam), "k_hat": k_vec / k_norm}
    return out


def compute_mlp_edits(
    w_down: torch.Tensor,
    v_mlp: torch.Tensor,
    mu_mlp: torch.Tensor,
    rho_mlp: float,
    alpha: float,
    layer: int = 0,
) -> dict:
    """Per-neuron rank-1 factors for one MLP down projection.

    ``w_down`` is ``[hidden, intermediate]``; neuron ``j`` is input column j, so
    the component has ``d_in == 1`` and its input-space direction can only be
    +-1. The released code folds that sign into lambda.
    """
    vhat = l2_normalize(v_mlp)
    scaled = w_down * mu_mlp.unsqueeze(0)  # [hidden, intermediate]
    g = F.cosine_similarity(vhat.unsqueeze(1), scaled, dim=0)  # [intermediate]
    lambdas = elastic_net_lambda(g, rho_mlp, alpha)
    k_scalars = w_down.T @ vhat  # [intermediate]

    mask = (lambdas != 0.0) & (k_scalars != 0.0)
    out: dict = {}
    for idx in torch.where(mask)[0].tolist():
        k_sign = 1.0 if k_scalars[idx].item() > 0 else -1.0
        out[(layer, idx)] = {"lambda": float(lambdas[idx].item() * k_sign)}
    return out


def build_edit_pack(
    w_o: torch.Tensor,
    w_down: torch.Tensor,
    v_attn: torch.Tensor,
    v_mlp: torch.Tensor,
    mu_attn: torch.Tensor,
    mu_mlp: torch.Tensor,
    num_heads: int,
    rho_attn: float,
    rho_mlp: float,
    alpha: float,
    layer: int = 0,
) -> EditPack:
    if not alpha < 1.0:
        raise ValueError("alpha must be < 1 for the Elastic-Net closed form")
    return EditPack(
        attn=compute_attn_edits(w_o, v_attn, mu_attn, num_heads, rho_attn, alpha, layer),
        mlp=compute_mlp_edits(w_down, v_mlp, mu_mlp, rho_mlp, alpha, layer),
        meta={
            "vhat_attn": {layer: l2_normalize(v_attn)},
            "vhat_mlp": {layer: l2_normalize(v_mlp)},
            "rho_attn": rho_attn,
            "rho_mlp": rho_mlp,
            "alpha": alpha,
            "num_heads": num_heads,
        },
    )


# ---------------------------------------------------------------------------
# Edit application (released evaluate.py:apply_rank1_edits_to_hf_model)
# ---------------------------------------------------------------------------
def apply_edits(
    w_o: torch.Tensor,
    w_down: torch.Tensor,
    pack: EditPack,
    num_heads: int,
    layer: int = 0,
) -> None:
    """Apply factors in place, in the dtype of the target weights.

    Casting vhat/khat to the weight dtype is released behaviour and is where
    bfloat16 rounding enters the update.
    """
    hidden = w_o.shape[0]
    head_dim = hidden // num_heads

    for (lyr, head), payload in pack.attn.items():
        if lyr != layer:
            continue
        lam = float(payload["lambda"])
        vhat = pack.meta["vhat_attn"][lyr].to(dtype=w_o.dtype)
        khat = payload["k_hat"].to(dtype=w_o.dtype)
        c0, c1 = head * head_dim, (head + 1) * head_dim
        w_o[:, c0:c1].add_(lam * torch.outer(vhat, khat))

    for (lyr, neuron), payload in pack.mlp.items():
        if lyr != layer:
            continue
        lam = float(payload["lambda"])
        vhat = pack.meta["vhat_mlp"][lyr].to(dtype=w_down.dtype)
        w_down[:, neuron].add_(lam * vhat)


# ---------------------------------------------------------------------------
# Validation suite
# ---------------------------------------------------------------------------
HIDDEN, NUM_HEADS, INTER = 64, 8, 96
# Published best safety configuration for llama2-7b, recovered from the
# official README visualize_edit.py invocation (not stated in the paper).
PUBLISHED_BEST_LLAMA2 = {"rho_attn": 0.18, "rho_mlp": 0.55, "alpha": 0.8}


def _fixture(dtype=torch.float32, seed=20):
    """Synthetic single-layer fixture with transformer-shaped tensors."""
    gen = torch.Generator().manual_seed(seed)
    f = dict(
        w_o=torch.randn(HIDDEN, HIDDEN, generator=gen, dtype=torch.float32) * 0.05,
        w_down=torch.randn(HIDDEN, INTER, generator=gen, dtype=torch.float32) * 0.05,
        v_attn=torch.randn(HIDDEN, generator=gen, dtype=torch.float32),
        v_mlp=torch.randn(HIDDEN, generator=gen, dtype=torch.float32),
        mu_attn=torch.randn(HIDDEN, generator=gen, dtype=torch.float32),
        mu_mlp=torch.randn(INTER, generator=gen, dtype=torch.float32).abs(),
    )
    return {k: v.to(dtype) for k, v in f.items()}


def _report(results: list[tuple[str, bool, str]]) -> bool:
    width = max(len(name) for name, _, _ in results)
    print(f"\n{'CHECK'.ljust(width)}  RESULT  DETAIL")
    print("-" * (width + 50))
    for name, ok, detail in results:
        print(f"{name.ljust(width)}  {'PASS' if ok else 'FAIL':6s}  {detail}")
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("-" * (width + 50))
    print(f"{len(results) - n_fail}/{len(results)} checks passed")
    return n_fail == 0


def run_validations() -> bool:
    cfg: dict[str, float] = PUBLISHED_BEST_LLAMA2
    results: list[tuple[str, bool, str]] = []

    # 1. Shapes and orientation.
    f = _fixture()
    pack = build_edit_pack(
        f["w_o"], f["w_down"], f["v_attn"], f["v_mlp"], f["mu_attn"], f["mu_mlp"],
        NUM_HEADS,
        rho_attn=cfg["rho_attn"], rho_mlp=cfg["rho_mlp"], alpha=cfg["alpha"],
    )
    n_attn, n_mlp = pack.n_edits()
    head_dim = HIDDEN // NUM_HEADS
    ok_shape = all(p["k_hat"].shape == (head_dim,) for p in pack.attn.values())
    ok_unit = all(
        abs(p["k_hat"].norm().item() - 1.0) < 1e-5 for p in pack.attn.values()
    )
    results.append((
        "component shapes / orientation",
        ok_shape and ok_unit,
        f"k_hat in R^head_dim={head_dim}, unit norm; {n_attn} heads, {n_mlp} neurons edited",
    ))

    # 2. Rank-1 structure of each per-head delta.
    base = _fixture()
    edited = {k: v.clone() for k, v in base.items()}
    apply_edits(edited["w_o"], edited["w_down"], pack, NUM_HEADS)
    # The delta is exactly rank 1 in exact arithmetic. In float32 the trailing
    # singular values are rounding noise near 1e-7 of the leading one, so a
    # rank test must compare s[1]/s[0] rather than use an absolute tolerance:
    # matrix_rank(delta, tol=1e-8) reports rank 5-8 on the same tensors.
    sv_ratios = []
    for (_, head) in pack.attn:
        c0, c1 = head * head_dim, (head + 1) * head_dim
        delta = edited["w_o"][:, c0:c1] - base["w_o"][:, c0:c1]
        sv = torch.linalg.svdvals(delta.double())
        sv_ratios.append((sv[1] / sv[0]).item())
    ok_rank = len(sv_ratios) > 0 and all(r < 1e-5 for r in sv_ratios)
    results.append((
        "rank-1 change per edited head",
        ok_rank,
        f"max s[1]/s[0] = {max(sv_ratios):.2e} over {len(sv_ratios)} heads"
        if sv_ratios
        else "no edits produced",
    ))

    # 3. Disabled-edit parity (released -1.0 sentinel).
    off = build_edit_pack(
        f["w_o"], f["w_down"], f["v_attn"], f["v_mlp"], f["mu_attn"], f["mu_mlp"],
        NUM_HEADS, rho_attn=-1.0, rho_mlp=-1.0, alpha=cfg["alpha"],
    )
    par = _fixture()
    ref = {k: v.clone() for k, v in par.items()}
    apply_edits(par["w_o"], par["w_down"], off, NUM_HEADS)
    ok_parity = (
        off.n_edits() == (0, 0)
        and torch.equal(par["w_o"], ref["w_o"])
        and torch.equal(par["w_down"], ref["w_down"])
    )
    results.append((
        "disabled-edit parity (rho=-1)",
        ok_parity,
        "zero factors, weights bitwise identical",
    ))

    # 4. Only intended weights change.
    untouched_heads = [
        j for j in range(NUM_HEADS) if (0, j) not in pack.attn
    ]
    ok_scope = True
    for j in untouched_heads:
        c0, c1 = j * head_dim, (j + 1) * head_dim
        if not torch.equal(edited["w_o"][:, c0:c1], base["w_o"][:, c0:c1]):
            ok_scope = False
    changed_cols = (edited["w_down"] != base["w_down"]).any(dim=0)
    expected_cols = {n for (_, n) in pack.mlp}
    ok_scope = ok_scope and set(torch.where(changed_cols)[0].tolist()) == expected_cols
    results.append((
        "only intended weights modified",
        ok_scope,
        f"{len(untouched_heads)} heads and {INTER - len(expected_cols)} neurons untouched",
    ))

    # 5. Finite arithmetic.
    ok_finite = bool(torch.isfinite(edited["w_o"]).all().item()) and bool(
        torch.isfinite(edited["w_down"]).all().item()
    )
    lam_vals = [p["lambda"] for p in pack.attn.values()] + [
        p["lambda"] for p in pack.mlp.values()
    ]
    lam_max = max((abs(v) for v in lam_vals), default=0.0)
    results.append((
        "finite arithmetic",
        bool(ok_finite and all(abs(v) < 1e6 for v in lam_vals)),
        f"max |lambda| = {lam_max:.4f}",
    ))

    # 6. Exact restoration by subtracting the same factors.
    restored = {k: v.clone() for k, v in edited.items()}
    neg = EditPack(
        attn={k: {**v, "lambda": -v["lambda"]} for k, v in pack.attn.items()},
        mlp={k: {"lambda": -v["lambda"]} for k, v in pack.mlp.items()},
        meta=pack.meta,
    )
    apply_edits(restored["w_o"], restored["w_down"], neg, NUM_HEADS)
    max_resid = max(
        (restored["w_o"] - base["w_o"]).abs().max().item(),
        (restored["w_down"] - base["w_down"]).abs().max().item(),
    )
    results.append((
        "restoration of original weights",
        max_resid < 1e-6,
        f"max residual = {max_resid:.2e} (float32)",
    ))

    # 7. Determinism / configuration-safe resumption.
    pack_b = build_edit_pack(
        _fixture()["w_o"], _fixture()["w_down"], f["v_attn"], f["v_mlp"],
        f["mu_attn"], f["mu_mlp"], NUM_HEADS,
        rho_attn=cfg["rho_attn"], rho_mlp=cfg["rho_mlp"], alpha=cfg["alpha"],
    )
    same_keys = set(pack.attn) == set(pack_b.attn) and set(pack.mlp) == set(pack_b.mlp)
    same_lams = all(
        pack.attn[k]["lambda"] == pack_b.attn[k]["lambda"] for k in pack.attn
    )
    results.append((
        "deterministic edit construction",
        same_keys and same_lams,
        "identical component set and magnitudes across rebuilds",
    ))

    # 8. Degenerate steering vector (zero norm).
    fz = _fixture()
    zero_pack = build_edit_pack(
        fz["w_o"], fz["w_down"], torch.zeros(HIDDEN), torch.zeros(HIDDEN),
        fz["mu_attn"], fz["mu_mlp"], NUM_HEADS,
        rho_attn=cfg["rho_attn"], rho_mlp=cfg["rho_mlp"], alpha=cfg["alpha"],
    )
    results.append((
        "zero-norm steering vector handled",
        zero_pack.n_edits() == (0, 0),
        "l2_normalize(0)=0 via eps, cosine=0, soft-threshold -> no edit, no exception",
    ))

    # 9. Degenerate importance score (W mu = 0).
    fd = _fixture()
    zero_pack2 = build_edit_pack(
        fd["w_o"], fd["w_down"], fd["v_attn"], fd["v_mlp"],
        torch.zeros(HIDDEN), torch.zeros(INTER), NUM_HEADS,
        rho_attn=cfg["rho_attn"], rho_mlp=cfg["rho_mlp"], alpha=cfg["alpha"],
    )
    results.append((
        "zero mean activation handled (g:=0)",
        zero_pack2.n_edits() == (0, 0),
        "matches Theorem 3.3 convention g_i := 0 when W_i mu_i = 0",
    ))

    # 10. bfloat16 vs float32 precision of the same configuration.
    f32 = _fixture(dtype=torch.float32)
    fbf = _fixture(dtype=torch.bfloat16)
    p32 = build_edit_pack(
        f32["w_o"], f32["w_down"], f32["v_attn"], f32["v_mlp"],
        f32["mu_attn"], f32["mu_mlp"], NUM_HEADS,
        rho_attn=cfg["rho_attn"], rho_mlp=cfg["rho_mlp"], alpha=cfg["alpha"],
    )
    pbf = build_edit_pack(
        fbf["w_o"], fbf["w_down"], fbf["v_attn"], fbf["v_mlp"],
        fbf["mu_attn"], fbf["mu_mlp"], NUM_HEADS,
        rho_attn=cfg["rho_attn"], rho_mlp=cfg["rho_mlp"], alpha=cfg["alpha"],
    )
    set32, setbf = set(p32.attn) | set(p32.mlp), set(pbf.attn) | set(pbf.mlp)
    jaccard = len(set32 & setbf) / max(len(set32 | setbf), 1)
    results.append((
        "bf16 vs fp32 component selection",
        True,  # observational, not pass/fail
        f"selected {len(set32)} fp32 vs {len(setbf)} bf16, Jaccard={jaccard:.3f} "
        "(observational: released pipeline runs bf16)",
    ))

    # 11. Structural property of the MLP importance score.
    fm = _fixture()
    vhat = l2_normalize(fm["v_mlp"])
    g_scaled = F.cosine_similarity(
        vhat.unsqueeze(1), fm["w_down"] * fm["mu_mlp"].unsqueeze(0), dim=0
    )
    g_unscaled = F.cosine_similarity(vhat.unsqueeze(1), fm["w_down"], dim=0)
    # For a 1-input component, cos(v, W_j * mu_j) = sign(mu_j) * cos(v, W_j),
    # so |g| cannot depend on the magnitude of the mean activation.
    agree = torch.allclose(g_scaled.abs(), g_unscaled.abs(), atol=1e-5)
    results.append((
        "MLP |g| independent of ||mu|| (structural)",
        agree,
        "mean-activation magnitude affects only the sign for MLP neurons",
    ))

    return _report(results)


if __name__ == "__main__":
    import sys

    print("Steer2Edit edit-math validation (CPU, synthetic fixture)")
    print(f"torch {torch.__version__}; released requirements pin torch==2.6.0")
    print(
        "config under test: "
        f"rho_attn={PUBLISHED_BEST_LLAMA2['rho_attn']}, "
        f"rho_mlp={PUBLISHED_BEST_LLAMA2['rho_mlp']}, "
        f"alpha={PUBLISHED_BEST_LLAMA2['alpha']} "
        "(README best llama2-7b safety setting)"
    )
    sys.exit(0 if run_validations() else 1)
