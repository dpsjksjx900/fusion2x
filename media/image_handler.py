import os
import shutil

def process_image(frame_dir, output_path, logger=None):
    """
    Handles export of the processed image (single-image mode).
    Moves or renames the processed image from frame_dir to output_path.
    """
    # Find the processed image (assuming there's only one)
    images = [f for f in os.listdir(frame_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not images:
        raise RuntimeError("No output image found in frame directory.")
    src = os.path.join(frame_dir, images[0])
    shutil.move(src, output_path)
    if logger:
        logger.info(f"[ImageHandler] Moved {src} -> {output_path}")
