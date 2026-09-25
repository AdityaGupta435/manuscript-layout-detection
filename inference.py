import argparse
import json
from pathlib import Path

from PIL import Image
from ultralytics import YOLO


CLASS_NAMES = {
    0: "header",
    1: "footer",
    2: "main_text",
    3: "side_text",
    4: "filler",
}

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "best.pt"
)

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def get_images(input_path):
    input_path = Path(input_path)

    if input_path.is_file():
        return [input_path]

    if input_path.is_dir():
        return sorted(
            p
            for p in input_path.iterdir()
            if p.is_file()
            and p.suffix.lower() in IMAGE_EXTENSIONS
        )

    return []


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def run_inference(input_path, output_path, confidence=0.25):
    input_path = Path(input_path)
    output_path = Path(output_path)

    annotated_dir = output_path / "annotated"
    json_dir = output_path / "json"

    annotated_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    images = get_images(input_path)

    if not images:
        print(f"No images found in: {input_path}")
        return

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    model = YOLO(str(MODEL_PATH))

    print("=" * 60)
    print("MANUSCRIPT LAYOUT DETECTION")
    print("=" * 60)
    print(f"Model  : {MODEL_PATH}")
    print(f"Images : {len(images)}")
    print(f"Output : {output_path}")
    print("=" * 60)

    for image_path in images:

        print(f"\nProcessing: {image_path.name}")

        with Image.open(image_path) as image:
            image_width, image_height = image.size

        result = model.predict(
            source=str(image_path),
            conf=confidence,
            verbose=False,
            device="cpu",
        )[0]

        detections = []

        if result.boxes is not None:

            for box in result.boxes:

                class_id = int(box.cls[0].item())
                score = float(box.conf[0].item())

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Keep coordinates inside image boundaries
                x1 = clamp(x1, 0, image_width)
                y1 = clamp(y1, 0, image_height)
                x2 = clamp(x2, 0, image_width)
                y2 = clamp(y2, 0, image_height)

                detections.append(
                    {
                        "class_id": class_id,
                        "class": CLASS_NAMES.get(
                            class_id,
                            "unknown"
                        ),
                        "confidence": round(score, 4),
                        "bounding_box": {
                            "x1": round(x1, 2),
                            "y1": round(y1, 2),
                            "x2": round(x2, 2),
                            "y2": round(y2, 2),
                        },
                    }
                )

        # Annotated image
        annotated_image = result.plot()

        annotated_path = (
            annotated_dir / image_path.name
        )

        Image.fromarray(annotated_image[:, :, ::-1]).save(
            annotated_path
        )

        # JSON
        json_data = {
            "image": image_path.name,
            "image_width": image_width,
            "image_height": image_height,
            "detections": detections,
        }

        json_path = (
            json_dir
            / f"{image_path.stem}.json"
        )

        with open(
            json_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                json_data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        print(
            f"Detections: {len(detections)}"
        )

    print("\n" + "=" * 60)
    print("INFERENCE COMPLETE")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Manuscript Layout Detection"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input image or image directory",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output directory",
    )

    parser.add_argument(
        "--confidence",
        type=float,
        default=0.25,
        help="Minimum confidence threshold",
    )

    args = parser.parse_args()

    run_inference(
        args.input,
        args.output,
        args.confidence,
    )


if __name__ == "__main__":
    main()