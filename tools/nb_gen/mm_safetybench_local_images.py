def stage_local_images():
    """Copy one archive from Drive, then read images from the VM disk."""
    import shutil
    import tempfile
    import time
    global IMAGE_DIR
    if not IMAGE_ZIP.is_file():
        raise FileNotFoundError(f"The image ZIP is required for local staging: {IMAGE_ZIP}")
    stage = Path(tempfile.mkdtemp(prefix="mm_safetybench_images_", dir="/content"))
    local_zip = stage / "images.zip"
    total = IMAGE_ZIP.stat().st_size
    copied = 0
    started = time.monotonic()
    print(f"Copying image ZIP to VM disk ({total / 2**20:.1f} MiB).", flush=True)
    with IMAGE_ZIP.open("rb") as source, local_zip.open("wb") as target:
        while chunk := source.read(8 * 2**20):
            target.write(chunk)
            copied += len(chunk)
            if copied % (64 * 2**20) == 0 or copied == total:
                print(f"ZIP copy: {copied / 2**20:.0f}/{total / 2**20:.0f} MiB", flush=True)
    if copied != total:
        raise RuntimeError("The image archive copy was incomplete")
    image_root = stage / "images"
    prefix = "MM-SafetyBench(imgs)/"
    with ZipFile(local_zip) as archive:
        files = [info for info in archive.infolist()
                 if not info.is_dir() and info.filename.lower().endswith(".jpg")]
        for i, info in enumerate(files, 1):
            if not info.filename.startswith(prefix):
                raise ValueError("Unexpected image archive root")
            relative = Path(info.filename[len(prefix):])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unsafe archive member path")
            destination = image_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
            if i % 500 == 0 or i == len(files):
                print(f"Local extraction: {i}/{len(files)} images", flush=True)
    IMAGE_DIR = image_root
    print(f"Local images ready in {time.monotonic() - started:.1f}s: {IMAGE_DIR}", flush=True)


def image_hash(images, rows):
    if isinstance(images, ZipFile):
        return digest(IMAGE_ZIP)
    names = sorted(row["image_path"] for row in rows if row["image_path"])
    hashes = []
    for i, name in enumerate(names, 1):
        hashes.append((name, sha256(images.read(name)).hexdigest()))
        if i % 500 == 0 or i == len(names):
            print(f"Fingerprinting local images: {i}/{len(names)}", flush=True)
    return manifest_hash(hashes)
