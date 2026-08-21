import os
from django.core.management.base import BaseCommand
from django.conf import settings
from wordpress_import.image_optimizer import resize_existing_image_in_place


class Command(BaseCommand):
    help = "Scan media directory and resize any images exceeding maximum dimension (default: 1600px)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--media-dir",
            default=settings.MEDIA_ROOT,
            help="Directory to scan for media files (default: MEDIA_ROOT)",
        )
        parser.add_argument(
            "--max-dim",
            type=int,
            default=1600,
            help="Maximum width or height in pixels (default: 1600)",
        )
        parser.add_argument(
            "--quality",
            type=int,
            default=85,
            help="JPEG/WebP output quality (1-100, default: 85)",
        )

    def handle(self, *args, **options):
        media_dir = options["media_dir"]
        max_dim = options["max_dim"]
        quality = options["quality"]

        if not os.path.isdir(media_dir):
            self.stderr.write(self.style.ERROR(f"Directory not found: {media_dir}"))
            return

        self.stdout.write(f"Scanning '{media_dir}' for images larger than {max_dim}px...")

        total_scanned = 0
        total_resized = 0

        for root, dirs, files in os.walk(media_dir):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in [".jpg", ".jpeg", ".png", ".webp", ".jfif"]:
                    total_scanned += 1
                    file_path = os.path.join(root, filename)
                    resized = resize_existing_image_in_place(file_path, max_dim=max_dim, quality=quality)
                    if resized:
                        total_resized += 1
                        rel_path = os.path.relpath(file_path, media_dir)
                        self.stdout.write(f"  [Resized] {rel_path}")

        self.stdout.write(self.style.SUCCESS(
            f"Done! Scanned {total_scanned} images, resized {total_resized} images to max {max_dim}px."
        ))
