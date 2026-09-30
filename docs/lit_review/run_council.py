import os, sys, json, time
os.environ["RESEARCHINGOS_RUN_MODE"]="live"          # never fall back to mock papers
BACKEND="/Users/aryamandev/Developer/ResearchingOS/backend"
sys.path.insert(0,BACKEND); os.chdir(BACKEND)
OUT=sys.argv[1]; topic=sys.argv[2]; maxp=int(sys.argv[3])
from agents.council import CouncilOrchestrator
orch=CouncilOrchestrator(vault_path=f"{OUT}/vault", memory_file_path=f"{OUT}/memory.json")
logs=[]
def cb(d):
    logs.append(d); print(f"[{d.get('stage')}] {d.get('agent')}: {str(d.get('message'))[:230]}",flush=True)
t=time.time()
res=orch.run_debate_only(topic,cb,max_papers=maxp)
print("RESULT:",json.dumps(res,default=str)[:600]); print("elapsed s:",round(time.time()-t))
json.dump(logs,open(f"{OUT}/logs.json","w"),indent=1,default=str)
