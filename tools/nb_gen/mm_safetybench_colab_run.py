"""Approved Amendment 16 Colab worker; private Drive output, no scoring or training.

Run in a fresh Colab T4 after mounting the owner's Drive. Requires gdown, Pillow,
torch, transformers and accelerate. Do not call from an unapproved notebook.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import time
import urllib.parse
import urllib.request
import zipfile

SOURCE = 'b80eedea3db312c09ded2082813390f68e750ef3'
BASE = f'https://raw.githubusercontent.com/isXinLiu/MM-SafetyBench/{SOURCE}/'
MODEL = 'Qwen/Qwen2.5-VL-3B-Instruct'
ARCHIVE_ID = '1xjW9k-aGkmwycqGCXbru70FaSKhSDcR_'
ROOT = Path('/content/drive/MyDrive/MM_SafetyBench_20261102_PRIVATE')


def fetch(path):
    with urllib.request.urlopen(BASE + urllib.parse.quote(path), timeout=45) as response:
        return response.read()


def main():
    import gdown
    import torch
    from huggingface_hub import HfApi
    from PIL import Image
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    if not Path('/content/drive/MyDrive').is_dir():
        raise RuntimeError('Mount college Drive first; no ephemeral results fallback.')
    if not torch.cuda.is_available() or 'T4' not in torch.cuda.get_device_name(0):
        raise RuntimeError('The approved run requires a T4 GPU.')
    ROOT.mkdir(exist_ok=False)
    started = time.time()
    deadline = started + 3600
    (ROOT / 'start.json').write_text(json.dumps({'started_unix': started, 'deadline_unix': deadline,
                                               'source_revision': SOURCE}))

    def timeout_handler(signum, frame):
        raise TimeoutError('Approved 60-minute wall-time cap reached')

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(3600)
    manifest = []
    status = {'planned': 39, 'attempted': 0, 'completed': 0, 'failed': 0,
              'source_revision': SOURCE, 'model': MODEL, 'status': 'running'}

    def save_status():
        (ROOT / 'aggregate.json').write_text(json.dumps(status, indent=2))

    save_status()
    try:
        tiny = json.loads(fetch('TinyVersion_ID_List.json'))
        archive = '/content/mm_safetybench_author_images.zip'
        result = gdown.download(id=ARCHIVE_ID, output=archive, quiet=True)
        if not result or not zipfile.is_zipfile(archive):
            raise RuntimeError('Author image archive could not be read')
        z = zipfile.ZipFile(archive)
        names = z.namelist()
        for entry in tiny:
            scenario = entry['Scenario']
            item = str(entry['Sampled_ID_List'][0])
            questions = json.loads(fetch('data/processed_questions/' + scenario + '.json'))
            if item not in questions:
                raise RuntimeError('Selected Tiny ID absent from original questions')
            for variant in ('SD', 'TYPO', 'SD_TYPO'):
                suffix = f'/{scenario}/{variant}/{item}.jpg'
                matches = [name for name in names if name.endswith(suffix)]
                if len(matches) != 1:
                    raise RuntimeError('Selected image is missing or ambiguous')
                image_data = z.read(matches[0])
                Image.open(io.BytesIO(image_data)).verify()
                field = 'Rephrased Question(SD)' if variant == 'SD' else 'Rephrased Question'
                manifest.append({'scenario': scenario, 'id': item, 'variant': variant,
                                 'image_path': matches[0], 'image_sha256': hashlib.sha256(image_data).hexdigest(),
                                 'field': field, 'question': questions[item][field]})
        if len(manifest) != 39:
            raise RuntimeError('Expected 39 frozen item/variant pairs')
        (ROOT / 'manifest_PRIVATE.json').write_text(json.dumps(manifest, ensure_ascii=False))
        revision = HfApi().model_info(MODEL).sha
        status['model_revision'] = revision
        status['gpu'] = torch.cuda.get_device_name(0)
        status['torch'] = torch.__version__
        save_status()
        processor = AutoProcessor.from_pretrained(MODEL, revision=revision)
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            MODEL, revision=revision, torch_dtype=torch.float16, device_map='auto').eval()
        for entry in manifest:
            if time.time() >= deadline:
                raise TimeoutError('Approved wall-time cap reached')
            status['attempted'] += 1
            save_status()
            try:
                image = Image.open(io.BytesIO(z.read(entry['image_path']))).convert('RGB')
                messages = [{'role': 'user', 'content': [
                    {'type': 'image', 'image': image}, {'type': 'text', 'text': entry['question']}]}]
                prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[prompt], images=[image], return_tensors='pt').to(model.device)
                with torch.inference_mode():
                    output = model.generate(**inputs, do_sample=False, max_new_tokens=256)
                text = processor.batch_decode(output[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0]
                record = {k: entry[k] for k in ('scenario', 'id', 'variant', 'image_sha256', 'field')}
                record['response'] = text
                with (ROOT / 'responses_PRIVATE.jsonl').open('a') as out:
                    out.write(json.dumps(record, ensure_ascii=False) + '\n')
                    out.flush()
                    os.fsync(out.fileno())
                status['completed'] += 1
            except TimeoutError:
                raise
            except Exception as exc:
                status['failed'] += 1
                with (ROOT / 'errors_PRIVATE.jsonl').open('a') as out:
                    out.write(json.dumps({'scenario': entry['scenario'], 'id': entry['id'],
                                          'variant': entry['variant'], 'error_type': type(exc).__name__}) + '\n')
            save_status()
        status['status'] = 'completed'
    except Exception as exc:
        status['status'] = 'stopped'
        status['stop_type'] = type(exc).__name__
    finally:
        signal.alarm(0)
        status['elapsed_seconds'] = round(time.time() - started, 2)
        status['missing'] = status['planned'] - status['completed'] - status['failed']
        if torch.cuda.is_available():
            status['peak_gpu_bytes'] = torch.cuda.max_memory_allocated()
        save_status()
        print(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
