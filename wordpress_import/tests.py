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


class ExtractImagesTest(TestCase):
    def setUp(self):
        self.processor = ContentProcessor(site_url="http://example.com")

    def test_extract_bare_img(self):
        html = '<p>Text</p><img src="/media/uploads/2024/01/photo.jpg" alt="A photo"><p>More text</p>'
        content, images = self.processor.extract_images(html)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["src"], "/media/uploads/2024/01/photo.jpg")
        self.assertEqual(images[0]["alt"], "A photo")
        self.assertNotIn("<img", content)
        self.assertIn("Text", content)
        self.assertIn("More text", content)

    def test_extract_img_in_figure(self):
        html = '<figure><img src="/media/uploads/2024/01/cat.jpg" alt="Cat"><figcaption>A cat</figcaption></figure>'
        content, images = self.processor.extract_images(html)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["src"], "/media/uploads/2024/01/cat.jpg")
        self.assertNotIn("<figure", content)

    def test_extract_img_in_a_tag(self):
        html = '<a href="/media/uploads/2024/01/big.jpg"><img src="/media/uploads/2024/01/big.jpg" alt="Big"></a>'
        content, images = self.processor.extract_images(html)
        self.assertEqual(len(images), 1)
        self.assertNotIn("<a", content)

    def test_extract_img_in_p_tag(self):
        html = '<p><img src="/media/uploads/2024/01/dog.jpg" alt="Dog"></p>'
        content, images = self.processor.extract_images(html)
        self.assertEqual(len(images), 1)
        self.assertNotIn("<p>", content)

    def test_featured_image_removed_from_content_but_not_in_gallery(self):
        html = '<img src="/media/uploads/2024/01/featured.jpg" alt="Featured"><img src="/media/uploads/2024/01/other.jpg" alt="Other">'
        content, images = self.processor.extract_images(
            html, featured_image_url="/media/uploads/2024/01/featured.jpg"
        )
        # Featured image removed from content
        self.assertNotIn("featured.jpg", content)
        # But not added to the gallery list
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["src"], "/media/uploads/2024/01/other.jpg")

    def test_featured_image_with_size_suffix_removed_from_content(self):
        html = '<img src="/media/uploads/2024/01/featured-300x200.jpg" alt="Featured"><img src="/media/uploads/2024/01/other.jpg" alt="Other">'
        content, images = self.processor.extract_images(
            html, featured_image_url="/media/uploads/2024/01/featured.jpg"
        )
        # Size-suffixed featured image also removed from content
        self.assertNotIn("featured-300x200.jpg", content)
        # But not in gallery
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["src"], "/media/uploads/2024/01/other.jpg")

    def test_skip_non_upload_images(self):
        html = '<img src="https://external.com/logo.png" alt="Logo"><img src="/media/uploads/2024/01/local.jpg" alt="Local">'
        content, images = self.processor.extract_images(html)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["src"], "/media/uploads/2024/01/local.jpg")
        self.assertIn("external.com/logo.png", content)

    def test_no_duplicate_images(self):
        html = '<img src="/media/uploads/2024/01/photo.jpg"><img src="/media/uploads/2024/01/photo.jpg">'
        content, images = self.processor.extract_images(html)
        self.assertEqual(len(images), 1)

    def test_empty_content(self):
        content, images = self.processor.extract_images("")
        self.assertEqual(content, "")
        self.assertEqual(images, [])

    def test_content_without_images(self):
        html = "<p>Just text, no images here.</p>"
        content, images = self.processor.extract_images(html)
        self.assertEqual(images, [])
        self.assertEqual(content, html)
