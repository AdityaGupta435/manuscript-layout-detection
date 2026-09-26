# Manuscript Layout Detection

Computer vision pipeline for detecting structural regions in historical and handwritten manuscript images.

The system detects five layout classes:

1. `header`
2. `footer`
3. `main_text`
4. `side_text`
5. `filler`

For every detected region, the system produces:

- Class label
- Confidence score
- Bounding box
- Annotated image
- Machine-readable JSON

---

## 1. Project Structure

```text
manuscript-layout-detection/
│
├── data/
│   ├── raw/
│   └── annotations/
│       ├── classes.txt
│       ├── labels/
│       └── preview/
│
├── models/
│   └── best.pt
│
├── src/
│   ├── annotate.py
│   ├── prepare_yolo_dataset.py
│   ├── validate_dataset.py
│   └── validate_results.py
│
├── inference.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 2. Classes

The system detects five manuscript layout classes:

| Class ID | Class | Description |
|---:|---|---|
| 0 | `header` | Clearly distinct heading, title, or section heading |
| 1 | `footer` | Footer, page number, folio, or bottom annotation |
| 2 | `main_text` | Primary textual content |
| 3 | `side_text` | Marginal notes, annotations, or text outside the primary reading flow |
| 4 | `filler` | Decorative elements, English text, pencil text, illustrations, diagrams, or ornamental panels |

Classes are not forced onto every image. A manuscript page can contain zero instances of a class.

## 3. Dataset

A representative subset of 45 manuscript images was annotated for the prototype.

### Dataset Split

- Training images: 36
- Validation images: 9
- Total images: 45
- Total annotated boxes: 243

Annotations use the YOLO format:

```text
class_id center_x center_y width height
```

## 4. Annotation Rules

Annotations represent semantic regions rather than physical page artifacts.

### Header

Annotate clearly distinct headings or titles.

Do not label an ordinary first body-text line as a header.

### Footer

Annotate clearly distinct footer text, folio numbers, page numbers, or bottom annotations.

Do not label ordinary bottom body text as a footer.

### Main Text

Annotate the primary textual content.

Physically separated columns or blocks can be represented by separate bounding boxes.

### Side Text

Annotate text outside the primary reading flow, including marginal notes and clearly separated side annotations.

### Filler

Annotate decorative elements, English text, pencil text, illustrations, diagrams, or ornamental panels that are treated as filler according to the assignment definition.

Do not annotate stains, shadows, holes, blank damaged regions, borders, or other background artifacts.

## 5. Model

The project uses an Ultralytics YOLO object-detection model.

### Base Model

```text
YOLO11n
```

### Training Configuration

```text
Epochs : 30
Image size : 640
Batch size : 2
Device : CPU
Train/validation split : 80/20
Random seed : 42
```

The final trained model is stored at:

```text
models/best.pt
```

### Model Rationale

YOLO11n was selected as a lightweight object-detection model suitable for
bounding-box localization and multi-class classification. The model provides
a practical balance between detection capability and computational cost,
which was important because training and inference were performed on a
CPU-only environment with limited hardware resources.

The model was fine-tuned for the five manuscript-specific layout classes:
header, footer, main_text, side_text, and filler.

## 6. Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

## 7. Inference

The required inference command is:

```powershell
python inference.py --input ./data/test_images --output ./results
```

The input can be either:

- A single image
- A directory containing multiple images

Example:

```powershell
python inference.py --input ./data/raw --output ./results
```

An optional confidence threshold can also be specified:

```powershell
python inference.py --input ./data/test_images --output ./results --confidence 0.40
```

## 8. Output

The inference pipeline creates the following output structure:

```text
results/
├── annotated/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
│
└── json/
    ├── image1.json
    ├── image2.json
    └── ...
```

The `annotated/` directory contains images with detected bounding boxes.

The `json/` directory contains machine-readable detection results.

Original input images are not modified.

## 9. JSON Format

Each processed image generates a corresponding JSON file.

Example:

```json
{
  "image": "example.jpg",
  "image_width": 2000,
  "image_height": 3000,
  "detections": [
    {
      "class_id": 2,
      "class": "main_text",
      "confidence": 0.91,
      "bounding_box": {
        "x1": 120.0,
        "y1": 350.0,
        "x2": 1800.0,
        "y2": 2600.0
      }
    }
  ]
}
```

Bounding boxes use pixel coordinates:

```text
x1, y1 = top-left
x2, y2 = bottom-right
```

Coordinates are clamped to the image boundaries.

## 10. Dataset Validation

Validate the YOLO annotations using:

```powershell
python .\src\validate_dataset.py
```

The validation checks:

- Image/label matching
- YOLO annotation format
- Valid class IDs
- Normalized coordinates
- Positive bounding-box dimensions
- Page-boundary constraints

A successful validation confirms that the dataset annotations follow the expected YOLO format and boundary requirements.

## 11. Result Validation

Validate generated JSON outputs using:

```powershell
python .\src\validate_results.py
```

The validator checks:

- Required JSON fields
- Valid class names
- Confidence range
- Bounding-box boundaries
- Valid bounding-box dimensions

## 12. Testing

The inference pipeline was tested on a batch of 45 images.

### Test Results

```text
Images processed : 45
Annotated images : 45
JSON files       : 45
Total detections : 236
Validation errors: 0
```

A separate confidence-threshold test was also performed at:

```text
confidence = 0.40
```

Three test images with different aspect ratios were processed successfully.

Boundary validation passed for all tested outputs.

## 13. Robustness Considerations

The assignment requires the system to handle variations including faded ink, bleed-through, stains, blur, skew, uneven lighting, page damage, varying aspect ratios, multi-column layouts, and different writing styles.

The prototype was evaluated for:

- Different image aspect ratios
- Historical manuscript layouts
- Multiple text blocks
- Multi-column layouts
- Marginal text
- Different page dimensions
- Bounding-box boundary constraints
- Confidence-threshold variation

The inference pipeline supports different image dimensions and clamps predicted bounding boxes to image boundaries.

Because the prototype uses a relatively small manually annotated dataset of 45 images, exhaustive evaluation of every degradation condition listed in the assignment was not performed. These conditions are therefore treated as robustness considerations rather than claims of complete robustness.

A production-scale system would require additional annotated examples covering faded ink, bleed-through, stains, blur, skew, uneven lighting, page damage, and a wider range of writing styles and layouts.

## 14. Reproducibility

The project includes:

- Fixed five-class definition
- YOLO-format annotations
- Fixed random seed for dataset splitting
- Training configuration
- Final trained model
- Inference script
- Dataset validator
- Result validator
- Dependency specification
- Reproducible CLI

## 15. Limitations

The prototype was trained on a relatively small annotated dataset of 45 images.

Some classes have relatively few validation examples, so class-specific validation metrics for rare classes should be interpreted cautiously.

For production deployment, additional annotated manuscript samples covering more writing styles, layouts, languages, degradation patterns, and document conditions would improve generalization.

## 16. Submission

The project is maintained in a private GitHub repository.

The repository contains:

- Source code
- Annotation files
- Final trained model
- Inference pipeline
- Validation scripts
- Requirements file
- Project documentation

The repository access is provided to the evaluation team as required.
