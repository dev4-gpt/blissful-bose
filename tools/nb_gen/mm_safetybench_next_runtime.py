MODEL_REVISION = ""  # Required for full runs. For smoke, resolve and print the current commit.
MODE = "smoke"  # "preflight", "smoke", or "full"
ALLOW_QWEN_CUSTOM_CODE = False
MAX_NEW_TOKENS = 32 if TRACK == "instructblip" and MODE == "smoke" else 256


def load_candidate(revision):
    import torch
    from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
    from huggingface_hub import snapshot_download

    snapshot = snapshot_download(MODEL_ID, revision=revision,
                                 ignore_patterns=["*.bin"] if TRACK == "instructblip" else None)
    common = dict(device_map="auto", torch_dtype=torch.float16, local_files_only=True)
    if TRACK == "instructblip":
        # Reserve VRAM for activations/KV cache and RAM for the Colab kernel.
        common.update(max_memory={0: "10GiB", "cpu": "4GiB"},
                      offload_folder="/content/instructblip_offload",
                      offload_state_dict=True)
    if TRACK == "qwen_vl":
        processor = AutoTokenizer.from_pretrained(snapshot, trust_remote_code=True, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(snapshot, trust_remote_code=True, fp16=True, **common)
    else:
        if TRACK == "idefics":
            processor = AutoProcessor.from_pretrained(snapshot, local_files_only=True)
            from transformers import IdeficsForVisionText2Text
            model = IdeficsForVisionText2Text.from_pretrained(snapshot, **common)
        else:
            from transformers import (InstructBlipForConditionalGeneration,
                                      InstructBlipProcessor, BlipImageProcessor)
            processor = InstructBlipProcessor.from_pretrained(
                snapshot, local_files_only=True,
                image_processor=BlipImageProcessor.from_pretrained(snapshot, local_files_only=True))
            model = InstructBlipForConditionalGeneration.from_pretrained(snapshot, **common)
    return model.eval(), processor


def generate_candidate(case, archive, loaded):
    import tempfile
    import torch
    from PIL import Image

    model, processor = loaded
    question = case["question"]
    raw = None if case["image_path"] is None else archive.read(case["image_path"])
    if TRACK == "instructblip" and MODE == "smoke":
        print(f"Checking InstructBLIP input: {case['variant']}", flush=True)
    settings = dict(max_new_tokens=MAX_NEW_TOKENS, do_sample=False, num_beams=1)
    if TRACK == "instructblip" and MODE == "smoke":
        # A routing smoke test must not spend the entire budget on one reply.
        settings["max_time"] = 90
    with torch.inference_mode():
        if TRACK == "qwen_vl":
            with tempfile.TemporaryDirectory() as temporary:
                content = []
                if raw is not None:
                    path = Path(temporary) / "input.png"
                    with Image.open(BytesIO(raw)) as original:
                        original.convert("RGB").save(path)
                    content.append({"image": str(path)})
                content.append({"text": question})
                query = processor.from_list_format(content)
                answer, _ = model.chat(processor, query=query, history=None, **settings)
            return answer.strip()

        image = None
        if raw is not None:
            with Image.open(BytesIO(raw)) as original:
                image = original.convert("RGB")
        if TRACK == "idefics":
            prompt = ["User:", image] if image is not None else ["User:"]
            prompt.append(f" {question}<end_of_utterance>\nAssistant:")
            inputs = processor([prompt], add_end_of_utterance_token=False,
                               return_tensors="pt").to(model.device, dtype=torch.float16)
            eos = processor.tokenizer("<end_of_utterance>", add_special_tokens=False).input_ids
            blocked = processor.tokenizer(["<image>", "<fake_token_around_image>"],
                                          add_special_tokens=False).input_ids
            tokens = model.generate(**inputs, eos_token_id=eos, bad_words_ids=blocked, **settings)
            return processor.batch_decode(tokens[:, inputs.input_ids.shape[1]:],
                                          skip_special_tokens=True)[0].strip()

        if image is None:
            if hasattr(model, "hf_device_map"):
                model._preprocess_accelerate()
            lm = model.language_model
            device = lm.get_input_embeddings().weight.device
            if device.type == "meta":
                device = torch.device("cuda", torch.cuda.current_device())
            inputs = processor.tokenizer(question, return_tensors="pt").to(device)
            tokens = lm.generate(**inputs, **settings)
            tokens = tokens[:, inputs.input_ids.shape[1]:]
        else:
            inputs = processor(images=image, text=question, return_tensors="pt")
            pixels = inputs["pixel_values"]
            # A single image must reach the encoder as B,C,H,W.
            if pixels.ndim == 5 and pixels.shape[0] == 1 and pixels.shape[1] == 1:
                pixels = pixels[:, 0]
            if pixels.ndim != 4 or pixels.shape[0] != 1 or pixels.shape[1] != 3:
                raise ValueError(f"Unexpected single-image pixel_values shape: {tuple(pixels.shape)}")
            inputs["pixel_values"] = pixels
            if MODE == "smoke":
                print(f"Vision input shape: {tuple(pixels.shape)}", flush=True)
            device = model.device
            if device.type == "meta":
                device = torch.device("cuda", torch.cuda.current_device())
            inputs = inputs.to(device, dtype=torch.float16)
            tokens = model.generate(**inputs, **settings)
        return processor.tokenizer.batch_decode(tokens, skip_special_tokens=True)[0].strip()


def run_candidate():
    if MODE not in {"smoke", "full"}:
        raise ValueError("Choose preflight, smoke, or full")
    if not (OWNER_APPROVAL_RECORD and GPU_MINUTES and GPU_MINUTES > 0):
        raise RuntimeError("Record the approved GPU time budget")
    import torch
    import transformers
    import gc
    import sys
    import traceback
    from huggingface_hub import HfApi

    if transformers.__version__ != TRANSFORMERS_VERSION:
        raise RuntimeError(f"Install transformers=={TRANSFORMERS_VERSION} and restart this runtime")
    if not torch.cuda.is_available():
        raise RuntimeError("Select a GPU runtime")
    previous_exception = getattr(sys, "last_traceback", None)
    if previous_exception is not None:
        traceback.clear_frames(previous_exception)
    gc.collect()
    torch.cuda.empty_cache()
    if TRACK == "qwen_vl" and not (ALLOW_QWEN_CUSTOM_CODE and MODEL_REVISION):
        raise RuntimeError("Review and pin the original Qwen custom code before running")
    if MODE == "full" and not MODEL_REVISION:
        raise ValueError("Reuse the model revision recorded during smoke")
    revision = MODEL_REVISION or HfApi().model_info(MODEL_ID).sha
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("Provide a full checkpoint commit hash")
    print(f"Checkpoint {MODEL_ID} at {revision}", flush=True)
    provenance = dict(model=MODEL_ID, revision=revision, precision="float16",
                      torch=torch.__version__, transformers=transformers.__version__,
                      gpu=torch.cuda.get_device_name(0), max_new_tokens=MAX_NEW_TOKENS,
                      do_sample=False, num_beams=1)
    if TRACK == "instructblip":
        provenance["placement"] = "fp16_auto_10gib_v1"
    execute(cases, RUNS / f"MM_SafetyBench_{TRACK}_PRIVATE", lambda: load_candidate(revision),
            generate_candidate, provenance, MODE == "smoke")


if MODE != "preflight":
    if TRACK == "instructblip" and MODE == "smoke":
        GPU_MINUTES = min(GPU_MINUTES, 15)
    run_candidate()
