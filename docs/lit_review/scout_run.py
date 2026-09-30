import sys, json, time
sys.path.insert(0, '.')
from services.search import AcademicSearchService
s = AcademicSearchService()
queries = [
 "continual safety alignment fine-tuning",
 "safety alignment degradation vision-language models fine-tuning",
 "safety alignment vision language models",
 "gradient-based data selection safety fine-tuning",
 "benign fine-tuning compromises safety alignment",
 "catastrophic forgetting safety vision-language models continual learning",
 "multimodal jailbreak benchmark vision language model",
 "safety basin fine-tuning LLM",
 "LoRA safety subspace preserving alignment during fine-tuning",
 "over-refusal vision language models safety",
 "model merging safety alignment restoration",
 "continual instruction tuning multimodal large language models",
]
out = {}
for q in queries:
    t=time.time()
    try:
        r = s.run_combined_search(q, limit=8)
    except Exception as e:
        r = [{"error": repr(e)}]
    out[q] = r
    print(f"{q!r}: {len(r)} results in {time.time()-t:.0f}s", flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1, default=str)
