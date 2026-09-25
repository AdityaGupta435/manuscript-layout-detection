import json
from pathlib import Path


RESULTS_DIR = Path("results/json")

REQUIRED_TOP_LEVEL = {
    "image",
    "image_width",
    "image_height",
    "detections",
}

REQUIRED_DETECTION = {
    "class_id",
    "class",
    "confidence",
    "bounding_box",
}

VALID_CLASSES = {
    "header",
    "footer",
    "main_text",
    "side_text",
    "filler",
}


def main():
    json_files = sorted(RESULTS_DIR.glob("*.json"))

    errors = 0
    total_detections = 0

    print("=" * 60)
    print("RESULT JSON VALIDATION")
    print("=" * 60)

    for json_file in json_files:

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            missing = REQUIRED_TOP_LEVEL - set(data.keys())

            if missing:
                print(
                    f"ERROR: {json_file.name} "
                    f"missing fields: {missing}"
                )
                errors += 1
                continue

            width = data["image_width"]
            height = data["image_height"]

            for detection in data["detections"]:

                missing_detection = (
                    REQUIRED_DETECTION
                    - set(detection.keys())
                )

                if missing_detection:
                    print(
                        f"ERROR: {json_file.name} "
                        f"missing detection fields: "
                        f"{missing_detection}"
                    )
                    errors += 1
                    continue

                if detection["class"] not in VALID_CLASSES:
                    print(
                        f"ERROR: {json_file.name} "
                        f"invalid class: "
                        f"{detection['class']}"
                    )
                    errors += 1

                confidence = detection["confidence"]

                if not 0 <= confidence <= 1:
                    print(
                        f"ERROR: {json_file.name} "
                        f"invalid confidence: "
                        f"{confidence}"
                    )
                    errors += 1

                box = detection["bounding_box"]

                x1 = box["x1"]
                y1 = box["y1"]
                x2 = box["x2"]
                y2 = box["y2"]

                if not (
                    0 <= x1 <= width
                    and 0 <= x2 <= width
                    and 0 <= y1 <= height
                    and 0 <= y2 <= height
                ):
                    print(
                        f"ERROR: {json_file.name} "
                        f"bounding box outside image"
                    )
                    errors += 1

                if x2 <= x1 or y2 <= y1:
                    print(
                        f"ERROR: {json_file.name} "
                        f"invalid bounding box"
                    )
                    errors += 1

                total_detections += 1

        except Exception as error:
            print(
                f"ERROR: {json_file.name} -> {error}"
            )
            errors += 1

    print("=" * 60)
    print(f"JSON files       : {len(json_files)}")
    print(f"Total detections : {total_detections}")
    print(f"Errors           : {errors}")
    print("=" * 60)

    if errors == 0:
        print("RESULT VALIDATION PASSED")
    else:
        print("RESULT VALIDATION FAILED")


if __name__ == "__main__":
    main()