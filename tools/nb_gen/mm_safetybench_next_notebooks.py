"""Build one end-to-end Colab notebook per next-wave model family."""

import json

MODELS = {
    "idefics": ("IDEFICS-9B-Instruct", "HuggingFaceM4/idefics-9b-instruct", "4.46.3"),
    "instructblip": ("InstructBLIP Vicuna-7B", "Salesforce/instructblip-vicuna-7b", "4.46.3"),
    "qwen_vl": ("Original Qwen-VL-Chat", "Qwen/Qwen-VL-Chat", "4.32.0"),
}


def build_next_notebooks(root, notebook, mount, cells, handoff):
    shared = [
        cell for cell in cells if cell["cell_type"] == "code"
        and any(marker in "".join(cell["source"]) for marker in
                ("DRIVE = Path(", "def make_manifest(", "def execute("))
    ]
    config, preflight, runner = shared
    adapter = (root / "tools/nb_gen/mm_safetybench_next_runtime.py").read_text()
    for track, (name, model, version) in MODELS.items():
        intro = f"""# MM-SafetyBench · {name}

1. Mount private Drive and run the input check. It verifies 1,680 questions and all three image variants.
2. In the model cell, enter the approved time budget and select Run all. The default mode is `"smoke"`. The four benign cases check text and image routing and save answers separately. Follow the dependency instructions printed by the cell if the environment differs.
3. After reviewing the smoke output and approving the full run, set `MODE = "full"` and enter the input hashes. Reuse the checkpoint revision printed during smoke. The notebook saves 6,720 answers to its own private ledger.
4. Run the final cell after generation. In full mode it automatically checks all 6,720 answers and writes `Runs/Judge_Handoff_PRIVATE/{track}/queue_PRIVATE.json`. To export an existing completed run without loading the model, use preflight mode and set `EXPORT_SAVED_RUN = True` in the final cell. Export runs locally in Colab and uses no Azure credentials.

This is a benchmark reproduction candidate. The [paper](https://arxiv.org/html/2311.17600v5#S4.SS1) names the family. The [checkpoint](https://huggingface.co/{model}) and decoding settings here are declared choices. The three image conditions use the released inputs. Text-only is an additional matched baseline where the paper does not report it for this family. InstructBLIP's text-only path uses its embedded language model with no visual conditioning.

Use a separate Colab runtime for this model. FP16 memory fit and the Python environment still need smoke validation. Install Transformers {version} with Accelerate in this runtime before enabling generation. Original Qwen also uses tiktoken, einops, transformers_stream_generator and the checkpoint's custom code. Review that code at the pinned revision before setting `ALLOW_QWEN_CUSTOM_CODE`.
"""
        cfg = "".join(config["source"]).replace("RUN_PREFLIGHT = False", "RUN_PREFLIGHT = True")
        source = (f"TRACK = {track!r}\nMODEL_ID = {model!r}\nTRANSFORMERS_VERSION = {version!r}\n"
                  + adapter)
        export = "".join(handoff["source"]).replace(
            '# Select "qwen_images", "qwen_all", "llava", or "minigpt4" to export offline.\n'
            'JUDGE_HANDOFF = ""',
            'EXPORT_SAVED_RUN = False  # Use with preflight to export a completed ledger.',
        ).replace(
            "if JUDGE_HANDOFF:\n    export_judge_handoff(JUDGE_HANDOFF)",
            "if MODE == \"full\" or EXPORT_SAVED_RUN:\n"
            "    queue_path = export_judge_handoff(TRACK)\n"
            "    print(f\"Saved private judging queue to {queue_path}\")",
        )
        track_cells = [
            dict(cell_type="markdown", metadata={}, source=intro.splitlines(True)), mount,
            dict(config, source=cfg.splitlines(True)), preflight, runner,
            dict(handoff, source=("# *** -------\n" + source).splitlines(True)),
            dict(handoff, source=export.splitlines(True)),
        ]
        path = root / "notebooks" / f"mm_safetybench_{track}_generation.ipynb"
        path.write_text(json.dumps(dict(notebook, cells=track_cells), indent=1, ensure_ascii=False) + "\n")
