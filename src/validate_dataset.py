from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = ROOT / "data" / "raw"
LABEL_DIR = ROOT / "data" / "annotations" / "labels"

VALID_CLASSES = {0, 1, 2, 3, 4}

image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

images = {
    p.stem: p
    for p in IMAGE_DIR.iterdir()
    if p.is_file() and p.suffix.lower() in image_extensions
}

labels = {
    p.stem: p
    for p in LABEL_DIR.glob("*.txt")
}

print("=" * 60)
print("MANUSCRIPT DATASET VALIDATION")
print("=" * 60)

print(f"Images found : {len(images)}")
print(f"Labels found : {len(labels)}")

errors = []

# --------------------------------------------------
# 1. Image ↔ Label matching
# --------------------------------------------------

missing_labels = sorted(set(images) - set(labels))
extra_labels = sorted(set(labels) - set(images))

if missing_labels:
    print("\nMissing label files:")
    for name in missing_labels:
        print("  ", name)
        errors.append(f"Missing label: {name}")

if extra_labels:
    print("\nExtra label files:")
    for name in extra_labels:
        print("  ", name)
        errors.append(f"Extra label: {name}")

# --------------------------------------------------
# 2. Validate every label
# --------------------------------------------------

total_boxes = 0

for stem, label_path in sorted(labels.items()):

    try:
        image_path = images[stem]

        with Image.open(image_path) as img:
            image_width, image_height = img.size

    except Exception as e:
        errors.append(f"{stem}: image error - {e}")
        continue

    lines = label_path.read_text(encoding="utf-8").splitlines()

    for line_number, line in enumerate(lines, start=1):

        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) != 5:
            errors.append(
                f"{stem}: line {line_number} must contain 5 values"
            )
            continue

        try:
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])

        except ValueError:
            errors.append(
                f"{stem}: line {line_number} contains invalid numbers"
            )
            continue

        # Class validation
        if class_id not in VALID_CLASSES:
            errors.append(
                f"{stem}: line {line_number} invalid class {class_id}"
            )

        # Coordinate validation
        values = [x_center, y_center, width, height]

        if any(value < 0 or value > 1 for value in values):
            errors.append(
                f"{stem}: line {line_number} coordinate outside 0-1"
            )

        # Width / height must be positive
        if width <= 0 or height <= 0:
            errors.append(
                f"{stem}: line {line_number} has non-positive size"
            )

        # Bounding box boundary validation
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2

        if x1 < 0 or y1 < 0 or x2 > 1 or y2 > 1:
            errors.append(
                f"{stem}: line {line_number} bounding box outside image"
            )

        total_boxes += 1

# --------------------------------------------------
# 3. Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

print(f"Images       : {len(images)}")
print(f"Labels       : {len(labels)}")
print(f"Total boxes  : {total_boxes}")
print(f"Errors       : {len(errors)}")

if errors:
    print("\n❌ VALIDATION FAILED\n")

    for error in errors:
        print(" -", error)

else:
    print("\n✅ VALIDATION PASSED")
    print("All annotations are valid YOLO format.")
    print("All classes are within 0-4.")
    print("All coordinates are within image boundaries.")