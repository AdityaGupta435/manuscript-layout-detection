from pathlib import Path
from PIL import Image, ImageDraw
import random
import math


DATASET_DIR = Path("data/immi_raw/IMMI_dataset")
OUTPUT_DIR = Path("results")

FOLDERS = [
    "ASR_Images",
    "Bhoomi_data",
    "Jain_manuscripts",
    "jain-mscripts",
    "penn-in-hand",
    "penn_in_hand",
    "sample_test",
]

SAMPLES_PER_FOLDER = 6

THUMB_WIDTH = 280
THUMB_HEIGHT = 240
LABEL_HEIGHT = 55

COLUMNS = 3


def get_images(folder):
    extensions = {".jpg", ".jpeg", ".png"}

    images = [
        p for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in extensions
        and not p.stem.lower().startswith("rotated_")
    ]

    return images


def make_thumbnail(path):

    try:
        image = Image.open(path).convert("RGB")

        image.thumbnail(
            (THUMB_WIDTH - 10, THUMB_HEIGHT - 10)
        )

        canvas = Image.new(
            "RGB",
            (THUMB_WIDTH, THUMB_HEIGHT),
            "white"
        )

        x = (THUMB_WIDTH - image.width) // 2
        y = (THUMB_HEIGHT - image.height) // 2

        canvas.paste(image, (x, y))

        return canvas

    except Exception as e:
        print(f"Could not read {path}: {e}")
        return None


def main():

    OUTPUT_DIR.mkdir(exist_ok=True)

    random.seed(42)

    selected = []

    for folder_name in FOLDERS:

        folder = DATASET_DIR / folder_name

        if not folder.exists():
            print(f"Missing folder: {folder_name}")
            continue

        images = get_images(folder)

        if not images:
            print(f"No images: {folder_name}")
            continue

        count = min(SAMPLES_PER_FOLDER, len(images))

        samples = random.sample(images, count)

        for image in samples:
            selected.append((folder_name, image))

    rows = math.ceil(len(selected) / COLUMNS)

    width = COLUMNS * THUMB_WIDTH
    height = rows * (THUMB_HEIGHT + LABEL_HEIGHT)

    sheet = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(sheet)

    for index, (folder_name, image_path) in enumerate(selected):

        thumbnail = make_thumbnail(image_path)

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

    output = OUTPUT_DIR / "candidate_preview.jpg"

    sheet.save(output, quality=90)

    print()
    print(f"Candidate preview: {output}")
    print(f"Images shown: {len(selected)}")


if __name__ == "__main__":
    main()