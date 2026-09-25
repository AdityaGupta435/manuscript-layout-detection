from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
import random


DATASET_DIR = Path("data/immi_raw/IMMI_dataset")
OUTPUT_DIR = Path("results")
OUTPUT_FILE = OUTPUT_DIR / "dataset_preview.jpg"

SAMPLES_PER_FOLDER = 3
THUMB_WIDTH = 250
THUMB_HEIGHT = 250
LABEL_HEIGHT = 45
COLUMNS = 3


def get_images(folder):
    extensions = {".jpg", ".jpeg", ".png"}

    return [
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in extensions
    ]


def create_thumbnail(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img.thumbnail((THUMB_WIDTH, THUMB_HEIGHT))

        canvas = Image.new(
            "RGB",
            (THUMB_WIDTH, THUMB_HEIGHT),
            "white"
        )

        x = (THUMB_WIDTH - img.width) // 2
        y = (THUMB_HEIGHT - img.height) // 2

        canvas.paste(img, (x, y))

        return canvas

    except Exception as e:
        print(f"Skipping {image_path}: {e}")
        return None


def main():

    OUTPUT_DIR.mkdir(exist_ok=True)

    folders = [
        p for p in DATASET_DIR.iterdir()
        if p.is_dir()
    ]

    selected = []

    random.seed(42)

    for folder in sorted(folders):

        images = get_images(folder)

        if not images:
            continue

        # Avoid rotated duplicates for initial visual inspection
        non_rotated = [
            p for p in images
            if not p.stem.lower().startswith("rotated_")
        ]

        if len(non_rotated) >= SAMPLES_PER_FOLDER:
            images = random.sample(
                non_rotated,
                SAMPLES_PER_FOLDER
            )
        else:
            images = random.sample(
                images,
                min(SAMPLES_PER_FOLDER, len(images))
            )

        for image in images:
            selected.append((folder.name, image))

    rows = math.ceil(len(selected) / COLUMNS)

    sheet_width = COLUMNS * THUMB_WIDTH
    sheet_height = rows * (THUMB_HEIGHT + LABEL_HEIGHT)

    sheet = Image.new(
        "RGB",
        (sheet_width, sheet_height),
        "white"
    )

    draw = ImageDraw.Draw(sheet)

    for index, (folder_name, image_path) in enumerate(selected):

        thumbnail = create_thumbnail(image_path)

        if thumbnail is None:
            continue

        row = index // COLUMNS
        col = index % COLUMNS

        x = col * THUMB_WIDTH
        y = row * (THUMB_HEIGHT + LABEL_HEIGHT)

        sheet.paste(thumbnail, (x, y))

        label = f"{folder_name}\n{image_path.name}"

        draw.text(
            (x + 5, y + THUMB_HEIGHT + 5),
            label,
            fill="black"
        )

    sheet.save(OUTPUT_FILE, quality=90)

    print(f"Preview created: {OUTPUT_FILE}")
    print(f"Samples included: {len(selected)}")


if __name__ == "__main__":
    main()