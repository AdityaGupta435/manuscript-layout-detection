from pathlib import Path
from PIL import Image, ImageDraw
import math


RAW_DIR = Path("data/raw")
OUTPUT = Path("results/selected_dataset_preview.jpg")

THUMB_W = 280
THUMB_H = 220
LABEL_H = 45

COLUMNS = 3


def main():

    images = sorted([
        p for p in RAW_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ])

    print(f"Images found: {len(images)}")

    if not images:
        print("No images found.")
        return

    rows = math.ceil(len(images) / COLUMNS)

    sheet = Image.new(
        "RGB",
        (
            COLUMNS * THUMB_W,
            rows * (THUMB_H + LABEL_H)
        ),
        "white"
    )

    draw = ImageDraw.Draw(sheet)

    for i, path in enumerate(images):

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

            draw.text(
                (x + 5, y + THUMB_H + 5),
                path.name,
                fill="black"
            )

        except Exception as e:
            print(f"Could not read {path}: {e}")

    OUTPUT.parent.mkdir(exist_ok=True)

    sheet.save(OUTPUT, quality=90)

    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()