"""Generate a private-output, free-Colab JIP encoder notebook; GPU remains opt-in."""
import json
from pathlib import Path
import nbformat

ROOT=Path(__file__).resolve().parents[2]


def build():
    md=nbformat.v4.new_markdown_cell
    code=nbformat.v4.new_code_cell
    cells=[md('''# Jailbreak in Pieces: released encoder example — Colab T4

**28 October 2026 · Prepared, NOT RUN · No paid GPU.**

This notebook reproduces the structure of the authors' released visual-trigger
encoder optimization. It does not reproduce every trigger branch, the downstream
VLM experiment or the paper's ASR table. The code is a disclosed reimplementation
of the inspected loop, not unchanged execution of their script.

Primary environment: free Colab T4. Kaggle is a possible separate free fallback
after private preservation, quota checks and an explicit remaining-budget decision.
Do not reset or delete an existing runtime. Do not upgrade to paid compute.

Default Run all performs no installs, downloads or GPU work. The amendment and
60-minute cap require owner acceptance before enabling execution.'''),
    md('''## 1. What is being reproduced?

[Paper §§3–4 / Algorithm 1](https://arxiv.org/html/2307.14539v2)
and [pinned original encoder code](https://github.com/erfanshayegani/Jailbreak-In-Pieces/blob/b7b2bce812adada23f583f63f63e564f84d277c6/src/adv_image.py).

Released visual target and white initialization → original processor without
normalization → CLIP ViT-L/14-336 → Euclidean feature distance → Adam pixel
updates → box clamping → JPEG → save/reload evaluation.

The target and initialization come from the official release and are hash-checked.
No substitute images, newly constructed prompts or invented test outcomes are used.'''),
    md(r'''## 2. Mathematical contract

Let $x_0$ be the released initialization and $z_t=E(P(x_t))$ the released visual
target's feature. Optimize $L(x)=\operatorname{PairwiseDistance}_2(E(P(x)),z_t)$.
Here the released processor disables normalization; the helper follows that choice.
Its input tensor is the optimization variable; preprocessing is applied before it.

Adam updates the image, then $x\leftarrow\operatorname{clip}(x,0,1)$, with learning
rate 0.1. The target embedding is fixed. Use raw CLIP features and PyTorch's original
PairwiseDistance defaults. Do not replace this with cosine loss or unit-normalized
features. All CLIP weights remain fixed.

Profile: 50 updates. If valid and projected affordable, independently restart from
the original initialization for the released 5000 updates. A short profile is not
the full released-length run. Lower feature distance is not jailbreak success.'''),
    code('''from pathlib import Path
import json, sys, time, hashlib, subprocess, shutil
RUN_APPROVED = False
ACCEPTED_PROTOCOL = ""  # Set only after the owner accepts Amendment 13 and its cap.
PROTOCOL_TOKEN = "AMENDMENT_13_JIP_ENCODER_60_MIN_FREE_ONLY"
ATTEMPT_FOLDER = "JIP_ENCODER_20261028_ATTEMPT01_PRIVATE"
print("Prepared; GPU/download execution:", RUN_APPROVED)
'''),
    md('''## 3. Connect private persistent storage

The owner clicks the Drive authorization. Mount only when execution is approved.
The persistent clock starts in the following execution cell, before installation.
An existing attempt folder/clock is preserved: choose no new attempt without an
explicit budget decision. This notebook does not overwrite completed evidence.'''),
    code('''ROOT_PRIVATE = None
if RUN_APPROVED:
    if ACCEPTED_PROTOCOL != PROTOCOL_TOKEN:
        raise ValueError("Owner acceptance of the exact amendment/cap is required")
    from google.colab import drive
    drive.mount('/content/drive')
    drive_root = Path('/content/drive/MyDrive')
    if not drive_root.is_dir():
        raise RuntimeError("Private Drive mount not available")
    ROOT_PRIVATE = drive_root / ATTEMPT_FOLDER
else:
    print("No Drive authorization, network access or model execution requested.")
'''),
    md('''## 4. Reviewed helper source

This is ordinary inspectable Python. The next cell stores it as a string without
executing it. Source/model/data manifests and artifacts are written privately only
after approval. Model revision is resolved and recorded before weight loading.
The original paper-era model/environment identity remains unresolved.'''),
    code('HELPER_SOURCE = '+repr((ROOT/'tools/vlm_jip_encoder.py').read_text())+'\nprint("Helper prepared; source SHA256:", hashlib.sha256(HELPER_SOURCE.encode()).hexdigest())'),
    md('''## 5. Bounded execution — starts one 60-minute clock

Select a T4 under Runtime → Change runtime type before this cell; check free quota
and account settings yourself. No paid service is called by this notebook.

Installation and model execution run in child processes with the remaining wall
budget. A five-minute preservation reserve is withheld. The fixed profile and
release-length stage share one clock; failure never restarts it. Source identity,+processor settings, software versions, actual GPU, frozen weights and loss traces
are recorded. No downstream VLM or safety-request generation runs here.'''),
    code('''if RUN_APPROVED:
    import importlib.util
    helper_path = ROOT_PRIVATE / 'vlm_jip_encoder_PRIVATE.py'
    ROOT_PRIVATE.mkdir(parents=True, exist_ok=True)
    if (ROOT_PRIVATE/'attempt_clock_PRIVATE.json').exists():
        raise RuntimeError("Existing clock preserved; do not reset or replay this attempt")
    helper_path.write_text(HELPER_SOURCE)
    spec = importlib.util.spec_from_file_location('jip_encoder_private', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    state = helper.start(ROOT_PRIVATE, ACCEPTED_PROTOCOL, 'colab_free_t4')
    log_path = ROOT_PRIVATE/'execution_PRIVATE.log'
    outcome = {'status':'started', 'asr':'NOT_MEASURED'}
    def remaining():
        budget = state['deadline']-time.time()-300
        if budget <= 0:
            raise TimeoutError('No execution budget remains after preservation reserve')
        return budget
    try:
        with log_path.open('w') as log:
            subprocess.run([sys.executable,'-m','pip','install','--quiet',
                'transformers==4.57.1','huggingface-hub>=0.34,<1','Pillow','numpy'],
                stdout=log,stderr=subprocess.STDOUT,check=True,timeout=remaining())
            command = ('import sys,json; from pathlib import Path; '
                'sys.path.insert(0,sys.argv[1]); '
                'import vlm_jip_encoder_PRIVATE as j; '
                'r=Path(sys.argv[1]); s=json.loads((r/"attempt_clock_PRIVATE.json").read_text()); '
                'j.run(r,s)')
            subprocess.run([sys.executable,'-c',command,str(ROOT_PRIVATE)],
                stdout=log,stderr=subprocess.STDOUT,check=True,timeout=remaining())
        outcome['status'] = 'encoder_process_complete_requires_review'
    except (subprocess.TimeoutExpired, TimeoutError) as error:
        outcome.update(status='budget_stopped_incomplete',error_type=type(error).__name__)
    except Exception as error:
        outcome.update(status='failed_requires_review',error_type=type(error).__name__)
    finally:
        outcome.update(finished=time.time(),elapsed_seconds=time.time()-state['started'])
        helper.save(ROOT_PRIVATE/'controller_status_PRIVATE.json',outcome)
        state.update(status=outcome['status'],finished=outcome['finished'])
        helper.save(ROOT_PRIVATE/'attempt_clock_PRIVATE.json',state)
        archive = Path(shutil.make_archive(str(ROOT_PRIVATE)+'_PRESERVED_PRIVATE','zip',ROOT_PRIVATE))
        preservation = dict(archive_name=archive.name,bytes=archive.stat().st_size,
                            sha256=helper.sha(archive),status=outcome['status'])
        helper.save(ROOT_PRIVATE.parent/(ROOT_PRIVATE.name+'_PRESERVATION_PRIVATE.json'),preservation)
    print(json.dumps(outcome,indent=2))
else:
    print("NOT_RUN. No package installation, checkpoint download or GPU allocation initiated.")
'''),
    md('''## 6. Read the actual encoder results

The following cell displays scalar engineering outcomes only. Keep target/optimized
images and source content private. Failure or no improvement must be reported.
Compare tensor-space and JPEG-reloaded distance; delivery can change the objective.
The original 50 and 5000 updates are two stages, not two independent test cases.'''),
    code('''if RUN_APPROVED and ROOT_PRIVATE is not None:
    summary = ROOT_PRIVATE/'encoder_summary_PRIVATE.json'
    if summary.exists():
        evidence = json.loads(summary.read_text())
        print(json.dumps(evidence['results'],indent=2))
        print('Frozen weights unchanged:',evidence['identity']['weights_unchanged'])
    else:
        print('No complete encoder summary. Inspect the private status/log; ASR is NOT_MEASURED.')
else:
    print('Original-paper results: NOT_RUN; downstream ASR: NOT_MEASURED')
'''),
    md('''## 7. Editable interpretation after the run

**Observed:** fill only from saved scalar results and completion records.

**Fidelity:** released inputs/code identity, resolved checkpoint, actual processor,
library/precision differences, implementation changes, 50/5000 completion and JPEG effect.

**Limits:** one released visual-trigger example; no full trigger/scenario coverage,
no downstream behavior evaluation, no safety ASR or human validation. Current model
revision is not proof of original historical checkpoint equivalence.

**Next step:** review private artifacts and measured cost, then prepare original-compatible
downstream evaluation separately. Preserve this notebook with actual outputs on Drive
before another stage. Kaggle fallback requires private storage, verified free quota and
a remaining-budget decision; it is not an automatic additional attempt.'''),
    md('## Appendix: reviewable Amendment 13 draft\n\n'+(ROOT/'docs/JIP_FREE_T4_REPRODUCTION_PROTOCOL.md').read_text())]
    notebook=nbformat.v4.new_notebook(cells=cells,metadata={
        'kernelspec':{'name':'python3','display_name':'Python 3'},
        'accelerator':'GPU','colab':{'name':'vlm_jip_free_t4.ipynb','gpuType':'T4'},
        'scientific_run_status':'NOT_RUN','paid_compute_allowed':False})
    nbformat.validate(notebook)
    for cell in cells:
        if cell.cell_type=='code': compile(cell.source,'<generated-cell>','exec')
    path=ROOT/'notebooks/vlm_jip_free_t4.ipynb'
    path.write_text(json.dumps(notebook,ensure_ascii=False,separators=(',',':')))
    print(path,len(cells),'cells; code syntax passed; no GPU run')


if __name__=='__main__':build()
