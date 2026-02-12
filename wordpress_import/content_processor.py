"""
WordPress content processor.

Transforms WordPress HTML content for Django:
- Rewrites internal URLs (wp-content/uploads -> /media/uploads)
- Converts WordPress shortcodes to HTML
- Cleans up WordPress-specific markup
- Fixes image paths
"""

import re
import logging

from django.conf import settings

logger = logging.getLogger("wordpress_import")

# Regex to match <img> tags (including self-closing)
IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
# Extract src attribute from <img> tag
IMG_SRC_RE = re.compile(r'src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
# Extract alt attribute from <img> tag
IMG_ALT_RE = re.compile(r'alt\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
# Match wrapping <a> around <img> (common WP pattern)
A_IMG_RE = re.compile(
    r"<a\b[^>]*>\s*(<img\b[^>]*>)\s*</a>",
    re.IGNORECASE | re.DOTALL,
)
# Match <figure> wrapping <img> or <a><img></a>
FIGURE_IMG_RE = re.compile(
    r"<figure\b[^>]*>\s*(?:<a\b[^>]*>\s*)?(<img\b[^>]*>)(?:\s*</a>)?\s*(?:<figcaption\b[^>]*>.*?</figcaption>)?\s*</figure>",
    re.IGNORECASE | re.DOTALL,
)
# Match <p> containing only an <img> (or <a><img></a>)
P_IMG_RE = re.compile(
    r"<p>\s*(?:<a\b[^>]*>\s*)?(<img\b[^>]*>)(?:\s*</a>)?\s*</p>",
    re.IGNORECASE | re.DOTALL,
)


class ContentProcessor:
    """Process and clean WordPress HTML content for Django."""

    # Common WordPress shortcodes
    SHORTCODE_RE = re.compile(r"\[(\w+)([^\]]*)\](?:(.*?)\[/\1\])?", re.DOTALL)

    def __init__(self, site_url=""):
        self.site_url = site_url.rstrip("/")

    def process(self, content):
        """Apply all content transformations."""
        if not content:
            return ""

        content = self._rewrite_upload_urls(content)
        content = self._rewrite_internal_links(content)
        content = self._process_shortcodes(content)
        content = self._clean_wp_markup(content)
        content = self._fix_image_tags(content)

        return content

    def extract_images(self, content, featured_image_url=""):
        """Extract image URLs from content and return (cleaned_content, image_list).

        Each image in the returned list is a dict with 'src' and 'alt' keys.
        Images matching featured_image_url are removed from the content but
        NOT added to the gallery list (they are already shown as featured image).
        The content is returned with all upload image tags (and their wrappers) removed.
        """
        if not content:
            return "", []

        images = []
        seen_srcs = set()

        # Normalize featured image URL for comparison
        featured_norm = self._normalize_upload_url(featured_image_url) if featured_image_url else ""

        def _collect_img(img_tag):
            """Parse an <img> tag and collect it if it's an upload image."""
            src_match = IMG_SRC_RE.search(img_tag)
            if not src_match:
                return False
            src = src_match.group(1)

            # Only extract images that look like uploaded media
            if "/uploads/" not in src and "/wp-content/" not in src:
                return False

            src_norm = self._normalize_upload_url(src)

            # Featured image: remove from content but don't add to gallery
            if featured_norm and src_norm == featured_norm:
                return True

            if src_norm in seen_srcs:
                return True  # Duplicate, still remove from content
            seen_srcs.add(src_norm)

            alt_match = IMG_ALT_RE.search(img_tag)
            alt = alt_match.group(1) if alt_match else ""
            images.append({"src": src, "alt": alt})
            return True

        # Process in order: <figure> wraps, then <p> wraps, then <a> wraps, then bare <img>
        # Track which img tags have been handled
        handled_imgs = set()

        def _replace_figure(match):
            img_tag = match.group(1)
            if _collect_img(img_tag):
                handled_imgs.add(img_tag)
                return ""
            return match.group(0)

        content = FIGURE_IMG_RE.sub(_replace_figure, content)

        def _replace_p_img(match):
            img_tag = match.group(1)
            if img_tag in handled_imgs:
                return ""
            if _collect_img(img_tag):
                handled_imgs.add(img_tag)
                return ""
            return match.group(0)

        content = P_IMG_RE.sub(_replace_p_img, content)

        def _replace_a_img(match):
            img_tag = match.group(1)
            if img_tag in handled_imgs:
                return ""
            if _collect_img(img_tag):
                handled_imgs.add(img_tag)
                return ""
            return match.group(0)

        content = A_IMG_RE.sub(_replace_a_img, content)

        def _replace_bare_img(match):
            img_tag = match.group(0)
            if img_tag in handled_imgs:
                return ""
            if _collect_img(img_tag):
                return ""
            return match.group(0)

        content = IMG_TAG_RE.sub(_replace_bare_img, content)

        # Clean up leftover empty paragraphs
        content = re.sub(r"<p>\s*</p>", "", content)

        return content, images

    def _normalize_upload_url(self, url):
        """Normalize an upload URL to just the relative path for comparison."""
        if not url:
            return ""
        # Strip to just uploads/YYYY/MM/filename.ext
        match = re.search(r"uploads/(.+)$", url)
        if match:
            # Remove size suffixes like -300x200
            path = match.group(1)
            path = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", path)
            return path
        return url

    def _rewrite_upload_urls(self, content):
        """Rewrite wp-content/uploads URLs to Django media URLs."""
        # Match absolute URLs to uploads
        if self.site_url:
            content = content.replace(
                f"{self.site_url}/wp-content/uploads/",
                f"{settings.MEDIA_URL}uploads/",
            )

        # Match relative URLs to uploads
        content = re.sub(
            r'(?:(?:https?://[^/]+)?/wp-content/uploads/)',
            f"{settings.MEDIA_URL}uploads/",
            content,
        )

        return content

    def _rewrite_internal_links(self, content):
        """Rewrite WordPress internal page/post links."""
        if not self.site_url:
            return content

        # Replace absolute site URLs with relative paths
        content = content.replace(f'{self.site_url}/', "/")
        content = content.replace(self.site_url, "/")

        return content

    def _process_shortcodes(self, content):
        """Convert WordPress shortcodes to HTML equivalents."""

        def replace_shortcode(match):
            tag = match.group(1)
            attrs_str = match.group(2) or ""
            inner = match.group(3) or ""

            attrs = self._parse_shortcode_attrs(attrs_str)

            # Caption shortcode
            if tag == "caption":
                caption_text = inner.strip()
                width = attrs.get("width", "")
                align = attrs.get("align", "")
                css_class = f"wp-caption {align}".strip()
                style = f"width: {width}px;" if width else ""
                return (
                    f'<figure class="{css_class}" style="{style}">'
                    f"{caption_text}</figure>"
                )

            # Gallery shortcode
            if tag == "gallery":
                ids = attrs.get("ids", "")
                return f'<div class="wp-gallery" data-ids="{ids}"></div>'

            # Video shortcodes
            if tag in ("youtube", "vimeo", "video"):
                src = attrs.get("src", "") or attrs.get("url", "") or inner
                if src:
                    return (
                        f'<div class="video-embed">'
                        f'<iframe src="{src}" frameborder="0" allowfullscreen></iframe>'
                        f"</div>"
                    )

            # Audio shortcode
            if tag == "audio":
                src = attrs.get("src", "") or attrs.get("mp3", "")
                if src:
                    return f'<audio controls src="{src}"></audio>'

            # Embed shortcode
            if tag == "embed":
                return inner

            # Code shortcode
            if tag == "code":
                lang = attrs.get("language", "") or attrs.get("lang", "")
                return f'<pre><code class="language-{lang}">{inner}</code></pre>'

            # Default: just return inner content or empty
            if inner:
                return inner
            return ""

        content = self.SHORTCODE_RE.sub(replace_shortcode, content)
        return content

    def _parse_shortcode_attrs(self, attrs_str):
        """Parse WordPress shortcode attributes."""
        attrs = {}
        # Match key="value" or key='value' or key=value
        for match in re.finditer(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))', attrs_str):
            key = match.group(1)
            value = match.group(2) or match.group(3) or match.group(4) or ""
            attrs[key] = value
        return attrs

    def _clean_wp_markup(self, content):
        """Remove WordPress-specific markup and classes."""
        # Remove WordPress alignment classes on images (keep img tag)
        content = re.sub(r'\s*class="[^"]*wp-image-\d+[^"]*"', "", content)

        # Remove empty paragraphs
        content = re.sub(r"<p>\s*</p>", "", content)

        # Convert WordPress <!--more--> tag
        content = content.replace("<!--more-->", '<span id="more"></span>')

        # Remove WordPress <!--nextpage--> tag
        content = content.replace("<!--nextpage-->", "")

        return content

    def _fix_image_tags(self, content):
        """Ensure image tags have proper attributes."""
        # Add loading="lazy" to images that don't have it
        content = re.sub(
            r"<img(?![^>]*loading=)([^>]*?)(/?)>",
            r'<img loading="lazy"\1\2>',
            content,
        )
        return content


def process_all_content(site_url="", extract_gallery=True):
    """Process content for all posts and pages in the database.

    If extract_gallery is True, images are extracted from post content
    and stored as PostGalleryImage entries.
    """
    from blog.models import Post, Page, Media, PostGalleryImage

    processor = ContentProcessor(site_url=site_url)
    count = 0
    gallery_count = 0

    for post in Post.objects.select_related("featured_image").all():
        new_content = processor.process(post.content)

        if extract_gallery:
            featured_url = ""
            if post.featured_image and post.featured_image.original_url:
                featured_url = post.featured_image.original_url
            elif post.featured_image and post.featured_image.file:
                featured_url = post.featured_image.file.name

            new_content, images = processor.extract_images(new_content, featured_url)

            for position, img_data in enumerate(images):
                media = _find_media_by_url(img_data["src"])
                if media:
                    PostGalleryImage.objects.get_or_create(
                        post=post, media=media,
                        defaults={"position": position},
                    )
                    gallery_count += 1

        if new_content != post.content:
            post.content = new_content
            post.save(update_fields=["content"])
            count += 1

    for page in Page.objects.all():
        new_content = processor.process(page.content)
        if new_content != page.content:
            page.content = new_content
            page.save(update_fields=["content"])
            count += 1

    logger.info("Processed content for %d posts/pages, extracted %d gallery images", count, gallery_count)
    return count


def _find_media_by_url(src):
    """Find a Media object matching an image URL."""
    from blog.models import Media

    # Try matching by original_url
    if src:
        media = Media.objects.filter(original_url__endswith=src.split("/uploads/")[-1]).first()
        if media:
            return media

        # Try matching by file path
        match = re.search(r"uploads/(.+)$", src)
        if match:
            path = match.group(1)
            # Remove size suffix for matching
            base_path = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", path)
            media = Media.objects.filter(file__endswith=base_path).first()
            if media:
                return media
            # Try with the exact path (might include size suffix)
            if path != base_path:
                media = Media.objects.filter(file__endswith=path).first()
                if media:
                    return media

    return None
