from django.test import TestCase

from wordpress_import.content_processor import ContentProcessor


class ContentProcessorTest(TestCase):
    def test_rewrite_upload_urls(self):
        processor = ContentProcessor(site_url="http://example.com")
        html = '<img src="http://example.com/wp-content/uploads/2024/01/photo.jpg">'
        result = processor.process(html)
        self.assertIn("/media/uploads/2024/01/photo.jpg", result)
        self.assertNotIn("wp-content", result)

    def test_process_caption_shortcode(self):
        processor = ContentProcessor()
        html = '[caption width="300"]<img src="test.jpg"> My caption[/caption]'
        result = processor.process(html)
        self.assertIn("<figure", result)
        self.assertIn("My caption", result)

    def test_clean_empty_paragraphs(self):
        processor = ContentProcessor()
        html = "<p>Hello</p><p>  </p><p>World</p>"
        result = processor.process(html)
        self.assertNotIn("<p>  </p>", result)

    def test_lazy_loading(self):
        processor = ContentProcessor()
        html = '<img src="test.jpg" alt="test">'
        result = processor.process(html)
        self.assertIn('loading="lazy"', result)

    def test_internal_link_rewrite(self):
        processor = ContentProcessor(site_url="http://example.com")
        html = '<a href="http://example.com/my-page/">Link</a>'
        result = processor.process(html)
        self.assertIn('href="/my-page/"', result)
