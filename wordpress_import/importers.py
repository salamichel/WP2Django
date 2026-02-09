"""
WordPress data importers.

Each importer handles a specific WordPress entity type and maps it
to the corresponding Django model.
"""

import logging
import re
from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from blog.models import (
    Post, Page, Category, Tag, Comment, Media, Menu, MenuItem, Redirect, PluginData,
)

logger = logging.getLogger("wordpress_import")


def _parse_datetime(value):
    """Parse a WordPress datetime string."""
    if not value or value == "0000-00-00 00:00:00":
        return None
    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        return timezone.make_aware(dt)
    except (ValueError, TypeError):
        return None


def _safe_slug(text, max_length=500):
    """Generate a unique-safe slug from text."""
    slug = slugify(text) or "untitled"
    return slug[:max_length]


def _clean_wp_slug(slug):
    """Clean a WordPress slug to be Django-compatible.

    WordPress allows URL-encoded unicode in slugs (e.g. %e2%80%99 for
    curly apostrophe). Django's SlugField only accepts [-a-zA-Z0-9_].
    """
    if not slug:
        return slug
    # URL-decode first (e.g. %e2%80%99 -> ')
    from urllib.parse import unquote
    slug = unquote(slug)
    # Re-slugify to strip non-ASCII and invalid chars
    cleaned = slugify(slug)
    return cleaned or slugify(slug.encode("ascii", "ignore").decode()) or "untitled"


def _map_post_status(wp_status):
    """Map WordPress post status to Django status."""
    mapping = {
        "publish": "published",
        "draft": "draft",
        "pending": "pending",
        "private": "private",
        "trash": "trash",
        "auto-draft": "draft",
        "inherit": "published",
        "future": "draft",
    }
    return mapping.get(wp_status, "draft")


def _map_comment_status(wp_status):
    """Map WordPress comment status to Django status."""
    mapping = {
        "1": "approved",
        "0": "pending",
        "spam": "spam",
        "trash": "trash",
    }
    return mapping.get(str(wp_status), "pending")


class UserImporter:
    """Import WordPress users into Django User model."""

    def __init__(self, parser):
        self.parser = parser
        self.user_map = {}  # wp_user_id -> Django User

    def run(self):
        users_table = self.parser.get_table("users")
        usermeta_table = self.parser.get_table("usermeta")

        # Build a lookup of user meta
        meta_map = {}
        for row in usermeta_table["rows"]:
            uid = int(row.get("user_id", 0))
            key = row.get("meta_key", "")
            val = row.get("meta_value", "")
            if uid not in meta_map:
                meta_map[uid] = {}
            meta_map[uid][key] = val

        count = 0
        for row in users_table["rows"]:
            wp_id = int(row.get("ID", 0))
            login = row.get("user_login", "")
            email = row.get("user_email", "")
            display_name = row.get("display_name", login)

            if not login:
                continue

            user, created = User.objects.get_or_create(
                username=login,
                defaults={
                    "email": email or "",
                    "first_name": meta_map.get(wp_id, {}).get("first_name", ""),
                    "last_name": meta_map.get(wp_id, {}).get("last_name", ""),
                    "is_active": True,
                },
            )
            if created:
                user.set_unusable_password()
                user.save()

            self.user_map[wp_id] = user
            count += 1

        logger.info("Imported %d users", count)
        return self.user_map


class TaxonomyImporter:
    """Import WordPress taxonomies (categories, tags) into Django."""

    def __init__(self, parser):
        self.parser = parser
        self.category_map = {}  # wp_term_id -> Category
        self.tag_map = {}  # wp_term_id -> Tag

    def run(self):
        terms = self.parser.get_table("terms")
        taxonomy = self.parser.get_table("term_taxonomy")

        # Build term data: term_id -> {name, slug}
        term_data = {}
        for row in terms["rows"]:
            tid = int(row.get("term_id", 0))
            term_data[tid] = {
                "name": row.get("name", ""),
                "slug": _clean_wp_slug(row.get("slug", "")),
            }

        # Build taxonomy info: term_taxonomy_id -> {term_id, taxonomy, description, parent}
        tax_entries = []
        for row in taxonomy["rows"]:
            tax_entries.append({
                "term_taxonomy_id": int(row.get("term_taxonomy_id", 0)),
                "term_id": int(row.get("term_id", 0)),
                "taxonomy": row.get("taxonomy", ""),
                "description": row.get("description", ""),
                "parent": int(row.get("parent", 0)),
            })

        # First pass: create all categories and tags (without parents)
        for entry in tax_entries:
            tid = entry["term_id"]
            data = term_data.get(tid, {})
            name = data.get("name", "")
            slug = data.get("slug", "") or _safe_slug(name)

            if not name:
                continue

            if entry["taxonomy"] == "category":
                cat, _ = Category.objects.get_or_create(
                    wp_term_id=tid,
                    defaults={
                        "name": name,
                        "slug": slug,
                        "description": entry.get("description", ""),
                    },
                )
                self.category_map[tid] = cat

            elif entry["taxonomy"] == "post_tag":
                tag, _ = Tag.objects.get_or_create(
                    wp_term_id=tid,
                    defaults={
                        "name": name,
                        "slug": slug,
                        "description": entry.get("description", ""),
                    },
                )
                self.tag_map[tid] = tag

        # Second pass: set parent categories
        for entry in tax_entries:
            if entry["taxonomy"] == "category" and entry["parent"]:
                tid = entry["term_id"]
                parent_tid = entry["parent"]
                if tid in self.category_map and parent_tid in self.category_map:
                    cat = self.category_map[tid]
                    cat.parent = self.category_map[parent_tid]
                    cat.save(update_fields=["parent"])

        logger.info("Imported %d categories, %d tags", len(self.category_map), len(self.tag_map))
        return self.category_map, self.tag_map


class PostImporter:
    """Import WordPress posts and pages into Django."""

    def __init__(self, parser, user_map, category_map, tag_map):
        self.parser = parser
        self.user_map = user_map
        self.category_map = category_map
        self.tag_map = tag_map
        self.post_map = {}  # wp_post_id -> Post
        self.page_map = {}  # wp_post_id -> Page
        self.attachment_map = {}  # wp_post_id -> Media

    def run(self):
        posts_table = self.parser.get_table("posts")
        postmeta_table = self.parser.get_table("postmeta")
        relationships_table = self.parser.get_table("term_relationships")
        taxonomy_table = self.parser.get_table("term_taxonomy")

        # Build postmeta lookup: post_id -> {meta_key: meta_value}
        postmeta = {}
        for row in postmeta_table["rows"]:
            pid = int(row.get("post_id", 0))
            key = row.get("meta_key", "")
            val = row.get("meta_value", "")
            if pid not in postmeta:
                postmeta[pid] = {}
            postmeta[pid][key] = val

        # Build term_taxonomy_id -> (term_id, taxonomy)
        tax_lookup = {}
        for row in taxonomy_table["rows"]:
            ttid = int(row.get("term_taxonomy_id", 0))
            tax_lookup[ttid] = {
                "term_id": int(row.get("term_id", 0)),
                "taxonomy": row.get("taxonomy", ""),
            }

        # Build relationships: object_id -> [term_taxonomy_ids]
        rel_map = {}
        for row in relationships_table["rows"]:
            oid = int(row.get("object_id", 0))
            ttid = int(row.get("term_taxonomy_id", 0))
            if oid not in rel_map:
                rel_map[oid] = []
            rel_map[oid].append(ttid)

        # Sort posts so attachments are processed first (needed for featured images)
        rows = sorted(posts_table["rows"], key=lambda r: (
            0 if r.get("post_type") == "attachment" else 1
        ))

        used_slugs_post = set()
        used_slugs_page = set()

        for row in rows:
            wp_id = int(row.get("ID", 0))
            post_type = row.get("post_type", "post")
            status = row.get("post_status", "draft")
            title = row.get("post_title", "") or ""
            slug = _clean_wp_slug(row.get("post_name", "")) or _safe_slug(title)
            content = row.get("post_content", "") or ""
            excerpt = row.get("post_excerpt", "") or ""
            author_id = int(row.get("post_author", 0))
            parent_id = int(row.get("post_parent", 0))
            date = _parse_datetime(row.get("post_date"))
            modified = _parse_datetime(row.get("post_modified"))

            meta = postmeta.get(wp_id, {})
            author = self.user_map.get(author_id)

            if post_type == "attachment":
                self._import_attachment(wp_id, row, meta)
            elif post_type == "post":
                slug = self._unique_slug(slug, used_slugs_post, Post, "slug")
                used_slugs_post.add(slug)
                self._import_post(wp_id, title, slug, content, excerpt, status, author, date, meta, rel_map, tax_lookup)
            elif post_type == "page":
                slug = self._unique_slug(slug, used_slugs_page, Page, "slug")
                used_slugs_page.add(slug)
                self._import_page(wp_id, title, slug, content, status, author, date, parent_id, row, meta)
            elif post_type == "nav_menu_item":
                pass  # Handled by MenuImporter
            # Revision, auto-draft, custom post types: skip

        # Set featured images
        for wp_id, post in self.post_map.items():
            meta = postmeta.get(wp_id, {})
            thumb_id = meta.get("_thumbnail_id")
            if thumb_id:
                try:
                    media = self.attachment_map.get(int(thumb_id))
                    if media:
                        post.featured_image = media
                        post.save(update_fields=["featured_image"])
                except (ValueError, TypeError):
                    pass

        logger.info(
            "Imported %d posts, %d pages, %d attachments",
            len(self.post_map), len(self.page_map), len(self.attachment_map),
        )
        return self.post_map, self.page_map, self.attachment_map

    def _unique_slug(self, slug, used_set, model_class, field):
        """Ensure slug is unique."""
        if not slug:
            slug = "untitled"
        original = slug
        counter = 1
        while slug in used_set or model_class.objects.filter(**{field: slug}).exists():
            slug = f"{original}-{counter}"
            counter += 1
        return slug

    def _import_attachment(self, wp_id, row, meta):
        guid = str(row.get("guid", "") or "")
        title = str(row.get("post_title", "") or "")
        mime = str(row.get("post_mime_type", "") or "")

        # Extract the relative file path from meta or guid
        file_path = str(meta.get("_wp_attached_file", "") or "")
        if not file_path and guid:
            # Try to extract path from URL
            match = re.search(r"/wp-content/uploads/(.+)$", guid)
            if match:
                file_path = match.group(1)

        media, _ = Media.objects.get_or_create(
            wp_post_id=wp_id,
            defaults={
                "title": title[:512],
                "file": f"uploads/{file_path}" if file_path else "",
                "alt_text": str(meta.get("_wp_attachment_image_alt", "") or "")[:512],
                "mime_type": mime[:255],
                "original_url": guid[:1024],
            },
        )
        self.attachment_map[wp_id] = media

    def _import_post(self, wp_id, title, slug, content, excerpt, status, author, date, meta, rel_map, tax_lookup):
        # SEO from Yoast or other plugins
        seo_title = meta.get("_yoast_wpseo_title", "") or meta.get("rank_math_title", "")
        seo_desc = meta.get("_yoast_wpseo_metadesc", "") or meta.get("rank_math_description", "")

        post, _ = Post.objects.get_or_create(
            wp_post_id=wp_id,
            defaults={
                "title": title,
                "slug": slug,
                "content": content,
                "excerpt": excerpt,
                "status": _map_post_status(status),
                "author": author,
                "published_at": date,
                "seo_title": seo_title or "",
                "seo_description": seo_desc or "",
            },
        )

        # Set categories and tags
        ttids = rel_map.get(wp_id, [])
        for ttid in ttids:
            tax_info = tax_lookup.get(ttid, {})
            tid = tax_info.get("term_id")
            taxonomy = tax_info.get("taxonomy")
            if taxonomy == "category" and tid in self.category_map:
                post.categories.add(self.category_map[tid])
            elif taxonomy == "post_tag" and tid in self.tag_map:
                post.tags.add(self.tag_map[tid])

        self.post_map[wp_id] = post

    def _import_page(self, wp_id, title, slug, content, status, author, date, parent_id, row, meta):
        seo_title = meta.get("_yoast_wpseo_title", "") or meta.get("rank_math_title", "")
        seo_desc = meta.get("_yoast_wpseo_metadesc", "") or meta.get("rank_math_description", "")
        menu_order = int(row.get("menu_order", 0) or 0)

        page, _ = Page.objects.get_or_create(
            wp_post_id=wp_id,
            defaults={
                "title": title,
                "slug": slug,
                "content": content,
                "status": _map_post_status(status),
                "author": author,
                "published_at": date,
                "menu_order": menu_order,
                "seo_title": seo_title or "",
                "seo_description": seo_desc or "",
            },
        )
        self.page_map[wp_id] = page

    def set_page_parents(self):
        """Second pass to set page parent relationships."""
        posts_table = self.parser.get_table("posts")
        for row in posts_table["rows"]:
            if row.get("post_type") != "page":
                continue
            wp_id = int(row.get("ID", 0))
            parent_id = int(row.get("post_parent", 0))
            if parent_id and wp_id in self.page_map and parent_id in self.page_map:
                page = self.page_map[wp_id]
                page.parent = self.page_map[parent_id]
                page.save(update_fields=["parent"])


class CommentImporter:
    """Import WordPress comments."""

    def __init__(self, parser, post_map):
        self.parser = parser
        self.post_map = post_map
        self.comment_map = {}

    def run(self):
        comments_table = self.parser.get_table("comments")

        # First pass: create all comments without parents
        for row in comments_table["rows"]:
            wp_id = int(row.get("comment_ID", 0))
            post_id = int(row.get("comment_post_ID", 0))
            post = self.post_map.get(post_id)
            if not post:
                continue

            status = _map_comment_status(row.get("comment_approved", "0"))
            date = _parse_datetime(row.get("comment_date"))

            comment, _ = Comment.objects.get_or_create(
                wp_comment_id=wp_id,
                defaults={
                    "post": post,
                    "author_name": row.get("comment_author", ""),
                    "author_email": row.get("comment_author_email", ""),
                    "author_url": row.get("comment_author_url", ""),
                    "content": row.get("comment_content", ""),
                    "status": status,
                },
            )
            if date and comment.pk:
                Comment.objects.filter(pk=comment.pk).update(created_at=date)

            self.comment_map[wp_id] = comment

        # Second pass: set parent comments
        for row in comments_table["rows"]:
            wp_id = int(row.get("comment_ID", 0))
            parent_id = int(row.get("comment_parent", 0))
            if parent_id and wp_id in self.comment_map and parent_id in self.comment_map:
                comment = self.comment_map[wp_id]
                comment.parent = self.comment_map[parent_id]
                comment.save(update_fields=["parent"])

        logger.info("Imported %d comments", len(self.comment_map))
        return self.comment_map


class MenuImporter:
    """Import WordPress navigation menus."""

    def __init__(self, parser):
        self.parser = parser

    def run(self):
        terms = self.parser.get_table("terms")
        taxonomy = self.parser.get_table("term_taxonomy")
        posts_table = self.parser.get_table("posts")
        postmeta_table = self.parser.get_table("postmeta")
        relationships_table = self.parser.get_table("term_relationships")

        # Find nav_menu taxonomy entries
        nav_menu_term_ids = set()
        for row in taxonomy["rows"]:
            if row.get("taxonomy") == "nav_menu":
                nav_menu_term_ids.add(int(row.get("term_id", 0)))

        # Build term lookup
        term_lookup = {}
        for row in terms["rows"]:
            tid = int(row.get("term_id", 0))
            term_lookup[tid] = {
                "name": row.get("name", ""),
                "slug": row.get("slug", ""),
            }

        # Create Menu objects
        menu_map = {}  # term_id -> Menu
        for tid in nav_menu_term_ids:
            data = term_lookup.get(tid, {})
            if data.get("name"):
                menu, _ = Menu.objects.get_or_create(
                    wp_term_id=tid,
                    defaults={
                        "name": data["name"],
                        "slug": data.get("slug", "") or _safe_slug(data["name"]),
                    },
                )
                menu_map[tid] = menu

        # Build postmeta lookup for nav menu items
        postmeta = {}
        for row in postmeta_table["rows"]:
            pid = int(row.get("post_id", 0))
            if pid not in postmeta:
                postmeta[pid] = {}
            postmeta[pid][row.get("meta_key", "")] = row.get("meta_value", "")

        # Build term_taxonomy_id -> term_id
        ttid_to_tid = {}
        for row in taxonomy["rows"]:
            ttid_to_tid[int(row.get("term_taxonomy_id", 0))] = int(row.get("term_id", 0))

        # Build object_id -> term_ids relationships
        obj_to_tids = {}
        for row in relationships_table["rows"]:
            oid = int(row.get("object_id", 0))
            ttid = int(row.get("term_taxonomy_id", 0))
            tid = ttid_to_tid.get(ttid)
            if tid:
                if oid not in obj_to_tids:
                    obj_to_tids[oid] = []
                obj_to_tids[oid].append(tid)

        # Process nav_menu_item posts
        menu_items_data = []
        for row in posts_table["rows"]:
            if row.get("post_type") != "nav_menu_item":
                continue
            wp_id = int(row.get("ID", 0))
            meta = postmeta.get(wp_id, {})

            # Which menu does this item belong to?
            item_tids = obj_to_tids.get(wp_id, [])
            menu = None
            for tid in item_tids:
                if tid in menu_map:
                    menu = menu_map[tid]
                    break

            if not menu:
                continue

            menu_items_data.append({
                "wp_id": wp_id,
                "menu": menu,
                "title": row.get("post_title", "") or meta.get("_menu_item_title", ""),
                "url": meta.get("_menu_item_url", ""),
                "target": meta.get("_menu_item_target", ""),
                "css_classes": meta.get("_menu_item_classes", ""),
                "position": int(row.get("menu_order", 0) or 0),
                "parent_wp_id": int(meta.get("_menu_item_menu_item_parent", 0) or 0),
                "object_type": meta.get("_menu_item_type", ""),
                "object_id": meta.get("_menu_item_object_id", ""),
                "object": meta.get("_menu_item_object", ""),
            })

        # Create menu items
        item_map = {}
        for data in menu_items_data:
            content_type = ""
            object_id = None
            if data["object_type"] == "post_type":
                content_type = data["object"]  # "post" or "page"
                try:
                    object_id = int(data["object_id"])
                except (ValueError, TypeError):
                    pass
            elif data["object_type"] == "taxonomy":
                content_type = data["object"]  # "category"
                try:
                    object_id = int(data["object_id"])
                except (ValueError, TypeError):
                    pass

            item, _ = MenuItem.objects.get_or_create(
                wp_post_id=data["wp_id"],
                defaults={
                    "menu": data["menu"],
                    "title": data["title"],
                    "url": data["url"],
                    "target": data["target"],
                    "css_classes": data["css_classes"],
                    "position": data["position"],
                    "content_type": content_type,
                    "object_id": object_id,
                },
            )
            item_map[data["wp_id"]] = item

        # Set parent menu items
        for data in menu_items_data:
            if data["parent_wp_id"] and data["wp_id"] in item_map and data["parent_wp_id"] in item_map:
                item = item_map[data["wp_id"]]
                item.parent = item_map[data["parent_wp_id"]]
                item.save(update_fields=["parent"])

        logger.info("Imported %d menus with %d items", len(menu_map), len(item_map))


class PluginDataImporter:
    """Import data from detected WordPress plugin tables."""

    def __init__(self, parser, post_map, page_map):
        self.parser = parser
        self.post_map = post_map
        self.page_map = page_map

    def run(self):
        plugin_tables = self.parser.get_plugin_tables()
        total = 0

        for plugin_name, table_names in plugin_tables.items():
            for table_name in table_names:
                table_data = self.parser.tables.get(table_name, {})
                rows = table_data.get("rows", [])

                for row in rows:
                    # Try to link to a post or page
                    related_post = None
                    related_page = None
                    for key in ("post_id", "post_ID", "object_id"):
                        if key in row:
                            try:
                                pid = int(row[key])
                                if pid in self.post_map:
                                    related_post = self.post_map[pid]
                                elif pid in self.page_map:
                                    related_page = self.page_map[pid]
                            except (ValueError, TypeError):
                                pass
                            break

                    PluginData.objects.create(
                        plugin_name=plugin_name,
                        source_table=table_name,
                        data=self._serialize_row(row),
                        related_post=related_post,
                        related_page=related_page,
                    )
                    total += 1

        logger.info("Imported %d plugin data rows from %d plugins", total, len(plugin_tables))

    def _serialize_row(self, row):
        """Convert row to JSON-serializable dict."""
        result = {}
        for key, value in row.items():
            if value is None:
                result[key] = None
            elif isinstance(value, (int, float, bool)):
                result[key] = value
            else:
                result[key] = str(value)
        return result


class RedirectGenerator:
    """Generate redirects from old WordPress URLs to new Django URLs."""

    def __init__(self, parser, post_map, page_map, category_map, tag_map):
        self.parser = parser
        self.post_map = post_map
        self.page_map = page_map
        self.category_map = category_map
        self.tag_map = tag_map

    def run(self):
        options = self.parser.get_table("options")

        # Try to detect WordPress permalink structure
        permalink_structure = "/%postname%/"
        site_url = ""
        for row in options["rows"]:
            name = row.get("option_name", "")
            if name == "permalink_structure":
                permalink_structure = row.get("option_value", "/%postname%/")
            elif name == "siteurl":
                site_url = row.get("option_value", "")

        count = 0

        # Generate post redirects
        posts_table = self.parser.get_table("posts")
        for row in posts_table["rows"]:
            wp_id = int(row.get("ID", 0))
            post_type = row.get("post_type", "")
            slug = row.get("post_name", "")
            date = row.get("post_date", "")

            if not slug:
                continue

            try:
                if post_type == "post" and wp_id in self.post_map:
                    post = self.post_map[wp_id]
                    new_url = post.get_absolute_url()
                    old_path = self._build_wp_url(permalink_structure, slug, date)
                    if old_path and old_path != new_url:
                        Redirect.objects.get_or_create(
                            old_path=old_path,
                            defaults={"new_path": new_url},
                        )
                        count += 1

                    # Also redirect /?p=ID
                    Redirect.objects.get_or_create(
                        old_path=f"/?p={wp_id}",
                        defaults={"new_path": new_url},
                    )

                elif post_type == "page" and wp_id in self.page_map:
                    page = self.page_map[wp_id]
                    new_url = page.get_absolute_url()
                    old_path = f"/{slug}/"
                    if old_path != new_url:
                        Redirect.objects.get_or_create(
                            old_path=old_path,
                            defaults={"new_path": new_url},
                        )
                        count += 1
            except Exception as e:
                logger.warning("Skipping redirect for post %d: %s", wp_id, e)

        logger.info("Generated %d redirects", count)

    def _build_wp_url(self, structure, slug, date):
        """Build the old WordPress URL based on permalink structure."""
        if not structure:
            return None

        url = structure
        url = url.replace("%postname%", slug)

        if date and ("%year%" in url or "%monthnum%" in url or "%day%" in url):
            try:
                dt = datetime.strptime(str(date)[:10], "%Y-%m-%d")
                url = url.replace("%year%", str(dt.year))
                url = url.replace("%monthnum%", f"{dt.month:02d}")
                url = url.replace("%day%", f"{dt.day:02d}")
            except ValueError:
                pass

        # Clean up any remaining tags
        url = re.sub(r"%\w+%", "", url)
        return url
