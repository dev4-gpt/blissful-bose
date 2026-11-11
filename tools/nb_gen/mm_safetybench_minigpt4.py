RUN_MINIGPT4 = False
MINIGPT4_SMOKE = True
MINIGPT4_CHECKOUT = Path("/content/MiniGPT-4")
MINIGPT4_COMMIT = ""
MINIGPT4_VICUNA = None  # Local Vicuna v0 checkpoint directory.
MINIGPT4_PROJECTOR = None  # Matching upstream MiniGPT-4 weights.
MINIGPT4_PROJECTOR_SHA = ""


def load_minigpt4():
    import sys
    from types import SimpleNamespace
    import torch

    head = subprocess.check_output(
        ["git", "-C", str(MINIGPT4_CHECKOUT), "rev-parse", "HEAD"], text=True).strip()
    if head != MINIGPT4_COMMIT or not re.fullmatch(r"[a-f0-9]{40}", head):
        raise RuntimeError("Pin the reviewed MiniGPT-4 source revision")
    if not Path(MINIGPT4_VICUNA).is_dir() or digest(Path(MINIGPT4_PROJECTOR)) != MINIGPT4_PROJECTOR_SHA:
        raise RuntimeError("Stage the matched Vicuna and projector weights")
    if not torch.cuda.is_available():
        raise RuntimeError("A GPU is required")
    sys.path.insert(0, str(MINIGPT4_CHECKOUT.resolve()))
    from minigpt4.common.config import Config
    from minigpt4.common.registry import registry
    from minigpt4.conversation.conversation import Chat, CONV_VISION_Vicuna0

    config = Config(SimpleNamespace(cfg_path=str(MINIGPT4_CHECKOUT / "eval_configs/minigpt4_eval.yaml"),
                                    options=None))
    model_config = config.model_cfg
    model_config.llama_model = str(MINIGPT4_VICUNA)
    model_config.ckpt = str(MINIGPT4_PROJECTOR)
    model_config.low_resource = True
    model_config.device_8bit = 0
    model = registry.get_model_class(model_config.arch).from_config(model_config).to("cuda:0").eval()
    image_config = config.datasets_cfg.cc_sbu_align.vis_processor.train
    processor = registry.get_processor_class(image_config.name).from_config(image_config)
    return model, Chat(model, processor, device="cuda:0"), CONV_VISION_Vicuna0


def generate_minigpt4(case, archive, loaded):
    import torch
    from PIL import Image

    model, chat, template = loaded
    conversation = template.copy()
    images = []
    with torch.inference_mode():
        if case["image_path"] is not None:
            with Image.open(BytesIO(archive.read(case["image_path"]))) as raw:
                chat.upload_img(raw.convert("RGB"), conversation, images)
            chat.encode_img(images)
        else:
            conversation.system = ""
        chat.ask(case["question"], conversation)
        conversation.append_message(conversation.roles[1], None)
        prompt = conversation.get_prompt()
        if images:
            embeds = model.get_context_emb(prompt, images)
        else:
            # Upstream get_context_emb indexes the first image unconditionally.
            tokens = model.llama_tokenizer(prompt, return_tensors="pt").to(model.device)
            embeds = model.embed_tokens(tokens.input_ids)
        output = model.llama_model.generate(inputs_embeds=embeds, max_new_tokens=300,
                                            num_beams=1, do_sample=False)
        answer = model.llama_tokenizer.decode(output[0], skip_special_tokens=True).split("###")[0].strip()
    if not answer:
        raise ValueError("Empty completion")
    return answer


if RUN_MINIGPT4:
    if not (MINIGPT4_VICUNA and MINIGPT4_PROJECTOR and MINIGPT4_PROJECTOR_SHA):
        raise RuntimeError("Configure the MiniGPT-4 checkpoints first")
    execute(cases, RUNS / "MM_SafetyBench_MiniGPT4_PRIVATE", load_minigpt4, generate_minigpt4,
            dict(checkpoint="MiniGPT-4 Vicuna v0 candidate", revision=MINIGPT4_COMMIT,
                 vicuna=str(MINIGPT4_VICUNA), projector_sha256=MINIGPT4_PROJECTOR_SHA,
                 low_resource=True, max_new_tokens=300, num_beams=1, do_sample=False),
            MINIGPT4_SMOKE)
