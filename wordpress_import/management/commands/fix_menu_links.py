"""
Fix MenuItem FK links and clean PHP serialized data after WordPress import.

Menu items imported from WordPress may have:
- content_type/object_id set but linked_post/linked_page/linked_category NULL
- css_classes containing raw PHP serialized arrays like a:1:{i:0;s:0:"";}

Usage:
    python manage.py fix_menu_links [--dry-run]
"""

import re

from django.core.management.base import BaseCommand

from blog.models import MenuItem, Post, Page, Category


def _php_unserialize_array(value):
    """Extract string values from a PHP serialized array."""
    if not value or not isinstance(value, str):
        return ""
    if not value.startswith("a:"):
        return value
    strings = re.findall(r's:\d+:"([^"]*)"', value)
    return " ".join(s for s in strings if s)


class Command(BaseCommand):
    help = "Resolve MenuItem FK links and clean PHP serialized fields"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be fixed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        self._fix_fk_links(dry_run)
        self._fix_php_serialized_fields(dry_run)

    def _fix_fk_links(self, dry_run):
        """Resolve FK links from content_type/object_id."""
        fixed = 0
        errors = 0

        items = MenuItem.objects.filter(
            content_type__in=["post", "page", "category"],
            object_id__isnull=False,
            linked_post__isnull=True,
            linked_page__isnull=True,
            linked_category__isnull=True,
        )

        self.stdout.write(f"Found {items.count()} menu items with missing FK links.")

        for item in items:
            target = None
            field = None

            if item.content_type == "post":
                target = Post.objects.filter(wp_post_id=item.object_id).first()
                field = "linked_post"
            elif item.content_type == "page":
                target = Page.objects.filter(wp_post_id=item.object_id).first()
                field = "linked_page"
            elif item.content_type == "category":
                target = Category.objects.filter(wp_term_id=item.object_id).first()
                field = "linked_category"

            if target:
                if dry_run:
                    self.stdout.write(
                        f"  [DRY RUN] {item.title} -> {field}={target}"
                    )
                else:
                    setattr(item, field, target)
                    item.save(update_fields=[field])
                fixed += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Not found: {item.title} ({item.content_type}:{item.object_id})"
                    )
                )
                errors += 1

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(f"{prefix}{fixed} FK links fixed, {errors} not resolved.")
        )

    def _fix_php_serialized_fields(self, dry_run):
        """Clean PHP serialized data from css_classes."""
        fixed = 0
        items = MenuItem.objects.filter(css_classes__startswith="a:")

        self.stdout.write(f"Found {items.count()} menu items with PHP serialized css_classes.")

        for item in items:
            cleaned = _php_unserialize_array(item.css_classes)
            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] {item.title}: "{item.css_classes}" -> "{cleaned}"'
                )
            else:
                item.css_classes = cleaned
                item.save(update_fields=["css_classes"])
            fixed += 1

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(f"{prefix}{fixed} css_classes fields cleaned.")
        )
