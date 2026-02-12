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

    def test_extract_from_meta(self):
        content = "<p>Description libre.</p>"
        meta = {"race": "berger allemand", "sexe": "male", "espece": "chien"}
        data, cleaned = AnimalDataExtractor.extract(content, meta=meta)
        self.assertEqual(data["breed"], "berger allemand")
        self.assertEqual(data["species"], "chien")
