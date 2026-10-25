"""Differentiable Qwen2.5-VL adapter, batch one, native Transformers, frozen weights.

The attack canvas is explicit RGB: 224x224 by default, 448x448 in the broader panel. Resizing occurs
BEFORE defining its perturbation budget; original-resolution robustness is not claimed.
Patch layout follows the Apache-2.0 Transformers Qwen2VLImageProcessor implementation:
https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/models/qwen2_vl/image_processing_qwen2_vl.py
No upstream source copied; processor parity is checked before optimization.
"""
import hashlib
import time

import torch
import torch.nn.functional as F


def patchify(raw, image_processor):
    """Single still image, normalized then temporal-repeat and spatial patch grouping."""
    if raw.ndim != 4 or raw.shape[:2] != (1, 3):
        raise ValueError('Single RGB still image required')
    p, m, t = image_processor.patch_size, image_processor.merge_size, image_processor.temporal_patch_size
    h, w = raw.shape[-2:]
    if h % (p*m) or w % (p*m):
        raise ValueError('Canvas dimensions must be multiples of patch*merge')
    mean = raw.new_tensor(image_processor.image_mean).view(1, 3, 1, 1)
    std = raw.new_tensor(image_processor.image_std).view(1, 3, 1, 1)
    z = (raw - mean) / std
    gh, gw = h//p, w//p
    z = z.repeat(t, 1, 1, 1).reshape(1, t, 3, gh//m, m, p, gw//m, m, p)
    return z.permute(0, 3, 6, 4, 7, 2, 1, 5, 8).reshape(gh*gw, 3*t*p*p)


def shifted_nll(logits, ids, target_start):
    if not 1 <= target_start < ids.shape[1]:
        raise ValueError('Empty/misaligned target span')
    selected = logits[:, target_start-1:-1].float()
    targets = ids[:, target_start:]
    return F.cross_entropy(selected.reshape(-1, selected.shape[-1]), targets.reshape(-1))


class QwenAttackAdapter:
    MODEL = 'Qwen/Qwen2.5-VL-3B-Instruct'
    REVISION = '66285546d2b821cf421d4f5eb2576359d3770cd3'

    def __init__(self, canvas=224, max_new=256):
        import transformers
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
        if transformers.__version__ != '4.57.1':
            raise RuntimeError('Use reviewed transformers==4.57.1; restart after installing')
        if not torch.cuda.is_available():
            raise RuntimeError('Real VLM branch requires CUDA; CPU checks use injected tiny models')
        if canvas not in (224, 448) or max_new < 1 or max_new > 512:
            raise ValueError('Reviewed canvases=224/448; output cap must be 1..512')
        self.device, self.canvas, self.max_new = torch.device('cuda:0'), canvas, max_new
        self.processor = AutoProcessor.from_pretrained(self.MODEL, revision=self.REVISION,
                trust_remote_code=False, use_fast=False, min_pixels=canvas**2, max_pixels=canvas**2)
        # Explicit single device. No silent CPU offload or quantization substitutions.
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(self.MODEL,
                revision=self.REVISION, trust_remote_code=False, torch_dtype=torch.float16,
                attn_implementation='eager').to(self.device).eval()
        self.model.requires_grad_(False)
        self.model.config.use_cache = False
        self.identity = dict(model=self.MODEL, revision=self.REVISION, canvas=canvas,
                precision='fp16', attention='eager', batch=1, max_new=max_new,
                transformers=transformers.__version__, torch=torch.__version__,
                image_processor=self.processor.image_processor.to_dict(), generation='greedy')

    def read_image(self, path):
        from PIL import Image
        import numpy as np
        im = Image.open(path).convert('RGB')
        # Budget is on this canonical delivered canvas, never on original source pixels.
        if im.size != (self.canvas, self.canvas):
            im = im.resize((self.canvas, self.canvas), Image.Resampling.BICUBIC)
        return torch.from_numpy(np.array(im, copy=True)).permute(2, 0, 1).unsqueeze(0).to(self.device).float()/255

    def _inputs(self, image, prompt, target=None):
        from PIL import Image
        import numpy as np
        # Only template/IDs/grid go through non-differentiable processor. Replace
        # pixel_values with patchify(image) in _forward to keep raw input gradients.
        dummy = Image.fromarray(np.zeros((self.canvas, self.canvas, 3), dtype=np.uint8))
        content = ([dict(type='image')] if image is not None else []) + [dict(type='text', text=prompt)]
        messages = []
        if getattr(self,'system_prompt',''):
            messages.append(dict(role='system',content=[dict(type='text',text=self.system_prompt)]))
        messages.append(dict(role='user',content=content))
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        if getattr(self,'system_prompt','') and self.system_prompt not in text:
            raise ValueError('Native chat template dropped system instruction')
        data = self.processor(text=[text], images=[dummy] if image is not None else None, return_tensors='pt')
        data = {k: v.to(self.device) for k, v in data.items()}
        data.pop('pixel_values', None)
        start = data['input_ids'].shape[1]
        if target is not None:
            target_ids = self.processor.tokenizer(target, add_special_tokens=False, return_tensors='pt')['input_ids'].to(self.device)
            if not 0 < target_ids.shape[1] <= 128:
                raise ValueError('Target must have 1..128 tokens')
            data['input_ids'] = torch.cat([data['input_ids'], target_ids], dim=1)
            data['attention_mask'] = torch.ones_like(data['input_ids'])
        if data['input_ids'].shape[1] > 1024:
            raise ValueError('Development input token cap exceeded')
        return data, start

    def _forward(self, image, inputs):
        return self.model(**inputs, pixel_values=patchify(image, self.processor.image_processor).half(),
                          use_cache=False).logits

    def objective(self, clean, prompt, target):
        inputs, start = self._inputs(clean, prompt, target)
        def loss(image):
            return shifted_nll(self._forward(image, inputs), inputs['input_ids'], start)
        return loss

    def feature_objective(self, target_image):
        # Qwen merged visual-token features, not CLIP joint text/image embeddings.
        grid = torch.tensor([[1, self.canvas//14, self.canvas//14]], device=self.device)
        def features(image):
            value = self.model.model.visual(patchify(image, self.processor.image_processor).half(), grid_thw=grid)
            if not isinstance(value, torch.Tensor):
                raise TypeError('Unexpected Qwen visual output; inspect new library before use')
            return value.float()
        with torch.no_grad():
            target = features(target_image).detach()
        return lambda image: F.mse_loss(features(image), target)

    def match_objective(self, clean, prompt, target, teacher_prompt):
        student, start = self._inputs(clean, prompt, target)
        teacher, teacher_start = self._inputs(clean, teacher_prompt, target)
        with torch.no_grad():
            distribution = self._forward(clean, teacher)[:, teacher_start-1:-1].float().softmax(-1).detach()
        def loss(image):
            logits = self._forward(image, student)[:, start-1:-1].float()
            # Soft cross entropy under SAME teacher-forced continuation; adaptation
            # of behavioral matching, not the original full context-set algorithm.
            return -(distribution * logits.log_softmax(-1)).sum(-1).mean()
        return loss

    def parity_check(self, image, prompt, target):
        import numpy as np
        from PIL import Image
        pil = Image.fromarray((image[0].detach().cpu().permute(1, 2, 0).numpy()*255).round().astype(np.uint8))
        ref = self.processor.image_processor(images=[pil], return_tensors='pt')
        ours = patchify(image, self.processor.image_processor)
        reference = ref['pixel_values'].to(ours.device)
        if ours.shape != reference.shape or not torch.allclose(ours, reference, atol=2e-6, rtol=2e-6):
            raise ValueError('Differentiable processor parity failed')
        inputs, start = self._inputs(image, prompt, target)
        if not torch.equal(inputs['image_grid_thw'], ref['image_grid_thw'].to(self.device)):
            raise ValueError('Image grid differs from reference')
        with torch.no_grad():
            actual = self._forward(image, inputs)[:, start-1].float()
            expected = self.model(**inputs, pixel_values=reference.half(), use_cache=False).logits[:, start-1].float()
        if not torch.isfinite(actual).all() or not torch.allclose(actual, expected, atol=.05, rtol=.01):
            raise ValueError('Clean logits differ from reference')
        return dict(processor_max_error=float((ours-reference).abs().max()), logits_max_error=float((actual-expected).abs().max()))

    def generate(self, image, prompt):
        inputs, start = self._inputs(image, prompt)
        previous_peak = torch.cuda.max_memory_allocated()/1e9
        torch.cuda.reset_peak_memory_stats()
        begin = time.monotonic()
        visual = {} if image is None else dict(pixel_values=patchify(image, self.processor.image_processor).half())
        with torch.no_grad():
            result = self.model.generate(**inputs, **visual,
                    max_new_tokens=self.max_new, do_sample=False, use_cache=True)
        torch.cuda.synchronize()
        ids = result[0, start:]
        eos = self.model.generation_config.eos_token_id
        eos = eos if isinstance(eos, list) else [eos]
        return dict(response=self.processor.tokenizer.decode(ids, skip_special_tokens=True),
                    generated_ids=ids.cpu().tolist(), cap_hit=len(ids) >= self.max_new and int(ids[-1]) not in eos,
                    seconds=time.monotonic()-begin, peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9,
                    peak_reserved_gb=torch.cuda.max_memory_reserved()/1e9,
                    pre_generation_peak_gb=previous_peak)

    def frozen_fingerprint(self):
        # Full weight fingerprint is expensive; check frozen flags and mutation version
        # counters for ALL tensors, plus representative values. Loading is revision pinned.
        states = []
        for name, p in self.model.named_parameters():
            if p.requires_grad:
                raise ValueError('Trainable model parameter detected')
            sample = p.detach().reshape(-1)[:4].float().cpu().numpy().tobytes()
            states.append((name, p._version, hashlib.sha256(sample).hexdigest()))
        return states

    def close(self):
        self.model = None
        import gc
        gc.collect()
        torch.cuda.empty_cache()
