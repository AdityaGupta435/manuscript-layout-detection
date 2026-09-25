from pathlib import Path
from PIL import Image, ImageDraw


SOURCE = Path("data/immi_raw/IMMI_dataset/sample_test")
OUTPUT = Path("results/sample_test_candidates.jpg")

FILES = [
    "gsn3_18.jpg",
    "gsn6_4.jpg",
    "gsn8_9.jpg",
]

THUMB_W = 400
THUMB_H = 300
LABEL_H = 50


def main():

    images = []

    for filename in FILES:
        path = SOURCE / filename

        if not path.exists():
            print(f"Missing: {filename}")
            continue

        image = Image.open(path).convert("RGB")
        image.thumbnail((THUMB_W - 20, THUMB_H - 20))

        images.append((filename, image))

    if not images:
        print("No candidate images found.")
        return

    sheet = Image.new(
        "RGB",
        (THUMB_W * len(images), THUMB_H + LABEL_H),
        "white"
    )

    draw = ImageDraw.Draw(sheet)

    for i, (filename, image) in enumerate(images):

        x = i * THUMB_W

        ix = x + (THUMB_W - image.width) // 2
        iy = (THUMB_H - image.height) // 2

        sheet.paste(image, (ix, iy))

        draw.text(
            (x + 10, THUMB_H + 10),
            filename,
            fill="black"
        )

    OUTPUT.parent.mkdir(exist_ok=True)
    sheet.save(OUTPUT, quality=90)

    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()