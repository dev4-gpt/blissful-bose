# Native LLaVA setup validated by a four-condition benign smoke.
import json

CHECKPOINT_SETUP = r"""# *** -------
# Stage the upstream checkpoints in this runtime before offline generation.
import os, subprocess, sys
from pathlib import Path

WEIGHTS = CLIP_SNAPSHOT = None
stage_script = '''
import json
from huggingface_hub import snapshot_download
llava = snapshot_download("liuhaotian/llava-v1.5-7b", allow_patterns=["*.json", "*.model", "pytorch_model*.bin"])
clip = snapshot_download("openai/clip-vit-large-patch14-336", allow_patterns=["*.json", "model.safetensors", "pytorch_model.bin"])
print(json.dumps([llava, clip]))
'''
import json
staged = subprocess.check_output([sys.executable, "-c", stage_script],
    env={**os.environ, "HF_HUB_OFFLINE": "0"}, text=True, timeout=7200)
WEIGHTS, CLIP_SNAPSHOT = map(Path, json.loads(staged.strip().splitlines()[-1]))
os.environ["HF_HUB_OFFLINE"] = "1"
print("LLaVA snapshot:", WEIGHTS)
print("CLIP snapshot:", CLIP_SNAPSHOT)"""

SOURCE_SETUP = r"""# *** -------
# Pin the upstream native adapter before attempting generation.
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import subprocess, sys

LLAVA_COMMIT = "c121f0432da27facab705978f83c4ada465e46fd"
LLAVA_CHECKOUT = Path("/content/LLaVA")
llava_upstream = "https://github.com/haotian-liu/LLaVA.git"
if not LLAVA_CHECKOUT.exists():
    subprocess.run(["git", "init", str(LLAVA_CHECKOUT)], check=True, timeout=30)
if not (LLAVA_CHECKOUT / ".git").is_dir():
    raise RuntimeError("Existing LLaVA path is not a Git checkout")
git = ["git", "-C", str(LLAVA_CHECKOUT)]
head = subprocess.run([*git, "rev-parse", "--verify", "HEAD"], capture_output=True, text=True)
if head.returncode:
    if any(p.name != ".git" for p in LLAVA_CHECKOUT.iterdir()):
        raise RuntimeError("Refusing to overwrite existing LLaVA files")
    subprocess.run([*git, "fetch", "--depth", "1", llava_upstream, LLAVA_COMMIT], check=True, timeout=120)
    subprocess.run([*git, "checkout", "--detach", LLAVA_COMMIT], check=True, timeout=30)
elif head.stdout.strip() != LLAVA_COMMIT:
    raise RuntimeError("Existing LLaVA checkout differs from the pinned revision")
if subprocess.check_output([*git, "status", "--porcelain"], text=True).strip():
    raise RuntimeError("The native LLaVA checkout has local edits")
if str(LLAVA_CHECKOUT) not in sys.path:
    sys.path.insert(0, str(LLAVA_CHECKOUT))
print("Native LLaVA source:", LLAVA_COMMIT)
print("Python:", sys.version.split()[0])
for package in ("torch", "transformers", "accelerate", "sentencepiece", "shortuuid"):
    try:
        print(package, version(package))
    except PackageNotFoundError:
        print(package, "not installed")"""

ENVIRONMENT_SETUP = r"""# *** -------
# Native Transformers 4.37 uses tokenizers 0.15; isolate it from Colab's Python 3.13.
import os, shutil, subprocess, sys, time
from pathlib import Path

if RUN_INFERENCE and LLAVA_SMOKE:
    if not OWNER_APPROVAL_RECORD or not GPU_MINUTES or GPU_MINUTES <= 0:
        raise RuntimeError("The LLaVA smoke test needs an approved time budget")
    LLAVA_ENV_DEADLINE = time.monotonic() + GPU_MINUTES * 60
    llava_env = Path("/content/llava-native-311")
    LLAVA_PYTHON = llava_env / "bin/python"
    ready = llava_env / ".mm_safetybench_ready_v1"
    def llava_setup_call(command):
        subprocess.run(command, check=True, timeout=max(1, LLAVA_ENV_DEADLINE - time.monotonic()))
    if not ready.is_file():
        uv = shutil.which("uv")
        if not uv:
            llava_setup_call([sys.executable, "-m", "pip", "install", "uv"])
            uv = shutil.which("uv")
        if not uv:
            raise RuntimeError("Could not locate uv after installation")
        if not LLAVA_PYTHON.is_file():
            llava_setup_call([uv, "venv", "--python", "3.11", str(llava_env)])
        installer = [uv, "pip", "install", "--python", str(LLAVA_PYTHON)]
        llava_setup_call([*installer, "--index-url", "https://download.pytorch.org/whl/cu124",
                          "torch==2.6.0", "torchvision==0.21.0"])
        llava_setup_call([*installer, "transformers==4.37.2", "tokenizers==0.15.1",
                          "accelerate==0.27.2", "huggingface-hub==0.36.2", "numpy<2",
                          "sentencepiece==0.1.99", "protobuf", "shortuuid", "einops"])
        ready.touch()
    print("Isolated LLaVA interpreter:", LLAVA_PYTHON, flush=True)"""

SMOKE_RUNNER = r"""if RUN_INFERENCE:
    if not all(p and Path(p).is_dir() for p in (WEIGHTS, CLIP_SNAPSHOT)):
        raise RuntimeError("Run the checkpoint staging cell first")
    if not LLAVA_COMMIT or not (LLAVA_CHECKOUT / "llava/model/builder.py").is_file():
        raise RuntimeError("Run the pinned native source setup cell first")
    provenance = dict(checkpoint=LLAVA_MODEL, llava_commit=LLAVA_COMMIT, weights=str(WEIGHTS),
                      placement="fp16_auto_10gib_v1",
                      clip_snapshot=str(CLIP_SNAPSHOT), max_new_tokens=512, do_sample=False, num_beams=1)
    if LLAVA_SMOKE:
        import inspect, time, sys
        if not globals().get("LLAVA_PYTHON") or not LLAVA_PYTHON.is_file():
            raise RuntimeError("Run the isolated LLaVA environment cell first")
        remaining = min(15 * 60, LLAVA_ENV_DEADLINE - time.monotonic())
        if remaining <= 0:
            raise RuntimeError("The approved LLaVA smoke budget has elapsed")
        worker = "import os, re, json, subprocess, sys\nfrom pathlib import Path\nfrom hashlib import sha256\nfrom io import BytesIO\nfrom zipfile import ZipFile\n"
        config = dict(LLAVA_SIZE=LLAVA_SIZE, LLAVA_MODEL=LLAVA_MODEL, LLAVA_COMMIT=LLAVA_COMMIT,
                      FIELDS=FIELDS, AUTHOR_SHA=AUTHOR_SHA, OWNER_APPROVAL_RECORD=OWNER_APPROVAL_RECORD,
                      GPU_MINUTES=remaining / 60, provenance=provenance)
        worker += "globals().update(" + repr(config) + ")\n"
        for var, path in dict(LLAVA_CHECKOUT=LLAVA_CHECKOUT, WEIGHTS=WEIGHTS,
                              CLIP_SNAPSHOT=CLIP_SNAPSHOT, OUT=OUT).items():
            worker += f"{var} = Path({str(path)!r})\n"
        worker += "sys.path.insert(0, str(LLAVA_CHECKOUT))\n"
        for fn in (key, manifest_hash, load_llava, generate_llava, atomic_json,
                   append_private, smoke_cases, execute):
            worker += "\n" + inspect.getsource(fn) + "\n"
        worker += "\nimport torch, transformers\n"
        worker += "provenance.update(torch=torch.__version__, transformers=transformers.__version__, python=sys.version.split()[0])\n"
        worker += "execute([], OUT, load_llava, generate_llava, provenance, True)\n"
        compile(worker, "<isolated LLaVA smoke>", "exec")
        subprocess.run([str(LLAVA_PYTHON), "-u", "-c", worker], check=True,
                       env={**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"},
                       timeout=remaining)
    else:
        if os.getenv("HF_HUB_OFFLINE") != "1":
            raise RuntimeError("Prepare the approved offline full-run environment first")
        execute(cases, OUT, load_llava, generate_llava, provenance, False)"""

def attach_native_smoke_environment(root):
    path = root / "notebooks" / "mm_safetybench_llava_7b.ipynb"
    nb = json.loads(path.read_text())
    for i, cell in enumerate(nb["cells"]):
        source = "".join(cell["source"])
        if cell["cell_type"] == "code" and "def execute(" in source:
            body = source.split("\nif RUN_INFERENCE:\n", 1)[0]
            cell["source"] = (body + "\n" + SMOKE_RUNNER).splitlines(True)
            setup = [dict(cell_type="code", metadata={}, execution_count=None,
                          outputs=[], source=s.splitlines(True))
                     for s in (CHECKPOINT_SETUP, SOURCE_SETUP, ENVIRONMENT_SETUP)]
            nb["cells"][i:i] = setup
            break
    else:
        raise RuntimeError("No native LLaVA runner cell found")
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
