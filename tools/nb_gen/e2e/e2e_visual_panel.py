"""CPU integration test: two injected models, real pixel optimizers and private files."""
from pathlib import Path
import tempfile
import sys
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import vlm_visual_panel as panel


class FakeAdapter:
    def __init__(self,canvas=448,max_new=64):
        self.identity=dict(model='fake',revision='test',canvas=canvas,precision='fp32')

    def read_image(self,path):
        return torch.tensor(np.array(Image.open(path).convert('RGB'),copy=True)).permute(2,0,1).unsqueeze(0).float()/255

    def objective(self,image,prompt,target):
        return lambda x:(x-.2).square().mean()

    def feature_objective(self,target):
        return lambda x:(x-target).square().mean()

    def match_objective(self,image,prompt,target,teacher_prompt):
        return self.objective(image,prompt,target)

    def parity_check(self,image,prompt,target):
        return dict(processor_max_error=0.,logits_max_error=0.)

    def generate(self,image,prompt):
        return dict(response='red',generated_ids=[1],cap_hit=False,seconds=0.,
                    peak_allocated_gb=0.,peak_reserved_gb=0.)

    def frozen_fingerprint(self):
        return ('unchanged',)

    def close(self):
        pass


def main():
    import time
    torch.set_num_threads(1)
    with tempfile.TemporaryDirectory(prefix='panel_PRIVATE_') as folder:
        root=Path(folder)
        with patch.object(panel,'QwenAttackAdapter',FakeAdapter),patch.object(panel,'SmolAttackAdapter',FakeAdapter), \
             patch.object(torch.cuda,'reset_peak_memory_stats',lambda:None), \
             patch.object(torch.cuda,'max_memory_allocated',lambda:0):
            a=panel.run_model(root,'qwen',time.time()+120)
            b=panel.run_model(root,'smol',time.time()+120)
            assert a['status']=='complete' and b['status']=='complete',(a,b)
            assert len(a['variants'])==12 and b['transfer_cases']==8
            assert panel.run_model(root,'qwen',time.time()+120)==a
        aggregate=panel.summarize(root)
        assert len(aggregate['cases'])==68,len(aggregate['cases'])
        review=panel.review_packet(root)
        assert review['sampled']==120 and review['human_status']=='unlabelled'
        labels=panel.analyze_reviews(root)
        assert labels['axes']['unsafe_assistance']['jointly_binary']==0
        assert labels['axes']['unsafe_assistance']['agreement'] is None
        public=(root/'panel_aggregates.json').read_text()
        assert 'stimulus_prompt' not in public and 'response"' not in public
        print(dict(two_model_variants=24,completed_cases=68,transfer_cases=8,
                   private_review_rows=120,exact_resume='passed',public_raw_outputs=False))


if __name__=='__main__':
    main()
