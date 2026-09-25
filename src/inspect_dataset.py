from pathlib import Path
from PIL import Image
from collections import Counter


DATASET_DIR = Path("data/immi_raw/IMMI_dataset")


def main():
    images = list(DATASET_DIR.rglob("*.jpg"))
    images += list(DATASET_DIR.rglob("*.jpeg"))
    images += list(DATASET_DIR.rglob("*.png"))

    print(f"Total images found: {len(images)}")

    dimensions = Counter()
    folders = Counter()

    for image_path in images:
        try:
            with Image.open(image_path) as img:
                dimensions[img.size] += 1

            relative_parts = image_path.relative_to(DATASET_DIR).parts

            if relative_parts:
                folders[relative_parts[0]] += 1

        except Exception as e:
            print(f"Could not read: {image_path}")
            print(f"Error: {e}")

    print("\nImages by folder:")
    for folder, count in folders.most_common():
        print(f"{folder}: {count}")

    print("\nMost common dimensions:")
    for dimension, count in dimensions.most_common(20):
        print(f"{dimension}: {count}")


if __name__ == "__main__":
    main()