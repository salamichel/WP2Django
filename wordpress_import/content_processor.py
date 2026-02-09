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


def process_all_content(site_url=""):
    """Process content for all posts and pages in the database."""
    from blog.models import Post, Page

    processor = ContentProcessor(site_url=site_url)
    count = 0

    for post in Post.objects.all():
        new_content = processor.process(post.content)
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

    logger.info("Processed content for %d posts/pages", count)
    return count
