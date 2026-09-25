from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


# ============================================================
# Configuration
# ============================================================

IMAGE_DIR = Path("data/raw")
LABEL_DIR = Path("data/annotations/labels")
PREVIEW_DIR = Path("data/annotations/preview")

CLASSES = [
    "header",
    "footer",
    "main_text",
    "side_text",
    "filler",
]

DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 800


# ============================================================
# Annotation Application
# ============================================================

class AnnotationApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Manuscript Layout Annotation Tool")

        LABEL_DIR.mkdir(parents=True, exist_ok=True)
        PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

        self.image_files = sorted(
            [
                p for p in IMAGE_DIR.iterdir()
                if p.suffix.lower() in [".jpg", ".jpeg", ".png"]
            ]
        )

        if not self.image_files:
            messagebox.showerror(
                "Error",
                f"No images found in {IMAGE_DIR}"
            )
            root.destroy()
            return

        self.index = 0

        self.original_image = None
        self.tk_image = None

        self.display_scale = 1.0
        self.display_width = 0
        self.display_height = 0

        self.annotations = []

        # Default class = main_text
        self.selected_class = 2

        self.start_x = None
        self.start_y = None
        self.current_rectangle = None

        self.build_ui()
        self.load_image()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=8, pady=5)

        self.info_label = tk.Label(
            top,
            text="",
            font=("Arial", 11, "bold")
        )
        self.info_label.pack(side=tk.LEFT)

        self.class_label = tk.Label(
            top,
            text="Class: main_text",
            font=("Arial", 11, "bold")
        )
        self.class_label.pack(side=tk.RIGHT)

        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            background="gray"
        )

        self.canvas.pack(
            fill=tk.BOTH,
            expand=True
        )

        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=8, pady=5)

        instructions = (
            "1 Header | 2 Footer | 3 Main Text | "
            "4 Side Text | 5 Filler | "
            "U Undo | D Delete | S Save | "
            "N Next | P Previous | Esc Cancel"
        )

        tk.Label(
            bottom,
            text=instructions,
            font=("Arial", 9)
        ).pack()

        # Mouse events
        self.canvas.bind(
            "<ButtonPress-1>",
            self.on_mouse_down
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.on_mouse_drag
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.on_mouse_up
        )

        # Keyboard events
        self.root.bind(
            "<Key-1>",
            lambda e: self.set_class(0)
        )

        self.root.bind(
            "<Key-2>",
            lambda e: self.set_class(1)
        )

        self.root.bind(
            "<Key-3>",
            lambda e: self.set_class(2)
        )

        self.root.bind(
            "<Key-4>",
            lambda e: self.set_class(3)
        )

        self.root.bind(
            "<Key-5>",
            lambda e: self.set_class(4)
        )

        self.root.bind(
            "<Key-u>",
            lambda e: self.undo()
        )

        self.root.bind(
            "<Key-U>",
            lambda e: self.undo()
        )

        self.root.bind(
            "<Key-d>",
            lambda e: self.delete_last()
        )

        self.root.bind(
            "<Key-D>",
            lambda e: self.delete_last()
        )

        self.root.bind(
            "<Key-s>",
            lambda e: self.save_annotations()
        )

        self.root.bind(
            "<Key-S>",
            lambda e: self.save_annotations()
        )

        self.root.bind(
            "<Key-n>",
            lambda e: self.next_image()
        )

        self.root.bind(
            "<Key-N>",
            lambda e: self.next_image()
        )

        self.root.bind(
            "<Key-p>",
            lambda e: self.previous_image()
        )

        self.root.bind(
            "<Key-P>",
            lambda e: self.previous_image()
        )

        self.root.bind(
            "<Escape>",
            lambda e: self.cancel_current()
        )

        self.root.bind(
            "<Left>",
            lambda e: self.previous_image()
        )

        self.root.bind(
            "<Right>",
            lambda e: self.next_image()
        )

    # ========================================================
    # Image Loading
    # ========================================================

    def load_image(self):

        image_path = self.image_files[self.index]

        self.original_image = Image.open(
            image_path
        ).convert("RGB")

        original_width, original_height = (
            self.original_image.size
        )

        scale_x = DISPLAY_WIDTH / original_width
        scale_y = DISPLAY_HEIGHT / original_height

        self.display_scale = min(
            scale_x,
            scale_y,
            1.0
        )

        self.display_width = max(
            1,
            int(original_width * self.display_scale)
        )

        self.display_height = max(
            1,
            int(original_height * self.display_scale)
        )

        display_image = self.original_image.resize(
            (
                self.display_width,
                self.display_height
            ),
            Image.Resampling.LANCZOS
        )

        self.tk_image = ImageTk.PhotoImage(
            display_image
        )

        self.canvas.delete("all")

        self.canvas.config(
            width=self.display_width,
            height=self.display_height,
            scrollregion=(
                0,
                0,
                self.display_width,
                self.display_height
            )
        )

        self.canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.tk_image
        )

        self.load_annotations()
        self.update_info()

    # ========================================================
    # Label Path
    # ========================================================

    def label_path(self):

        return LABEL_DIR / (
            self.image_files[self.index].stem + ".txt"
        )

    # ========================================================
    # Load Existing Annotations
    # ========================================================

    def load_annotations(self):

        self.annotations = []

        path = self.label_path()

        if not path.exists():
            self.redraw_annotations()
            return

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                for line in f:

                    parts = line.strip().split()

                    if len(parts) != 5:
                        continue

                    class_id = int(parts[0])

                    if class_id < 0 or class_id >= len(CLASSES):
                        continue

                    cx = float(parts[1])
                    cy = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])

                    self.annotations.append(
                        {
                            "class_id": class_id,
                            "cx": cx,
                            "cy": cy,
                            "width": width,
                            "height": height,
                        }
                    )

        except Exception as e:

            messagebox.showerror(
                "Annotation Error",
                f"Could not load:\n{path}\n\n{e}"
            )

        self.redraw_annotations()

    # ========================================================
    # Save Annotations
    # ========================================================

    def save_annotations(self):

        path = self.label_path()

        # Do not create empty label files.
        if not self.annotations:

            if path.exists():
                path.unlink()

            print(
                f"No annotations: "
                f"{self.image_files[self.index].name}"
            )

            return

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            for ann in self.annotations:

                f.write(
                    f"{ann['class_id']} "
                    f"{ann['cx']:.6f} "
                    f"{ann['cy']:.6f} "
                    f"{ann['width']:.6f} "
                    f"{ann['height']:.6f}\n"
                )

        print(
            f"Saved {len(self.annotations)} annotations -> {path}"
        )

    # ========================================================
    # Class Selection
    # ========================================================

    def set_class(self, class_id):

        self.selected_class = class_id

        self.class_label.config(
            text=f"Class: {CLASSES[class_id]}"
        )

        print(
            f"Selected class: {class_id} - "
            f"{CLASSES[class_id]}"
        )

    # ========================================================
    # Mouse - Start Drawing
    # ========================================================

    def on_mouse_down(self, event):

        self.start_x = max(
            0,
            min(event.x, self.display_width)
        )

        self.start_y = max(
            0,
            min(event.y, self.display_height)
        )

        self.current_rectangle = (
            self.canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                outline="red",
                width=2
            )
        )

    # ========================================================
    # Mouse - Draw
    # ========================================================

    def on_mouse_drag(self, event):

        if self.current_rectangle is None:
            return

        x = max(
            0,
            min(event.x, self.display_width)
        )

        y = max(
            0,
            min(event.y, self.display_height)
        )

        self.canvas.coords(
            self.current_rectangle,
            self.start_x,
            self.start_y,
            x,
            y
        )

    # ========================================================
    # Mouse - Finish Drawing
    # ========================================================

    def on_mouse_up(self, event):

        if self.current_rectangle is None:
            return

        end_x = max(
            0,
            min(event.x, self.display_width)
        )

        end_y = max(
            0,
            min(event.y, self.display_height)
        )

        x1 = min(
            self.start_x,
            end_x
        )

        y1 = min(
            self.start_y,
            end_y
        )

        x2 = max(
            self.start_x,
            end_x
        )

        y2 = max(
            self.start_y,
            end_y
        )

        width = x2 - x1
        height = y2 - y1

        # Ignore accidental tiny clicks.
        if width < 5 or height < 5:

            self.canvas.delete(
                self.current_rectangle
            )

            self.current_rectangle = None
            return

        # Convert to normalized YOLO coordinates.
        cx = (
            (x1 + x2) / 2
        ) / self.display_width

        cy = (
            (y1 + y2) / 2
        ) / self.display_height

        norm_width = (
            width / self.display_width
        )

        norm_height = (
            height / self.display_height
        )

        # Boundary safety.
        cx = max(
            0.0,
            min(1.0, cx)
        )

        cy = max(
            0.0,
            min(1.0, cy)
        )

        norm_width = max(
            0.0,
            min(1.0, norm_width)
        )

        norm_height = max(
            0.0,
            min(1.0, norm_height)
        )

        annotation = {
            "class_id": self.selected_class,
            "cx": cx,
            "cy": cy,
            "width": norm_width,
            "height": norm_height,
        }

        self.annotations.append(
            annotation
        )

        self.canvas.delete(
            self.current_rectangle
        )

        self.current_rectangle = None

        self.draw_annotation(
            annotation,
            len(self.annotations) - 1
        )

        self.update_info()

    # ========================================================
    # Draw Existing Annotation
    # ========================================================

    def draw_annotation(
        self,
        annotation,
        index
    ):

        cx = (
            annotation["cx"]
            * self.display_width
        )

        cy = (
            annotation["cy"]
            * self.display_height
        )

        width = (
            annotation["width"]
            * self.display_width
        )

        height = (
            annotation["height"]
            * self.display_height
        )

        x1 = cx - width / 2
        y1 = cy - height / 2

        x2 = cx + width / 2
        y2 = cy + height / 2

        class_id = annotation["class_id"]

        class_name = CLASSES[class_id]

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            outline="red",
            width=2,
            tags="annotation"
        )

        self.canvas.create_text(
            x1 + 5,
            y1 + 5,
            anchor=tk.NW,
            text=f"{index + 1}: {class_name}",
            fill="red",
            font=("Arial", 10, "bold"),
            tags="annotation"
        )

    # ========================================================
    # Redraw
    # ========================================================

    def redraw_annotations(self):

        self.canvas.delete(
            "annotation"
        )

        for i, annotation in enumerate(
            self.annotations
        ):

            self.draw_annotation(
                annotation,
                i
            )

    # ========================================================
    # Undo
    # ========================================================

    def undo(self):

        if not self.annotations:
            return

        self.annotations.pop()

        self.redraw_annotations()
        self.update_info()

    # ========================================================
    # Delete Last
    # ========================================================

    def delete_last(self):

        if not self.annotations:
            return

        self.annotations.pop()

        self.redraw_annotations()
        self.update_info()

    # ========================================================
    # Cancel Current Box
    # ========================================================

    def cancel_current(self):

        if self.current_rectangle is not None:

            self.canvas.delete(
                self.current_rectangle
            )

            self.current_rectangle = None

    # ========================================================
    # Next Image
    # ========================================================

    def next_image(self):

        self.save_annotations()

        if self.index < len(self.image_files) - 1:

            self.index += 1

            self.load_image()

    # ========================================================
    # Previous Image
    # ========================================================

    def previous_image(self):

        self.save_annotations()

        if self.index > 0:

            self.index -= 1

            self.load_image()

    # ========================================================
    # Information
    # ========================================================

    def update_info(self):

        filename = self.image_files[
            self.index
        ].name

        self.info_label.config(
            text=(
                f"{self.index + 1}/"
                f"{len(self.image_files)} "
                f"| {filename} "
                f"| Boxes: "
                f"{len(self.annotations)}"
            )
        )


# ============================================================
# Main
# ============================================================

def main():

    root = tk.Tk()

    root.geometry(
        "1250x900"
    )

    AnnotationApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()