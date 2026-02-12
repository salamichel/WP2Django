from datetime import date

from django.test import TestCase

from wordpress_import.content_processor import ContentProcessor
from wordpress_import.importers import AnimalDataExtractor


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
class AnimalDataExtractorTest(TestCase):
    def test_extract_full_profile(self):
        content = (
            "<p>Age : 3 mois</p>"
            "<p>Né le : 29/10/2025</p>"
            "<p>Race : croisé</p>"
            "<p>Sexe : mâle</p>"
            "<p>Identification électronique : 250269611651491</p>"
            "<p>Vaccin : oui</p>"
            "<p>Castré : non car trop jeune</p>"
            "<p>Poids : 9,6 kg</p>"
            "<p>En accueil chez Jacqueline.</p>"
            "<p>Arnold est calme mais il adore jouer.</p>"
        )
        data, cleaned = AnimalDataExtractor.extract(
            content, categories=["Chiens"]
        )
        self.assertEqual(data["species"], "chien")
        self.assertEqual(data["sex"], "male")
        self.assertEqual(data["breed"], "croisé")
        self.assertEqual(data["birth_date"], date(2025, 10, 29))
        self.assertAlmostEqual(float(data["weight_kg"]), 9.6)
        self.assertEqual(data["identification"], "250269611651491")
        self.assertTrue(data["is_vaccinated"])
        self.assertFalse(data["is_sterilized"])
        self.assertEqual(data["foster_family"], "Jacqueline")
        # HTML should be cleaned of all data lines
        self.assertNotIn("Race :", cleaned)
        self.assertNotIn("Sexe :", cleaned)
        self.assertNotIn("Vaccin :", cleaned)
        self.assertNotIn("Poids :", cleaned)
        self.assertNotIn("accueil chez", cleaned)
        self.assertNotIn("<p>Age", cleaned)
        self.assertIn("Arnold est calme", cleaned)

    def test_html_cleaning_with_inline_tags(self):
        """Ensure HTML is cleaned even when fields have inline tags."""
        content = (
            "<p><strong>Race</strong> : berger allemand</p>"
            "<p>Sexe : <em>mâle</em></p>"
            "<p>Vaccin&eacute; : oui</p>"
            "<p>Description de l'animal tres gentil.</p>"
        )
        data, cleaned = AnimalDataExtractor.extract(
            content, categories=["Chiens"]
        )
        self.assertEqual(data["breed"], "berger allemand")
        # All data <p> blocks should be removed from HTML
        self.assertNotIn("Race", cleaned)
        self.assertNotIn("Sexe", cleaned)
        self.assertNotIn("Vaccin", cleaned)
        self.assertIn("Description de l'animal", cleaned)

    def test_narrative_text_with_keywords_preserved(self):
        """Narrative text mentioning keywords like 'vaccin' must NOT be removed."""
        content = (
            "<p>Race : croisé</p>"
            "<p>Sexe : mâle</p>"
            "<p>Vaccin : oui</p>"
            "<p>Castré : non car trop jeune</p>"
            "<p>En accueil chez Jacqueline.</p>"
            "<p>Arnold est calme et il a été vacciné la semaine dernière. "
            "Il est en accueil dans une famille aimante.</p>"
            "<p>Il adore jouer avec ses sœurs.</p>"
        )
        data, cleaned = AnimalDataExtractor.extract(
            content, categories=["Chiens"]
        )
        # Data lines should be removed
        self.assertNotIn("<p>Race : croisé</p>", cleaned)
        self.assertNotIn("<p>Vaccin : oui</p>", cleaned)
        # Narrative paragraphs with keywords must be PRESERVED
        self.assertIn("Arnold est calme", cleaned)
        self.assertIn("vacciné la semaine", cleaned)
        self.assertIn("accueil dans une famille", cleaned)
        self.assertIn("adore jouer", cleaned)

    def test_no_animal_data(self):
        content = "<p>Actualité de l'association cette semaine.</p>"
        data, cleaned = AnimalDataExtractor.extract(content)
        self.assertEqual(data, {})
        self.assertEqual(cleaned, content)

    def test_species_detection_from_categories(self):
        content = "<p>Race : siamois</p><p>Sexe : femelle</p>"
        data, cleaned = AnimalDataExtractor.extract(
            content, categories=["Chatons"]
        )
        self.assertEqual(data["species"], "chat")
        self.assertEqual(data["sex"], "femelle")

    def test_colored_span_html_format(self):
        """Real WordPress format: colored spans with inline labels, no <p> blocks."""
        content = (
            '<span style="color: #ff00ff;"><strong>Age :&nbsp;</strong></span>3 mois\n'
            '<span style="color: #ff00ff;"><strong>N\u00e9e le :</strong></span>&nbsp;29/10/2025\n'
            '<b><strong><span style="color: #ff00ff;">Race :</span>&nbsp;</strong></b>crois\u00e9e\n'
            '<span style="color: #ff00ff;"><b><strong>Sexe :</strong></b>&nbsp;</span>femelle\n'
            '<span style="color: #ff00ff;"><b><strong>Identification \u00e9lectronique :&nbsp;</strong></b></span>250269611649979\n'
            '<b><span style="color: #ff00ff;"><strong>Vaccin :</strong></span>&nbsp;</b>oui\n'
            '<span style="color: #ff00ff;"><b><strong>St\u00e9rilis\u00e9e :&nbsp;</strong></b></span>non car trop jeune\n'
            '<span style="color: #ff00ff;"><strong>Caract\u00e8re et histoire :</strong>&nbsp;</span>'
            'Yuffie est la fille de Kid\u00e9lia. Et la soeur de Arnold.\n'
            'Yuffie adore jouer avec ses soeurs et son fr\u00e8re.\n'
            'Poids : 9,5 kg.\n'
            '<div dir="ltr">En accueil chez Jacqueline.</div>\n'
            '<div dir="ltr"><a href="/media/uploads/photo.jpg">'
            '<img src="/media/uploads/photo.jpg"></a></div>'
        )
        data, cleaned = AnimalDataExtractor.extract(
            content, categories=["Chiens"]
        )
        # All structured fields extracted
        self.assertEqual(data["species"], "chien")
        self.assertEqual(data["sex"], "femelle")
        self.assertEqual(data["breed"], "crois\u00e9e")
        self.assertEqual(data["birth_date"], date(2025, 10, 29))
        self.assertAlmostEqual(float(data["weight_kg"]), 9.5)
        self.assertEqual(data["identification"], "250269611649979")
        self.assertTrue(data["is_vaccinated"])
        self.assertFalse(data["is_sterilized"])
        self.assertEqual(data["foster_family"], "Jacqueline")
        # Data lines removed from HTML
        self.assertNotIn("Age :", cleaned)
        self.assertNotIn("Race :", cleaned)
        self.assertNotIn("Sexe :", cleaned)
        self.assertNotIn("Vaccin :", cleaned)
        self.assertNotIn("Poids :", cleaned)
        self.assertNotIn("accueil chez", cleaned)
        # Narrative text preserved
        self.assertIn("Yuffie est la fille", cleaned)
        self.assertIn("Yuffie adore jouer", cleaned)
        # Image preserved
        self.assertIn("photo.jpg", cleaned)

    def test_extract_from_meta(self):
        content = "<p>Description libre.</p>"
        meta = {"race": "berger allemand", "sexe": "male", "espece": "chien"}
        data, cleaned = AnimalDataExtractor.extract(content, meta=meta)
        self.assertEqual(data["breed"], "berger allemand")
        self.assertEqual(data["species"], "chien")
