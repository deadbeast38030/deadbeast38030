#!/usr/bin/env python3
"""
prep_photo.py — turn a normal photo into a clean, high-contrast, background-free
grayscale source image that make_ascii_svg.py can convert cleanly.

Usage:
    python scripts/prep_photo.py source-photo.jpg

Output:
    source-prepped.png  (grayscale, white background, contrast-boosted)

Steps:
1. Remove the background with rembg so only the subject remains.
2. Boost local contrast with OpenCV CLAHE (contrast-limited adaptive histogram
   equalization) — a flatly-lit face has little separation between skin tone
   values; CLAHE pulls out real highlights and shadows.
3. Composite the cutout onto pure white so the background maps to the blank
   end of the ASCII ramp (white -> space character).
"""
import sys
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

try:
    from rembg import remove
except ImportError:
    remove = None


def remove_background(image_bytes: bytes) -> Image.Image:
    if remove is None:
        raise RuntimeError(
            "rembg is not installed. Run: pip install -r scripts/requirements.txt"
        )
    result_bytes = remove(image_bytes)
    return Image.open(BytesIO(result_bytes)).convert("RGBA")


def composite_on_white(rgba: Image.Image) -> Image.Image:
    background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")


def boost_contrast(img_rgb: Image.Image) -> Image.Image:
    arr = np.array(img_rgb.convert("L"))
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(arr)
    return Image.fromarray(boosted)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)

    src_path = sys.argv[1]
    with open(src_path, "rb") as f:
        raw = f.read()

    print("Removing background...")
    cutout = remove_background(raw)

    print("Compositing onto white...")
    on_white = composite_on_white(cutout)

    print("Boosting local contrast (CLAHE)...")
    final_gray = boost_contrast(on_white)

    out_path = "source-prepped.png"
    final_gray.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
