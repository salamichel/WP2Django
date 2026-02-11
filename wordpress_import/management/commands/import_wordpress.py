"""
Autonomous WordPress SQL dump importer.

Usage:
    python manage.py import_wordpress path/to/dump.sql [--dry-run] [--skip-plugins] [--media-dir path/to/wp-content/uploads]

This command:
1. Parses the SQL dump file
2. Auto-detects table prefix and all tables (core + plugins)
3. Reports what it found (tables, row counts, detected plugins)
4. Imports everything into Django models
5. Processes content (URL rewriting, shortcode conversion)
6. Generates redirects from old WordPress URLs
7. Optionally copies media files
"""

import os
import shutil
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from wordpress_import.sql_parser import SQLParser
from wordpress_import.importers import (
    UserImporter,
    TaxonomyImporter,
    PostImporter,
    CommentImporter,
    MenuImporter,
    PluginDataImporter,
    RedirectGenerator,
)
from wordpress_import.content_processor import process_all_content

logger = logging.getLogger("wordpress_import")


class Command(BaseCommand):
    help = "Import a WordPress SQL dump into Django"

    def add_arguments(self, parser):
        parser.add_argument("sql_file", help="Path to the WordPress SQL dump file")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Analyze the dump without importing data",
        )
        parser.add_argument(
            "--skip-plugins",
            action="store_true",
            help="Skip importing plugin data tables",
        )
        parser.add_argument(
            "--media-dir",
            help="Path to wp-content/uploads directory to copy media files from",
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all previously imported data before importing",
        )

    def handle(self, *args, **options):
        sql_file = options["sql_file"]
        dry_run = options["dry_run"]
        skip_plugins = options["skip_plugins"]
        media_dir = options.get("media_dir")

        if not os.path.isfile(sql_file):
            raise CommandError(f"SQL file not found: {sql_file}")

        self.stdout.write(self.style.MIGRATE_HEADING("=" * 60))
        self.stdout.write(self.style.MIGRATE_HEADING("WordPress to Django - Autonomous Importer"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 60))

        # Phase 1: Parse SQL
        self.stdout.write("\n[1/7] Parsing SQL dump...")
        parser = SQLParser(sql_file)
        tables = parser.parse()

        self._print_analysis(parser, tables)

        if dry_run:
            self.stdout.write(self.style.SUCCESS("\nDry run complete. No data imported."))
            return

        if options["flush"]:
            self._flush_data()



        # Phase 2: Import users
        self.stdout.write("\n[2/7] Importing users...")
        user_importer = UserImporter(parser)
        user_map = user_importer.run()
        self.stdout.write(self.style.SUCCESS(f"  -> {len(user_map)} users"))

        # Phase 3: Import taxonomies
        self.stdout.write("\n[3/7] Importing categories and tags...")
        tax_importer = TaxonomyImporter(parser)
        category_map, tag_map = tax_importer.run()
        self.stdout.write(self.style.SUCCESS(
            f"  -> {len(category_map)} categories, {len(tag_map)} tags"
        ))

        # Phase 4: Import posts, pages, attachments
        self.stdout.write("\n[4/7] Importing posts, pages, and media...")
        post_importer = PostImporter(parser, user_map, category_map, tag_map)
        post_map, page_map, attachment_map = post_importer.run()
        post_importer.set_page_parents()
        self.stdout.write(self.style.SUCCESS(
            f"  -> {len(post_map)} posts, {len(page_map)} pages, {len(attachment_map)} media"
        ))

        # Phase 5: Import comments
        self.stdout.write("\n[5/7] Importing comments...")
        comment_importer = CommentImporter(parser, post_map)
        comment_map = comment_importer.run()
        self.stdout.write(self.style.SUCCESS(f"  -> {len(comment_map)} comments"))

        # Phase 6: Import menus and plugin data
        self.stdout.write("\n[6/7] Importing menus and plugin data...")
        menu_importer = MenuImporter(parser, post_map, page_map, category_map)
        menu_importer.run()

        if not skip_plugins:
            plugin_importer = PluginDataImporter(parser, post_map, page_map)
            plugin_importer.run()

        # Phase 7: Process content and generate redirects
        self.stdout.write("\n[7/7] Processing content and generating redirects...")

        # Get site URL from WP options
        site_url = self._get_wp_option(parser, "siteurl")
        process_all_content(site_url=site_url)

        redirect_gen = RedirectGenerator(parser, post_map, page_map, category_map, tag_map)
        redirect_gen.run()

        # Copy media files if directory provided
        if media_dir:
            self._copy_media(media_dir)

        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("Import complete!"))
        self._print_summary(user_map, category_map, tag_map, post_map, page_map, attachment_map, comment_map)

    def _flush_data(self):
        """Delete all previously imported data."""
        from blog.models import (
            Post, Page, Media, Category, Tag, Comment,
            Menu, MenuItem, Redirect, PluginData,
        )
        from django.contrib.auth.models import User

        self.stdout.write(self.style.WARNING("\nFlushing all imported data..."))
        for model in [PluginData, Redirect, MenuItem, Menu, Comment, Post, Page, Media, Tag, Category]:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f"  Deleted {count} {model.__name__}")
        # Delete non-superuser users (imported from WP)
        wp_users = User.objects.filter(is_superuser=False).count()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(f"  Deleted {wp_users} imported users")

    def _print_analysis(self, parser, tables):
        """Print analysis of the SQL dump."""
        self.stdout.write(self.style.MIGRATE_HEADING("\n--- SQL Dump Analysis ---"))
        self.stdout.write(f"Table prefix: {parser.table_prefix}")
        self.stdout.write(f"Total tables found: {len(tables)}")

        # Core tables
        core = parser.get_core_tables()
        self.stdout.write(f"\nWordPress core tables ({len(core)}):")
        for suffix in core:
            full = parser.table_prefix + suffix
            rows = len(tables.get(full, {}).get("rows", []))
            self.stdout.write(f"  {full}: {rows} rows")

        # Plugin tables
        plugin_tables = parser.get_plugin_tables()
        if plugin_tables:
            self.stdout.write(f"\nDetected plugin tables ({len(plugin_tables)} plugins):")
            for plugin_name, table_names in plugin_tables.items():
                total_rows = sum(len(tables.get(t, {}).get("rows", [])) for t in table_names)
                self.stdout.write(f"  [{plugin_name}] {len(table_names)} tables, {total_rows} rows")
                for t in table_names:
                    rows = len(tables.get(t, {}).get("rows", []))
                    self.stdout.write(f"    - {t}: {rows} rows")
        else:
            self.stdout.write("\nNo plugin tables detected.")

    def _get_wp_option(self, parser, option_name):
        """Get a WordPress option value."""
        options = parser.get_table("options")
        for row in options["rows"]:
            if row.get("option_name") == option_name:
                return row.get("option_value", "")
        return ""

    def _copy_media(self, source_dir):
        """Copy WordPress uploads to Django media directory."""
        if not os.path.isdir(source_dir):
            self.stdout.write(self.style.WARNING(f"Media dir not found: {source_dir}"))
            return

        dest = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(dest, exist_ok=True)

        count = 0
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                src_path = os.path.join(root, filename)
                rel_path = os.path.relpath(src_path, source_dir)
                dst_path = os.path.join(dest, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"  -> Copied {count} media files"))

    def _print_summary(self, user_map, category_map, tag_map, post_map, page_map, attachment_map, comment_map):
        """Print final import summary."""
        self.stdout.write(self.style.MIGRATE_HEADING("\n--- Import Summary ---"))
        self.stdout.write(f"Users:       {len(user_map)}")
        self.stdout.write(f"Categories:  {len(category_map)}")
        self.stdout.write(f"Tags:        {len(tag_map)}")
        self.stdout.write(f"Posts:       {len(post_map)}")
        self.stdout.write(f"Pages:       {len(page_map)}")
        self.stdout.write(f"Media:       {len(attachment_map)}")
        self.stdout.write(f"Comments:    {len(comment_map)}")
        self.stdout.write("")
        self.stdout.write("Next steps:")
        self.stdout.write("  1. python manage.py createsuperuser")
        self.stdout.write("  2. Review imported content in /admin/")
        self.stdout.write("  3. If you have media files, use --media-dir flag")
        self.stdout.write("  4. Update SITE_URL in .env")
