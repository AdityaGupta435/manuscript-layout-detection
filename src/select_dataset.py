from pathlib import Path
import random
import shutil
import csv


SOURCE_DIR = Path("data/immi_raw/IMMI_dataset")
RAW_DIR = Path("data/raw")
MANIFEST = Path("data/raw_manifest.csv")

SELECTION = {
    "Jain_manuscripts": 15,
    "penn-in-hand": 8,
    "penn_in_hand": 5,
    "jain-mscripts": 5,
    "ASR_Images": 5,
    "Bhoomi_data": 3,
    "sample_test": 4,
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

RANDOM_SEED = 42


def get_images(folder):
    return [
        p
        for p in folder.rglob("*")
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTENSIONS
        and not p.stem.lower().startswith("rotated_")
    ]


def make_prefix(folder_name):
    prefixes = {
        "penn-in-hand": "penn_hyphen",
        "penn_in_hand": "penn_underscore",
        "jain-mscripts": "jain_mscripts",
        "Jain_manuscripts": "Jain_manuscripts",
        "ASR_Images": "ASR_Images",
        "Bhoomi_data": "Bhoomi_data",
        "sample_test": "sample_test",
    }

    return prefixes[folder_name]


def main():

    random.seed(RANDOM_SEED)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Remove previous candidate files
    for file in RAW_DIR.iterdir():
        if file.is_file():
            file.unlink()

    manifest_rows = []

    for folder_name, count in SELECTION.items():

        source_folder = SOURCE_DIR / folder_name

        if not source_folder.exists():
            print(f"WARNING: missing folder: {folder_name}")
            continue

        images = get_images(source_folder)

        if len(images) < count:
            print(
                f"WARNING: {folder_name} has only "
                f"{len(images)} usable images"
            )
            selected = images
        else:
            selected = random.sample(images, count)

        print(
            f"{folder_name}: selected "
            f"{len(selected)} / {len(images)}"
        )

        prefix = make_prefix(folder_name)

        for index, source_path in enumerate(selected, start=1):

            new_name = (
                f"{prefix}_{index:03d}"
                f"{source_path.suffix.lower()}"
            )

            destination = RAW_DIR / new_name

            shutil.copy2(source_path, destination)

            manifest_rows.append({
                "filename": new_name,
                "source_collection": folder_name,
                "source_path": str(source_path),
            })

    with open(
        MANIFEST,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename",
                "source_collection",
                "source_path",
            ],
        )

        writer.writeheader()
        writer.writerows(manifest_rows)

    print()
    print("=" * 50)
    print(f"Total selected: {len(manifest_rows)}")
    print(
        f"Actual files in raw: "
        f"{len(list(RAW_DIR.iterdir()))}"
    )
    print(f"Output directory: {RAW_DIR}")
    print(f"Manifest: {MANIFEST}")
    print("=" * 50)


if __name__ == "__main__":
    main()