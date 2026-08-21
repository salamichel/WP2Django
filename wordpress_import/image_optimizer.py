import os
import shutil
import logging
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def optimize_and_copy_image(src_path, dst_path, max_dim=1600, quality=85):
    """
    Copy an image while resizing it if dimensions exceed max_dim (max 1600px width/height).
    Preserves aspect ratio, corrects EXIF orientation, and optimizes file weight.
    """
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower()

    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".jfif"]:
        shutil.copy2(src_path, dst_path)
        return False

    try:
        with Image.open(src_path) as img:
            # Transpose according to EXIF orientation tag
            img = ImageOps.exif_transpose(img)
            w, h = img.size

            needs_resize = w > max_dim or h > max_dim

            if needs_resize:
                if w >= h:
                    new_w = max_dim
                    new_h = max(1, int(h * (max_dim / w)))
                else:
                    new_h = max_dim
                    new_w = max(1, int(w * (max_dim / h)))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Format-specific save with compression
            if ext in [".jpg", ".jpeg", ".jfif"]:
                if img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")
                img.save(dst_path, "JPEG", quality=quality, optimize=True)
            elif ext == ".png":
                img.save(dst_path, "PNG", optimize=True)
            elif ext == ".webp":
                img.save(dst_path, "WEBP", quality=quality, method=6)
            else:
                shutil.copy2(src_path, dst_path)

            return needs_resize
    except Exception as e:
        logger.warning("Error optimizing %s: %s (fallback to raw copy)", src_path, e)
        shutil.copy2(src_path, dst_path)
        return False


def resize_existing_image_in_place(file_path, max_dim=1600, quality=85):
    """
    Resize an existing image file in-place if its dimensions exceed max_dim.
    Returns True if file was modified, False otherwise.
    """
    if not os.path.isfile(file_path):
        return False

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".jfif"]:
        return False

    try:
        with Image.open(file_path) as img:
            img = ImageOps.exif_transpose(img)
            w, h = img.size

            if w <= max_dim and h <= max_dim:
                return False

            if w >= h:
                new_w = max_dim
                new_h = max(1, int(h * (max_dim / w)))
            else:
                new_h = max_dim
                new_w = max(1, int(w * (max_dim / h)))

            resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            if ext in [".jpg", ".jpeg", ".jfif"]:
                if resized_img.mode in ("RGBA", "P", "LA"):
                    resized_img = resized_img.convert("RGB")
                resized_img.save(file_path, "JPEG", quality=quality, optimize=True)
            elif ext == ".png":
                resized_img.save(file_path, "PNG", optimize=True)
            elif ext == ".webp":
                resized_img.save(file_path, "WEBP", quality=quality, method=6)

            return True
    except Exception as e:
        logger.warning("Could not resize %s in-place: %s", file_path, e)
        return False
