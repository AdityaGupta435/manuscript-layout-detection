from pathlib import Path
from PIL import Image, ImageDraw
import random
import math


DATASET_DIR = Path("data/immi_raw/IMMI_dataset/pdf_images")
OUTPUT = Path("results/pdf_images_preview.jpg")

SAMPLES = 18

THUMB_W = 300
THUMB_H = 250
LABEL_H = 55

COLUMNS = 3


def main():

    # Recursively find images
    images = [
        p for p in DATASET_DIR.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        and not p.stem.lower().startswith("rotated_")
    ]

    print(f"Total usable images: {len(images)}")

    if not images:
        print("No images found.")
        return

    random.seed(42)

    samples = random.sample(
        images,
        min(SAMPLES, len(images))
    )

    rows = math.ceil(len(samples) / COLUMNS)

    sheet = Image.new(
        "RGB",
        (
            COLUMNS * THUMB_W,
            rows * (THUMB_H + LABEL_H)
        ),
        "white"
    )

    draw = ImageDraw.Draw(sheet)

    for i, path in enumerate(samples):

        try:
            image = Image.open(path).convert("RGB")

            image.thumbnail(
                (THUMB_W - 10, THUMB_H - 10)
            )

            x = (i % COLUMNS) * THUMB_W
            y = (i // COLUMNS) * (THUMB_H + LABEL_H)

            ix = x + (THUMB_W - image.width) // 2
            iy = y + (THUMB_H - image.height) // 2

            sheet.paste(image, (ix, iy))

            # Show subfolder + filename
            relative = path.relative_to(DATASET_DIR)

            label = str(relative)

            draw.text(
                (x + 5, y + THUMB_H + 5),
                label,
                fill="black"
            )

        except Exception as e:
            print(f"Could not read {path}: {e}")

    OUTPUT.parent.mkdir(exist_ok=True)

    sheet.save(
        OUTPUT,
        quality=90
    )

    print(f"Created: {OUTPUT}")
    print(f"Images shown: {len(samples)}")


if __name__ == "__main__":
    main()