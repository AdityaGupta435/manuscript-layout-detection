from pathlib import Path
import random
import shutil

ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = ROOT / "data" / "raw"
LABEL_DIR = ROOT / "data" / "annotations" / "labels"
YOLO_DIR = ROOT / "data" / "yolo"

TRAIN_IMAGE_DIR = YOLO_DIR / "images" / "train"
VAL_IMAGE_DIR = YOLO_DIR / "images" / "val"

TRAIN_LABEL_DIR = YOLO_DIR / "labels" / "train"
VAL_LABEL_DIR = YOLO_DIR / "labels" / "val"

random.seed(42)

image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

images = sorted(
    [
        p for p in IMAGE_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in image_extensions
    ]
)

random.shuffle(images)

split_index = int(len(images) * 0.8)

train_images = images[:split_index]
val_images = images[split_index:]

for image_path in train_images:
    label_path = LABEL_DIR / f"{image_path.stem}.txt"

    shutil.copy2(
        image_path,
        TRAIN_IMAGE_DIR / image_path.name
    )

    shutil.copy2(
        label_path,
        TRAIN_LABEL_DIR / label_path.name
    )

for image_path in val_images:
    label_path = LABEL_DIR / f"{image_path.stem}.txt"

    shutil.copy2(
        image_path,
        VAL_IMAGE_DIR / image_path.name
    )

    shutil.copy2(
        label_path,
        VAL_LABEL_DIR / label_path.name
    )

print("=" * 50)
print("YOLO DATASET PREPARED")
print("=" * 50)
print(f"Total images : {len(images)}")
print(f"Train images : {len(train_images)}")
print(f"Val images   : {len(val_images)}")
print("=" * 50)