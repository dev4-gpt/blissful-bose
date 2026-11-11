"""Pinned upstream inference adapters. Embedded into each generated notebook worker."""


def gpu_budgets(torch):
    if not torch.cuda.is_available():
        raise RuntimeError("No CUDA GPU. Select a GPU runtime before installation or generation.")
    budgets = {}
    for index in range(torch.cuda.device_count()):
        free, _ = torch.cuda.mem_get_info(index)
        budgets[index] = max(0, free - 3 * 2**30)  # Activation/KV reserve, not a paper setting.
    minimum = {"llava": 14, "instructblip": 16, "idefics": 18, "qwen_vl": 20}[TRACK] * 2**30
    if sum(budgets.values()) < minimum:
        raise RuntimeError("Insufficient GPU-only weight budget with 3 GiB/device reserved. "
                           "Use a larger GPU or two GPUs; no CPU/disk/quantized fallback is enabled.")
    return budgets


def assert_gpu_only(model):
    if getattr(model, "is_loaded_in_4bit", False) or getattr(model, "is_loaded_in_8bit", False):
        raise ValueError("Quantized model is outside this FP16 protocol")
    placement = getattr(model, "hf_device_map", {})
    for value in placement.values():
        if not (isinstance(value, int) or str(value).startswith("cuda")):
            raise ValueError("CPU/disk/meta placement rejected before generation")
    devices = set()
    for _, parameter in model.named_parameters():
        if parameter.device.type != "cuda":
            raise ValueError("Every model parameter must reside on CUDA; offloaded/meta weights rejected")
        if parameter.is_floating_point() and str(parameter.dtype) != "torch.float16":
            raise ValueError("Expected FP16 parameters; precision silently changed")
        devices.add(str(parameter.device))
    if not devices:
        raise ValueError("Model has no verified GPU parameters")
    return dict(device_map={k: str(v) for k, v in placement.items()}, devices=sorted(devices))


def load_model(memory):
    import sys
    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoProcessor
    # Download exactly one weight serialization, plus tokenizer/config/source assets.
    patterns = ["*.json", "*.model", "*.txt", "*.tiktoken", "*.py"]
    patterns += ["pytorch_model*.bin"] if TRACK in {"llava", "qwen_vl"} else ["*.safetensors"]
    snapshot = snapshot_download(MODEL_ID, revision=REVISION, allow_patterns=patterns)
    if TRACK == "llava":
        clip = snapshot_download("openai/clip-vit-large-patch14-336", revision=CLIP_REVISION,
                                 allow_patterns=["*.json", "pytorch_model.bin"])
        import subprocess
        checkout = WORK / "LLaVA"
        if not checkout.exists():
            subprocess.run(["git", "init", str(checkout)], check=True)
            subprocess.run(["git", "-C", str(checkout), "fetch", "--depth", "1",
                            "https://github.com/haotian-liu/LLaVA.git", LLAVA_COMMIT], check=True)
            subprocess.run(["git", "-C", str(checkout), "checkout", "--detach", LLAVA_COMMIT], check=True)
        head = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", str(checkout), "status", "--porcelain"], text=True)
        if head != LLAVA_COMMIT or dirty.strip():
            raise ValueError("LLaVA source must be the unchanged pinned checkout")
        sys.path.insert(0, str(checkout))
        from llava.model.builder import load_pretrained_model
        from llava.model.language_model.llava_llama import LlavaConfig
        # HF also defines a composite LlavaConfig for a different architecture.
        # Load the pinned native class instead of AutoConfig's model_type dispatch.
        cfg = LlavaConfig.from_pretrained(snapshot, local_files_only=True)
        if (cfg.hidden_size != 4096 or cfg.image_aspect_ratio != "pad"
                or cfg.mm_vision_tower != "openai/clip-vit-large-patch14-336"
                or cfg.mm_use_im_start_end):
            raise ValueError("Unexpected original LLaVA configuration")
        # The unchanged upstream builder accepts a local tower path. Bind it to the pinned
        # snapshot instead of resolving mutable repo/main. Weights/preprocessing are unchanged.
        cfg.mm_vision_tower = clip
        mapping = "cuda:0" if len(memory) == 1 else "auto"
        tokenizer, model, processor, _ = load_pretrained_model(snapshot, None, "llava-v1.5-7b",
                      config=cfg, local_files_only=True, device_map=mapping,
                      max_memory={**memory, "cpu": 0})
        return model.eval(), (tokenizer, processor)
    common = dict(torch_dtype=torch.float16, device_map="auto", max_memory={**memory, "cpu": 0},
                  local_files_only=True)
    if TRACK == "qwen_vl":
        from transformers import AutoConfig
        from accelerate import init_empty_weights, infer_auto_device_map
        tokenizer = AutoTokenizer.from_pretrained(snapshot, trust_remote_code=True, local_files_only=True)
        cfg = AutoConfig.from_pretrained(snapshot, trust_remote_code=True, local_files_only=True)
        cfg.fp16, cfg.bf16, cfg.fp32, cfg.use_flash_attn = True, False, False, False
        with init_empty_weights():
            skeleton = AutoModelForCausalLM.from_config(cfg, trust_remote_code=True,
                                                       torch_dtype=torch.float16)
        skeleton.tie_weights()
        # Qwen's vision encoder must remain on one GPU; its text blocks may span both T4s.
        mapping = infer_auto_device_map(skeleton, max_memory={**memory, "cpu": 0}, dtype=torch.float16,
                         no_split_module_classes=["QWenBlock", "VisionTransformer"])
        del skeleton
        if any(not (isinstance(v, int) or str(v).startswith("cuda")) for v in mapping.values()):
            raise RuntimeError("Qwen GPU-only map does not fit; use larger GPUs")
        common["device_map"] = mapping
        model = AutoModelForCausalLM.from_pretrained(snapshot, config=cfg, trust_remote_code=True, **common)
        return model.eval(), tokenizer
    if TRACK == "idefics":
        from transformers import IdeficsForVisionText2Text
        processor = AutoProcessor.from_pretrained(snapshot, local_files_only=True)
        return IdeficsForVisionText2Text.from_pretrained(snapshot, **common).eval(), processor
    from transformers import InstructBlipForConditionalGeneration, InstructBlipProcessor, BlipImageProcessor
    processor = InstructBlipProcessor.from_pretrained(snapshot, local_files_only=True,
                  image_processor=BlipImageProcessor.from_pretrained(snapshot, local_files_only=True))
    return InstructBlipForConditionalGeneration.from_pretrained(snapshot, **common).eval(), processor


def check_pixels(pixels):
    if pixels.ndim != 4 or pixels.shape[0] != 1 or pixels.shape[1] != 3:
        raise ValueError(f"Upstream single-image processor must return BCHW, received {tuple(pixels.shape)}")


def answer_case(case, images, loaded):
    import torch
    from PIL import Image
    from io import BytesIO
    model, processor = loaded
    image = None
    if case["image_path"] is not None:
        with Image.open(BytesIO(images.read(case["image_path"]))) as raw:
            image = raw.convert("RGB")
    settings = dict(do_sample=False, num_beams=1, max_new_tokens=MAX_NEW_TOKENS)
    question = case["question"]
    with torch.inference_mode():
        if TRACK == "llava":
            from llava.constants import DEFAULT_IMAGE_TOKEN, IMAGE_TOKEN_INDEX
            from llava.conversation import conv_templates
            from llava.mm_utils import process_images, tokenizer_image_token
            tokenizer, vision_processor = processor
            kwargs = {}
            if image is not None:
                tower_device = next(model.get_vision_tower().parameters()).device
                pixels = process_images([image], vision_processor, model.config)
                kwargs = dict(images=pixels.to(tower_device, dtype=torch.float16), image_sizes=[image.size])
                question = DEFAULT_IMAGE_TOKEN + "\n" + question
            conv = conv_templates["llava_v1"].copy()
            conv.append_message(conv.roles[0], question)
            conv.append_message(conv.roles[1], None)
            device = model.get_input_embeddings().weight.device
            ids = tokenizer_image_token(conv.get_prompt(), tokenizer, IMAGE_TOKEN_INDEX,
                                        return_tensors="pt").unsqueeze(0).to(device)
            tokens = model.generate(ids, use_cache=True, **settings, **kwargs)
            return tokenizer.batch_decode(tokens, skip_special_tokens=True)[0].strip(), tokens.shape[-1]
        if TRACK == "qwen_vl":
            import tempfile
            with tempfile.TemporaryDirectory(dir=WORK) as directory:
                content = []
                if image is not None:
                    path = Path(directory) / "input.png"
                    image.save(path)
                    content.append({"image": str(path)})
                content.append({"text": question})
                answer, _ = model.chat(processor, query=processor.from_list_format(content), history=None, **settings)
            # chat returns text only: re-tokenization is not the original generated token count.
            return answer.strip(), None
        if TRACK == "idefics":
            prompt = ["User:", image] if image is not None else ["User:"]
            prompt.append(f" {question}<end_of_utterance>\nAssistant:")
            inputs = processor([prompt], add_end_of_utterance_token=False, return_tensors="pt")
            inputs = inputs.to(model.get_input_embeddings().weight.device, dtype=torch.float16)
            eos = processor.tokenizer("<end_of_utterance>", add_special_tokens=False).input_ids
            blocked = processor.tokenizer(["<image>", "<fake_token_around_image>"],
                                          add_special_tokens=False).input_ids
            tokens = model.generate(**inputs, eos_token_id=eos, bad_words_ids=blocked, **settings)
            tokens = tokens[:, inputs.input_ids.shape[-1]:]
            return processor.batch_decode(tokens, skip_special_tokens=True)[0].strip(), tokens.shape[-1]
        if image is None:
            # Declared extension: no visual conditioning; use this same model's embedded LLM.
            lm = model.language_model
            inputs = processor.tokenizer(question, return_tensors="pt").to(lm.get_input_embeddings().weight.device)
            tokens = lm.generate(**inputs, **settings)[:, inputs.input_ids.shape[-1]:]
        else:
            inputs = processor(images=image, text=question, return_tensors="pt")
            check_pixels(inputs["pixel_values"])  # Never silently squeeze/reshape malformed inputs.
            device = next(model.vision_model.parameters()).device
            inputs = inputs.to(device, dtype=torch.float16)
            tokens = model.generate(**inputs, **settings)
        return processor.tokenizer.batch_decode(tokens, skip_special_tokens=True)[0].strip(), tokens.shape[-1]
