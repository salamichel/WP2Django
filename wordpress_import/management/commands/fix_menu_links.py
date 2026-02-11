"""
Fix MenuItem FK links after WordPress import.

Menu items imported from WordPress have content_type/object_id set
but linked_post/linked_page/linked_category may be NULL.
This command resolves those references.

Usage:
    python manage.py fix_menu_links [--dry-run]
"""

from django.core.management.base import BaseCommand

from blog.models import MenuItem, Post, Page, Category


class Command(BaseCommand):
    help = "Resolve MenuItem FK links from WordPress content_type/object_id fields"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be fixed without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        fixed = 0
        errors = 0

        items = MenuItem.objects.filter(
            content_type__in=["post", "page", "category"],
            object_id__isnull=False,
            linked_post__isnull=True,
            linked_page__isnull=True,
            linked_category__isnull=True,
        )

        self.stdout.write(f"Found {items.count()} menu items to fix.")

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
            self.style.SUCCESS(f"\n{prefix}{fixed} menu items fixed, {errors} not resolved.")
        )
