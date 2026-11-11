"""Amendment 17: resumable full author-image evaluation; unscored, private."""
import hashlib
import io
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request
import zipfile

SOURCE = 'b80eedea3db312c09ded2082813390f68e750ef3'
MODEL = 'Qwen/Qwen2.5-VL-3B-Instruct'
REVISION = '66285546d2b821cf421d4f5eb2576359d3770cd3'
BASE = f'https://raw.githubusercontent.com/isXinLiu/MM-SafetyBench/{SOURCE}/'
ROOT = Path('/content/drive/MyDrive/MM_SafetyBench_Full_20261102_PRIVATE')
ZIP_PATH = Path('/content/mm_safetybench_author_images.zip')
CONFIG = {'source': SOURCE, 'model': MODEL, 'revision': REVISION, 'precision': 'float16',
          'sampling': 'greedy', 'max_new_tokens': 256, 'mapping': 'author-readme',
          'variants': ['SD', 'TYPO', 'SD_TYPO'], 'expected_items': 1680}


def get(path):
    with urllib.request.urlopen(BASE + urllib.parse.quote(path), timeout=45) as r:
        return r.read()


def atomic(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False))
    os.replace(temp, path)


def load_records(path):
    if not path.exists():
        return []
    with path.open() as f:
        return [json.loads(line) for line in f]


def main():
    import gdown
    import torch
    import transformers
    from PIL import Image
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    if not Path('/content/drive/MyDrive').is_dir():
        raise RuntimeError('Drive must be mounted before execution')
    if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
        raise RuntimeError('Expected T4 GPU')
    ROOT.mkdir(exist_ok=True)
    config_path = ROOT / 'config.json'
    if config_path.exists():
        if json.loads(config_path.read_text()) != CONFIG:
            raise RuntimeError('Configuration mismatch: refusing to resume')
    else:
        atomic(config_path, CONFIG)
    tiny = json.loads(get('TinyVersion_ID_List.json'))
    scenarios = [entry['Scenario'] for entry in tiny]
    if len(scenarios) != 13 or len(set(scenarios)) != 13:
        raise RuntimeError('Scenario inventory mismatch')
    if not ZIP_PATH.exists():
        gdown.download(id='1xjW9k-aGkmwycqGCXbru70FaSKhSDcR_', output=str(ZIP_PATH), quiet=True)
    if not zipfile.is_zipfile(ZIP_PATH):
        raise RuntimeError('Original archive not available or invalid')
    z = zipfile.ZipFile(ZIP_PATH)
    zip_names = z.namelist()
    manifest = []
    for scenario in scenarios:
        questions = json.loads(get('data/processed_questions/' + scenario + '.json'))
        for item, question in questions.items():
            for variant in CONFIG['variants']:
                field = 'Rephrased Question(SD)' if variant == 'SD' else 'Rephrased Question'
                suffix = f'/{scenario}/{variant}/{item}.jpg'
                matches = [n for n in zip_names if n.endswith(suffix)]
                manifest.append({'scenario': scenario, 'id': str(item), 'variant': variant,
                                 'field': field, 'question': question[field],
                                 'image_path': matches[0] if len(matches) == 1 else None})
    if len(manifest) != 5040:
        raise RuntimeError('Question count mismatch: refusing incomplete dataset')
    manifest_path = ROOT / 'manifest_PRIVATE.json'
    digest = hashlib.sha256(json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    digest_path = ROOT / 'manifest_sha256.txt'
    if digest_path.exists() and digest_path.read_text() != digest:
        raise RuntimeError('Manifest changed: refusing to resume')
    if not digest_path.exists():
        atomic(manifest_path, manifest)
        digest_path.write_text(digest)

    result_path = ROOT / 'responses_PRIVATE.jsonl'
    failures_path = ROOT / 'failures_PRIVATE.jsonl'
    prior = load_records(result_path)
    key = lambda x: (x['scenario'], x['id'], x['variant'])
    done = {key(x) for x in prior}
    if len(done) != len(prior):
        raise RuntimeError('Duplicate completed keys: refusing to resume')
    attempts = load_records(failures_path)
    # Failures remain in the ledger; an interrupted case may be retried on resume.
    status = {'planned': 5040, 'completed': len(done), 'failure_attempts': len(attempts),
              'model_revision': REVISION, 'source_revision': SOURCE, 'manifest_sha256': digest,
              'torch': torch.__version__, 'transformers': transformers.__version__, 'status': 'running'}
    atomic(ROOT / 'aggregate.json', status)
    processor = AutoProcessor.from_pretrained(MODEL, revision=REVISION)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL, revision=REVISION, torch_dtype=torch.float16, device_map='auto').eval()
    try:
        for case in manifest:
            if key(case) in done:
                continue
            try:
                if case['image_path'] is None:
                    raise FileNotFoundError('missing or ambiguous archive image')
                image_bytes = z.read(case['image_path'])
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                messages = [{'role': 'user', 'content': [
                    {'type': 'image', 'image': image}, {'type': 'text', 'text': case['question']}]}]
                prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[prompt], images=[image], return_tensors='pt').to(model.device)
                with torch.inference_mode():
                    output = model.generate(**inputs, do_sample=False, max_new_tokens=256)
                response = processor.batch_decode(output[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0]
                row = {k: case[k] for k in ('scenario', 'id', 'variant', 'field')}
                row.update(image_sha256=hashlib.sha256(image_bytes).hexdigest(), response=response)
                with result_path.open('a') as f:
                    f.write(json.dumps(row, ensure_ascii=False) + '\n')
                    f.flush()
                    os.fsync(f.fileno())
                done.add(key(case))
                status['completed'] = len(done)
            except Exception as exc:
                row = {k: case[k] for k in ('scenario', 'id', 'variant')}
                row.update(error_type=type(exc).__name__, timestamp=time.time())
                with failures_path.open('a') as f:
                    f.write(json.dumps(row) + '\n')
                    f.flush()
                    os.fsync(f.fileno())
                status['failure_attempts'] += 1
            status['remaining'] = 5040 - len(done)
            atomic(ROOT / 'aggregate.json', status)
        status['status'] = 'completed_pass'
    finally:
        status['remaining'] = 5040 - len(done)
        atomic(ROOT / 'aggregate.json', status)
        print(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
