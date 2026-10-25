"""Native Idefics3/SmolVLM adapter; common delivered 448 canvas, no image splitting.

This is an explicit preprocessing adaptation, not the model-card default 512 pipeline.
Official model/config: https://huggingface.co/HuggingFaceTB/SmolVLM-500M-Instruct
Transformers reference: v4.57.1/models/idefics3/{modeling,processing}_idefics3.py.
"""
import time
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from vlm_visual_adapter import QwenAttackAdapter, shifted_nll


class SmolAttackAdapter(QwenAttackAdapter):
    MODEL = 'HuggingFaceTB/SmolVLM-500M-Instruct'
    REVISION = 'a7da5b986cb59b408707209984f360a5f4ad7e47'

    def __init__(self, canvas=448, max_new=64):
        import transformers
        from transformers import AutoProcessor, Idefics3ForConditionalGeneration
        if transformers.__version__ != '4.57.1' or not torch.cuda.is_available():
            raise RuntimeError('Reviewed transformers==4.57.1 and CUDA required')
        if canvas != 448 or not 1 <= max_new <= 256:
            raise ValueError('Reviewed Smol profile is 448 canvas and 1..256 output tokens')
        self.device, self.canvas, self.max_new = torch.device('cuda:0'), canvas, max_new
        self.processor = AutoProcessor.from_pretrained(self.MODEL,revision=self.REVISION,
                trust_remote_code=False,use_fast=False)
        self.processor.image_processor.do_image_splitting = False
        self.processor.image_processor.do_resize = False
        self.processor.image_processor.max_image_size = dict(longest_edge=canvas)
        self.processor.image_seq_len = (canvas//16//4)**2
        # FP32 is a declared deployment choice on T4; no claim of precision-matched architecture causality.
        self.model = Idefics3ForConditionalGeneration.from_pretrained(self.MODEL,
                revision=self.REVISION,trust_remote_code=False,torch_dtype=torch.float32,
                attn_implementation='eager').to(self.device).eval().requires_grad_(False)
        self.model.config.use_cache = False
        self.identity = dict(model=self.MODEL,revision=self.REVISION,canvas=canvas,
                precision='fp32',attention='eager',batch=1,max_new=max_new,
                transformers=transformers.__version__,torch=torch.__version__,
                image_processor=self.processor.image_processor.to_dict(),
                image_seq_len=self.processor.image_seq_len,generation='greedy')

    def pixels(self, raw):
        processor = self.processor.image_processor
        mean = raw.new_tensor(processor.image_mean).view(1,3,1,1)
        std = raw.new_tensor(processor.image_std).view(1,3,1,1)
        return ((raw-mean)/std).unsqueeze(1).to(self.model.dtype)

    def _inputs(self, image, prompt, target=None):
        content = ([dict(type='image')] if image is not None else [])+[dict(type='text',text=prompt)]
        messages=[]
        if getattr(self,'system_prompt',''):
            messages.append(dict(role='system',content=[dict(type='text',text=self.system_prompt)]))
        messages.append(dict(role='user',content=content))
        text = self.processor.apply_chat_template(messages,
                tokenize=False,add_generation_prompt=True)
        if getattr(self,'system_prompt','') and self.system_prompt not in text:
            raise ValueError('Native chat template dropped system instruction')
        dummy = Image.new('RGB',(self.canvas,self.canvas),'white')
        data = self.processor(text=[text],images=[[dummy]] if image is not None else None,
                return_tensors='pt')
        data = {k:v.to(self.device) for k,v in data.items()}
        data.pop('pixel_values',None)
        start = data['input_ids'].shape[1]
        if target is not None:
            ids = self.processor.tokenizer(target,add_special_tokens=False,return_tensors='pt')['input_ids'].to(self.device)
            if not 0 < ids.shape[1] <= 128:
                raise ValueError('Target must contain 1..128 tokens')
            data['input_ids'] = torch.cat([data['input_ids'],ids],dim=1)
            data['attention_mask'] = torch.ones_like(data['input_ids'])
        if data['input_ids'].shape[1]>1024:
            raise ValueError('Input token cap exceeded')
        return data,start

    def _forward(self, image, inputs):
        return self.model(**inputs,pixel_values=self.pixels(image),use_cache=False).logits

    def feature_objective(self, target_image):
        def features(image):
            pixels = self.pixels(image)
            mask = torch.ones((1,1,self.canvas,self.canvas),dtype=torch.bool,device=self.device)
            return self.model.model.get_image_features(pixels,mask).float()
        with torch.no_grad():
            target = features(target_image).detach()
        return lambda image:F.mse_loss(features(image),target)

    def parity_check(self, image, prompt, target):
        pil = Image.fromarray((image[0].detach().cpu().permute(1,2,0).numpy()*255).round().astype(np.uint8))
        native = self.processor.image_processor(images=[[pil]],return_tensors='pt')
        ours = self.pixels(image)
        reference = native['pixel_values'].to(self.device,self.model.dtype)
        if reference.shape != ours.shape or not torch.allclose(ours,reference,atol=2e-6,rtol=2e-6):
            raise ValueError('Smol native preprocessing mismatch')
        inputs,start = self._inputs(image,prompt,target)
        with torch.no_grad():
            actual = self._forward(image,inputs)[:,start-1].float()
            expected = self.model(**inputs,pixel_values=reference,use_cache=False).logits[:,start-1].float()
        if not torch.isfinite(actual).all() or not torch.allclose(actual,expected,atol=1e-4,rtol=1e-4):
            raise ValueError('Smol native logits mismatch')
        return dict(processor_max_error=float((ours-reference).abs().max()),
                    logits_max_error=float((actual-expected).abs().max()))

    def generate(self, image, prompt):
        inputs,start = self._inputs(image,prompt)
        # Record the prior allocation peak before generation resets it.
        previous_peak = torch.cuda.max_memory_allocated()/1e9
        torch.cuda.reset_peak_memory_stats()
        begin = time.monotonic()
        visual = {} if image is None else dict(pixel_values=self.pixels(image))
        with torch.no_grad():
            out = self.model.generate(**inputs,**visual,max_new_tokens=self.max_new,
                    do_sample=False,use_cache=True)
        torch.cuda.synchronize()
        ids = out[0,start:]
        eos = self.model.generation_config.eos_token_id
        eos = eos if isinstance(eos,list) else [eos]
        return dict(response=self.processor.tokenizer.decode(ids,skip_special_tokens=True),
                generated_ids=ids.cpu().tolist(),cap_hit=len(ids)>=self.max_new and int(ids[-1]) not in eos,
                seconds=time.monotonic()-begin,peak_allocated_gb=torch.cuda.max_memory_allocated()/1e9,
                peak_reserved_gb=torch.cuda.max_memory_reserved()/1e9,pre_generation_peak_gb=previous_peak)


def cpu_architecture_check():
    """Random tiny native weights test the full Idefics3 image gradient, not model safety."""
    from transformers import Idefics3Config,Idefics3ForConditionalGeneration
    config = Idefics3Config(image_token_id=5,scale_factor=2,
            text_config=dict(vocab_size=32,hidden_size=32,intermediate_size=64,num_hidden_layers=1,
                             num_attention_heads=4,num_key_value_heads=2,pad_token_id=0),
            vision_config=dict(hidden_size=32,intermediate_size=64,num_hidden_layers=1,
                               num_attention_heads=4,image_size=64,patch_size=16))
    config._attn_implementation='eager'
    with torch.random.fork_rng():
        torch.manual_seed(1)
        model=Idefics3ForConditionalGeneration(config).eval().requires_grad_(False)
    raw=torch.linspace(.1,.9,3*64*64).reshape(1,1,3,64,64).requires_grad_(True)
    ids=torch.tensor([[1,5,5,5,5,8,9]])
    out=model(input_ids=ids,attention_mask=torch.ones_like(ids),pixel_values=raw,
              pixel_attention_mask=torch.ones((1,1,64,64),dtype=torch.bool),use_cache=False)
    grad,=torch.autograd.grad(shifted_nll(out.logits,ids,6),raw)
    assert torch.isfinite(grad).all() and grad.abs().max()>0
    return dict(native_idefics3_image_gradient='passed',pretrained=False,gpu=False)
