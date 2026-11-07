# MM-SafetyBench reproduction workbench

Inference code for selected experiments from [MM-SafetyBench (ECCV 2024)](https://arxiv.org/html/2311.17600v5). Use the [pinned author release](https://github.com/isXinLiu/MM-SafetyBench/tree/b80eedea3db312c09ded2082813390f68e750ef3) under its research-use terms. This branch contains code only. Benchmark data, model weights, executed notebooks, answers, and judge labels are external.

| Track | Code | Scope |
| --- | --- | --- |
| LLaVA-1.5-7B | [Colab notebook](llava-1.5-7b.ipynb) | Four-condition comparison with the 7B columns of Table 3 after scoring. |
| InstructBLIP Vicuna-7B | [Colab notebook](instructblip-vicuna-7b.ipynb) | Original model family. Text-only routes through the checkpoint's embedded language model and is an added baseline. |
| Qwen2.5-VL-3B-Instruct | [Image runner](qwen2_5_vl_images.py) and [text notebook](qwen2.5-vl-text.ipynb) | Extension to a newer model. The paper evaluated original Qwen-VL. |

## Run in Colab

1. Download the source ZIP from the pinned author release and the image ZIP linked by its README. Put them in your own private Drive folder as `MM-SafetyBench-main.zip` and `MM-SafetyBench(imgs).zip`. Preserve the ZIP layout and contents. The LLaVA and InstructBLIP notebooks verify the source ZIP and the released case and image fingerprints before inference.
2. Open the relevant notebook in Colab. The default Drive folder is `MyDrive/MM-SafetyBench-Private`. Edit its configuration if your folder differs. Use a GPU with sufficient VRAM for FP16 weights and activation headroom. LLaVA and InstructBLIP install isolated Python environments and check actual GPU placement. A single L4 passed the placement checks in our runs. Enable generation only after recording your compute allowance. Begin with the four benign smoke cases and then switch to full mode, which includes a 52-case timing pilot. Completed benchmark answers are saved individually. Resume only with matching inputs, checkpoint, software, decoding, and device placement.
3. For Qwen2.5 image conditions, mount Drive in a T4 runtime and run `qwen2_5_vl_images.py` inside Colab. The runner expects the image ZIP in the same Drive folder and uses the released questions from the pinned commit. The archived environment used PyTorch `2.11.0+cu130` and Transformers `5.22.0`. Use these versions for matching image and text runs. After validating the 5,040 saved image answers, use the text notebook to add the 1,680 matched original questions. The text notebook defaults to read-only case validation.
4. Check unique, nonempty answers by model, scenario, question ID, and condition. Keep the ledgers private. The LLaVA and InstructBLIP notebooks export a judging queue only after complete coverage. Azure GPT-4 judging is a separate stage. The authors supplied the scenario-specific rubrics and left the API connection to users of the release. Scoring and reproduction of published attack success rates remain pending.

## Scope and deviations

- The target is 1,680 questions across 13 scenarios and 6,720 cases per model. Text-only uses the original question. The three image conditions use the released SDXL, typography, and combined images. The images are reused from the release.
- For typography-only, the [release README](https://github.com/isXinLiu/MM-SafetyBench/tree/b80eedea3db312c09ded2082813390f68e750ef3#evaluation) pairs typography with the same rewritten question field as the combined condition. Section 3.2 of the paper groups typography with SDXL under the other rewritten question. This code follows the README.
- The notebooks pin upstream pretrained checkpoint revisions. FP16, greedy decoding, single-case inference, and token limits of 512 for LLaVA and 256 for the other two models are declared implementation settings. The historical settings are incompletely documented. InstructBLIP previously stopped on an empty decoded completion, and the runner retains stop-on-empty behavior.
- This workbench covers selected generation experiments. The full paper additionally evaluated a wider model panel and safety-prompt experiments. Generation coverage alone gives no attack success rate.
