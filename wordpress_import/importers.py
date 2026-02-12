"""
WordPress data importers.

Each importer handles a specific WordPress entity type and maps it
to the corresponding Django model.
"""

import logging
import re
from datetime import datetime, date

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


class AnimalDataExtractor:
    """Extract structured animal data from WordPress post content/excerpt.

    Parses French-language animal profile fields commonly found in
    animal protection association posts, e.g.:
        Age : 3 mois
        Race : croisé
        Sexe : mâle
        Né le : 29/10/2025
        Poids : 9,6 kg
        Identification électronique : 250269611651491
        Vaccin : oui
        Castré : non
        En accueil chez Jacqueline.
    """

    # Patterns for field extraction (case-insensitive, French labels)
    FIELD_PATTERNS = [
        (r"(?:nom|pr[eé]nom)\s*:\s*(.+)", "animal_name"),
        (r"(?:race|crois[eé])\s*:\s*(.+)", "breed"),
        (r"sexe\s*:\s*(.+)", "sex"),
        (r"(?:n[eé](?:\(e\))?\s+le|date\s+de\s+naissance)\s*:\s*(.+)", "birth_date"),
        (r"(?:poids)\s*:\s*(.+)", "weight_kg"),
        (r"(?:identification\s+[eé]lectronique|puce|identifi[eé])\s*:\s*(.+)", "identification"),
        (r"(?:vaccin(?:[eé])?|vaccination)\s*:\s*(.+)", "is_vaccinated"),
        (r"(?:castr[eé]|st[eé]rilis[eé]|castration|st[eé]rilisation)\s*:\s*(.+)", "is_sterilized"),
        (r"(?:en\s+)?(?:famille\s+d'?accueil|accueil)\s+(?:chez\s+)?(.+)", "foster_family"),
        (r"[âa]ge\s*:\s*(.+)", "age_text"),
        (r"esp[eè]ce\s*:\s*(.+)", "species"),
    ]

    # Species detection keywords
    SPECIES_KEYWORDS = {
        "chien": ["chien", "chienne", "chiot", "chiots", "canin"],
        "chat": ["chat", "chatte", "chaton", "chatons", "félin", "felin"],
        "rongeur": ["rongeur", "lapin", "hamster", "cochon d'inde", "cobaye", "furet", "rat", "souris"],
    }

    @classmethod
    def extract(cls, content, excerpt="", meta=None, categories=None):
        """Extract animal profile data from content, excerpt, and metadata.

        Returns a dict of animal fields, or empty dict if no animal data found.
        Also returns cleaned content with extracted fields removed.
        """
        result = {}
        text = cls._strip_html(content)

        # Try postmeta first (ACF or custom fields plugins)
        if meta:
            result.update(cls._extract_from_meta(meta))

        # Then parse from text content
        text_data, _lines = cls._extract_from_text(text)
        for key, value in text_data.items():
            if key not in result or not result[key]:
                result[key] = value

        if not result:
            return {}, content

        # Detect species from categories or content if not explicitly set
        if "species" not in result or not result["species"]:
            result["species"] = cls._detect_species(text, categories)

        # Normalize extracted values
        normalized = cls._normalize(result)

        if not normalized:
            return {}, content

        # Clean the content: remove matching HTML blocks using field patterns
        cleaned_content = cls._clean_content_html(content)

        return normalized, cleaned_content

    @classmethod
    def _strip_html(cls, html):
        """Strip HTML tags for text parsing."""
        text = re.sub(r"<br\s*/?>", "\n", html or "")
        text = re.sub(r"</p>\s*<p[^>]*>", "\n", text)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&#8217;", "'", text)
        return text

    @classmethod
    def _extract_from_meta(cls, meta):
        """Try to extract animal data from WordPress postmeta (ACF etc.)."""
        result = {}
        meta_mappings = {
            "animal_name": ["animal_name", "nom_animal", "pet_name", "name"],
            "breed": ["race", "breed", "animal_breed"],
            "sex": ["sexe", "sex", "animal_sex", "gender"],
            "birth_date": ["date_naissance", "birth_date", "date_of_birth", "dob"],
            "weight_kg": ["poids", "weight", "animal_weight"],
            "identification": ["identification", "puce", "microchip", "chip_number"],
            "species": ["espece", "species", "animal_type", "type_animal"],
            "foster_family": ["famille_accueil", "foster_family", "foster"],
        }
        for field, meta_keys in meta_mappings.items():
            for mk in meta_keys:
                val = meta.get(mk, "")
                if val and not val.startswith("_"):
                    result[field] = str(val).strip()
                    break
        return result

    @classmethod
    def _extract_from_text(cls, text):
        """Extract field values from free text using regex patterns."""
        result = {}
        lines_to_remove = []

        for line in text.split("\n"):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            for pattern, field in cls.FIELD_PATTERNS:
                match = re.search(pattern, line_stripped, re.IGNORECASE)
                if match:
                    value = match.group(1).strip().rstrip(".")
                    if field not in result or not result[field]:
                        result[field] = value
                    lines_to_remove.append(line_stripped)
                    break

        return result, lines_to_remove

    @classmethod
    def _detect_species(cls, text, categories=None):
        """Detect species from categories or content keywords."""
        # Check categories first
        if categories:
            cat_names = [c.lower() if isinstance(c, str) else c.name.lower() for c in categories]
            for species, keywords in cls.SPECIES_KEYWORDS.items():
                for kw in keywords:
                    if any(kw in cn for cn in cat_names):
                        return species

        # Check content
        text_lower = text.lower()
        for species, keywords in cls.SPECIES_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    return species

        return ""

    @classmethod
    def _normalize(cls, raw):
        """Normalize extracted raw values into model-compatible types."""
        result = {}

        if raw.get("animal_name"):
            result["animal_name"] = raw["animal_name"][:255]

        if raw.get("breed"):
            result["breed"] = raw["breed"][:255]

        if raw.get("identification"):
            result["identification"] = raw["identification"][:255]

        if raw.get("foster_family"):
            val = raw["foster_family"].rstrip(".")
            result["foster_family"] = val[:255]

        # Species
        species = raw.get("species", "")
        if species:
            species_lower = species.lower()
            for key, keywords in cls.SPECIES_KEYWORDS.items():
                if species_lower in keywords or species_lower == key:
                    result["species"] = key
                    break
            else:
                result["species"] = "autre"

        # Sex (check femelle first since "male" is a substring of "femelle")
        sex_val = raw.get("sex", "").lower().strip()
        if any(w in sex_val for w in ("femelle",)):
            result["sex"] = "femelle"
        elif any(w in sex_val for w in ("mâle", "male")):
            result["sex"] = "male"

        # Birth date
        birth_str = raw.get("birth_date", "")
        if birth_str:
            parsed = cls._parse_french_date(birth_str)
            if parsed:
                result["birth_date"] = parsed

        # Weight
        weight_str = raw.get("weight_kg", "")
        if weight_str:
            # Extract number, handle French comma decimal
            match = re.search(r"([\d]+[,.]?\d*)", weight_str.replace(",", "."))
            if match:
                try:
                    result["weight_kg"] = float(match.group(1))
                except ValueError:
                    pass

        # Booleans
        for field in ("is_vaccinated", "is_sterilized"):
            val = raw.get(field, "").lower()
            if val:
                if any(w in val for w in ("oui", "yes", "fait", "ok")):
                    result[field] = True
                elif any(w in val for w in ("non", "no", "pas")):
                    result[field] = False

        # Need at least species or breed to be considered an animal profile
        if not result.get("species") and not result.get("breed") and not result.get("sex"):
            return {}

        return result

    @classmethod
    def _parse_french_date(cls, text):
        """Parse dates in French formats: dd/mm/yyyy, dd-mm-yyyy, dd.mm.yyyy."""
        for fmt in (r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", r"(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})"):
            match = re.search(fmt, text)
            if match:
                groups = match.groups()
                try:
                    if len(groups[0]) == 4:
                        return date(int(groups[0]), int(groups[1]), int(groups[2]))
                    else:
                        return date(int(groups[2]), int(groups[1]), int(groups[0]))
                except (ValueError, TypeError):
                    continue
        return None

    # Regex patterns to match HTML blocks containing animal data.
    # These run directly on HTML so they handle inline tags, entities, etc.
    _HTML_BLOCK_PATTERNS = [
        # Each pattern matches a <p>...</p> or bare line containing the field label.
        # The (?:<[^>]*>)* allows inline tags like <strong>, <em>, <span> anywhere.
        r"age\s*:",
        r"(?:n[eé](?:\(e\))?\s+le|date\s+de\s+naissance)\s*:",
        r"(?:race|crois[eé])\s*:",
        r"sexe\s*:",
        r"(?:identification\s+[eé]lectronique|puce|identifi[eé])\s*:",
        r"(?:vaccin(?:[eé])?|vaccination)\s*:",
        r"(?:castr[eé]|st[eé]rilis[eé]|castration|st[eé]rilisation)\s*:",
        r"(?:poids)\s*:",
        r"(?:en\s+)?(?:famille\s+d['\u2019]?accueil|accueil)\s+(?:chez\s+)?",
        r"esp[eè]ce\s*:",
        r"(?:nom|pr[eé]nom)\s*:",
    ]

    @classmethod
    def _clean_content_html(cls, html_content):
        """Remove HTML blocks that contain animal profile data.

        Works directly on HTML, handling inline tags and entities.
        """
        cleaned = html_content

        # Decode common HTML entities for matching
        def _decode_entities(text):
            """Decode HTML entities in text for regex matching."""
            text = text.replace("&eacute;", "é")
            text = text.replace("&egrave;", "è")
            text = text.replace("&agrave;", "à")
            text = text.replace("&acirc;", "â")
            text = text.replace("&nbsp;", " ")
            text = text.replace("&#8217;", "'")
            text = text.replace("&#8216;", "'")
            text = text.replace("&rsquo;", "'")
            text = text.replace("&lsquo;", "'")
            text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
            return text

        for label_pattern in cls._HTML_BLOCK_PATTERNS:
            # Build a pattern that matches <p> blocks containing the label,
            # allowing for inline HTML tags anywhere in the text
            inline_tags = r"(?:<[^>]*>)*"
            # Inject inline_tags between each character group isn't practical,
            # so we strip tags for matching then remove the original block.

            # Strategy: find <p>...</p> blocks, check if their text matches
            p_pattern = re.compile(r"<p[^>]*>(.+?)</p>", re.DOTALL | re.IGNORECASE)
            new_parts = []
            last_end = 0

            for m in p_pattern.finditer(cleaned):
                inner_html = m.group(1)
                # Strip tags and decode entities for matching
                inner_text = re.sub(r"<[^>]+>", "", inner_html)
                inner_text = _decode_entities(inner_text).strip()

                if re.search(label_pattern, inner_text, re.IGNORECASE):
                    # Skip this <p> block (remove it)
                    new_parts.append(cleaned[last_end:m.start()])
                    last_end = m.end()

            if new_parts:
                new_parts.append(cleaned[last_end:])
                cleaned = "".join(new_parts)

            # Also handle bare lines (no <p> wrapper, separated by <br>)
            br_line = re.compile(
                r"([^\n<>]*?" + label_pattern + r"[^\n<]*?)(?:\s*<br\s*/?>)",
                re.IGNORECASE,
            )
            cleaned = br_line.sub("", cleaned)

        # Clean up empty paragraphs and excessive whitespace
        cleaned = re.sub(r"<p[^>]*>\s*</p>", "", cleaned)
        cleaned = re.sub(r"(?:\s*<br\s*/?>\s*){3,}", "<br>", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        return cleaned.strip()


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

        # Resolve categories for species detection
        ttids = rel_map.get(wp_id, [])
        category_names = []
        for ttid in ttids:
            tax_info = tax_lookup.get(ttid, {})
            tid = tax_info.get("term_id")
            taxonomy = tax_info.get("taxonomy")
            if taxonomy == "category" and tid in self.category_map:
                category_names.append(self.category_map[tid].name)

        # Extract animal profile data from content
        animal_data, cleaned_content = AnimalDataExtractor.extract(
            content, excerpt=excerpt, meta=meta, categories=category_names,
        )

        defaults = {
            "title": title,
            "slug": slug,
            "content": cleaned_content if animal_data else content,
            "excerpt": excerpt,
            "status": _map_post_status(status),
            "author": author,
            "published_at": date,
            "seo_title": seo_title or "",
            "seo_description": seo_desc or "",
        }

        # Add animal fields if extracted
        if animal_data:
            defaults.update(animal_data)
            # Use title as animal_name if not explicitly extracted
            if "animal_name" not in animal_data:
                defaults["animal_name"] = title
            defaults["is_adoptable"] = True
            logger.info("Extracted animal profile for post %d: %s", wp_id, title)

        post, _ = Post.objects.get_or_create(
            wp_post_id=wp_id,
            defaults=defaults,
        )

        # Set categories and tags
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

                    # Also redirect /?page_id=ID
                    Redirect.objects.get_or_create(
                        old_path=f"/?page_id={wp_id}",
                        defaults={"new_path": new_url},
                    )
            except Exception as e:
                logger.warning("Skipping redirect for post %d: %s", wp_id, e)

        # Generate category redirects (?cat=ID)
        for wp_term_id, category in self.category_map.items():
            try:
                new_url = category.get_absolute_url()
                Redirect.objects.get_or_create(
                    old_path=f"/?cat={wp_term_id}",
                    defaults={"new_path": new_url},
                )
                count += 1
            except Exception as e:
                logger.warning("Skipping redirect for category %d: %s", wp_term_id, e)

        # Generate tag redirects (?tag=slug)
        for wp_term_id, tag in self.tag_map.items():
            try:
                new_url = tag.get_absolute_url()
                Redirect.objects.get_or_create(
                    old_path=f"/?tag={tag.slug}",
                    defaults={"new_path": new_url},
                )
                count += 1
            except Exception as e:
                logger.warning("Skipping redirect for tag %d: %s", wp_term_id, e)

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
