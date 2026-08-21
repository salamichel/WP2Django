import os
import shutil
import logging
from PIL import Image, ImageOps, ImageFile

# Support truncated images and large photo resolutions from cameras/smartphones
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

logger = logging.getLogger(__name__)


def optimize_and_copy_image(src_path, dst_path, max_dim=1600, quality=85):
    """
    Copy an image while resizing it if dimensions exceed max_dim (max 1600px width/height).
    Preserves aspect ratio, corrects EXIF orientation, and optimizes file weight.
    Handles identical source and destination paths (in-place) safely and never crashes.
    """
    try:
        if not os.path.exists(src_path):
            return False

        src_abs = os.path.abspath(src_path)
        dst_abs = os.path.abspath(dst_path)
        is_same_file = (src_abs == dst_abs)

        os.makedirs(os.path.dirname(dst_abs), exist_ok=True)
        ext = os.path.splitext(src_path)[1].lower()

        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".jfif"]:
            if not is_same_file:
                shutil.copy2(src_path, dst_path)
            return False

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
            elif is_same_file:
                # Same file and no resize needed -> done
                return False

            # If writing to the same file, write to a temporary file first
            dst_target = (dst_path + ".tmp_opt") if is_same_file else dst_path

            # Format-specific save with compression
            if ext in [".jpg", ".jpeg", ".jfif"]:
                if img.mode in ("RGBA", "P", "LA"):
                    img = img.convert("RGB")
                img.save(dst_target, "JPEG", quality=quality, optimize=True)
            elif ext == ".png":
                img.save(dst_target, "PNG", optimize=True)
            elif ext == ".webp":
                img.save(dst_target, "WEBP", quality=quality, method=6)
            else:
                if not is_same_file:
                    shutil.copy2(src_path, dst_path)
                return False

            if is_same_file and os.path.exists(dst_target):
                os.replace(dst_target, dst_path)

            return needs_resize
    except Exception as e:
        logger.warning("Error optimizing %s -> %s: %s (fallback to raw copy)", src_path, dst_path, e)
        try:
            if not is_same_file and os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
        except Exception:
            pass
        return False


def resize_existing_image_in_place(file_path, max_dim=1600, quality=85):
    """
    Resize an existing image file in-place if its dimensions exceed max_dim.
    Returns True if file was modified, False otherwise.
    """
    return optimize_and_copy_image(file_path, file_path, max_dim=max_dim, quality=quality)
