from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone

from blog.models import Post, Page, Category, Tag, Comment, Menu, MenuItem, Redirect, Media, PostGalleryImage


class CategoryModelTest(TestCase):
    def test_auto_slug(self):
        cat = Category.objects.create(name="Test Category")
        self.assertEqual(cat.slug, "test-category")

    def test_str(self):
        cat = Category.objects.create(name="Tech", slug="tech")
        self.assertEqual(str(cat), "Tech")

    def test_get_absolute_url(self):
        cat = Category.objects.create(name="Tech", slug="tech")
        self.assertEqual(cat.get_absolute_url(), "/categories/tech/")

        cat_adoptes_2026 = Category.objects.create(name="Les Adoptés 2026", slug="les-adoptes-2026")
        self.assertEqual(cat_adoptes_2026.get_absolute_url(), "/categories/les-adoptes/2026/")

    def test_parent_relationship(self):
        parent = Category.objects.create(name="Parent", slug="parent")
        child = Category.objects.create(name="Child", slug="child", parent=parent)
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())


class TagModelTest(TestCase):
    def test_auto_slug(self):
        tag = Tag.objects.create(name="Python Tips")
        self.assertEqual(tag.slug, "python-tips")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "pass")
        self.cat = Category.objects.create(name="Tech", slug="tech")
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="<p>Hello world</p>",
            status="published",
            author=self.user,
            published_at=timezone.now(),
        )
        self.post.categories.add(self.cat)

    def test_str(self):
        self.assertEqual(str(self.post), "Test Post")

    def test_get_absolute_url(self):
        self.assertEqual(self.post.get_absolute_url(), "/articles/test-post/")

    def test_category_relation(self):
        self.assertIn(self.cat, self.post.categories.all())
        self.assertIn(self.post, self.cat.posts.all())


class PageModelTest(TestCase):
    def test_get_absolute_url(self):
        page = Page.objects.create(title="About", slug="about", status="published")
        self.assertEqual(page.get_absolute_url(), "/about/")


class CommentModelTest(TestCase):
    def test_comment_str(self):
        user = User.objects.create_user("author", "a@a.com", "pass")
        post = Post.objects.create(title="P", slug="p", status="published", author=user, published_at=timezone.now())
        comment = Comment.objects.create(post=post, author_name="John", content="Nice!", status="approved")
        self.assertIn("John", str(comment))


class PostGalleryImageModelTest(TestCase):
    def test_str(self):
        user = User.objects.create_user("author", "a@a.com", "pass")
        post = Post.objects.create(title="My Post", slug="my-post", status="published", author=user, published_at=timezone.now())
        media = Media.objects.create(title="Photo", file="uploads/2024/01/photo.jpg", mime_type="image/jpeg")
        gi = PostGalleryImage.objects.create(post=post, media=media, position=0)
        self.assertIn("My Post", str(gi))
        self.assertIn("Photo", str(gi))

    def test_unique_together(self):
        user = User.objects.create_user("author", "a@a.com", "pass")
        post = Post.objects.create(title="P", slug="p", status="published", author=user, published_at=timezone.now())
        media = Media.objects.create(title="M", file="uploads/2024/01/m.jpg", mime_type="image/jpeg")
        PostGalleryImage.objects.create(post=post, media=media, position=0)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            PostGalleryImage.objects.create(post=post, media=media, position=1)

    def test_ordering(self):
        user = User.objects.create_user("author", "a@a.com", "pass")
        post = Post.objects.create(title="P", slug="p", status="published", author=user, published_at=timezone.now())
        m1 = Media.objects.create(title="First", file="uploads/2024/01/a.jpg", mime_type="image/jpeg")
        m2 = Media.objects.create(title="Second", file="uploads/2024/01/b.jpg", mime_type="image/jpeg")
        PostGalleryImage.objects.create(post=post, media=m2, position=1)
        PostGalleryImage.objects.create(post=post, media=m1, position=0)
        images = list(post.gallery_images.all())
        self.assertEqual(images[0].media, m1)
        self.assertEqual(images[1].media, m2)


class RedirectModelTest(TestCase):
    def test_str(self):
        r = Redirect.objects.create(old_path="/old/", new_path="/new/")
        self.assertEqual(str(r), "/old/ -> /new/")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", "test@test.com", "pass")
        self.cat = Category.objects.create(name="Tech", slug="tech")
        self.tag = Tag.objects.create(name="Python", slug="python")
        self.post = Post.objects.create(
            title="Published Post",
            slug="published-post",
            content="<p>Content</p>",
            excerpt="Short excerpt",
            status="published",
            author=self.user,
            published_at=timezone.now(),
        )
        self.post.categories.add(self.cat)
        self.post.tags.add(self.tag)
        self.page = Page.objects.create(
            title="About Us",
            slug="about-us",
            content="<p>About</p>",
            status="published",
        )

    def test_home(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Published Post")

    def test_post_list(self):
        resp = self.client.get("/articles/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Published Post")

    def test_post_detail(self):
        resp = self.client.get("/articles/published-post/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Content")

    def test_post_detail_with_gallery(self):
        m1 = Media.objects.create(title="Gallery1", file="uploads/2024/01/g1.jpg", mime_type="image/jpeg")
        m2 = Media.objects.create(title="Gallery2", file="uploads/2024/01/g2.jpg", mime_type="image/jpeg")
        PostGalleryImage.objects.create(post=self.post, media=m1, position=0)
        PostGalleryImage.objects.create(post=self.post, media=m2, position=1)
        resp = self.client.get("/articles/published-post/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Galerie photos")
        self.assertContains(resp, "glightbox")
        self.assertContains(resp, "g1.jpg")
        self.assertContains(resp, "g2.jpg")

    def test_post_detail_without_gallery(self):
        resp = self.client.get("/articles/published-post/")
        self.assertNotContains(resp, "Galerie photos")
        self.assertNotContains(resp, "glightbox.min.css")

    def test_post_detail_draft_returns_404(self):
        Post.objects.create(title="Draft", slug="draft", status="draft", published_at=timezone.now())
        resp = self.client.get("/articles/draft/")
        self.assertEqual(resp.status_code, 404)

    def test_page_detail(self):
        resp = self.client.get("/about-us/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "About")

    def test_category_page(self):
        resp = self.client.get("/categorie/tech/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Published Post")

    def test_tag_page(self):
        resp = self.client.get("/tag/python/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Published Post")

    def test_search(self):
        resp = self.client.get("/recherche/?q=Published")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Published Post")

    def test_search_empty(self):
        resp = self.client.get("/recherche/?q=nonexistent")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "0 résultat")
        self.assertContains(resp, "Aucun résultat trouvé")

    def test_archive_year(self):
        year = self.post.published_at.year
        resp = self.client.get(f"/archives/{year}/")
        self.assertEqual(resp.status_code, 200)

    def test_feed(self):
        resp = self.client.get("/feed/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/rss+xml; charset=utf-8")

    def test_sitemap(self):
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)


class RedirectMiddlewareTest(TestCase):
    def test_redirect_permanent(self):
        Redirect.objects.create(old_path="/old-post/", new_path="/articles/new-post/", is_permanent=True)
        resp = self.client.get("/old-post/")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "/articles/new-post/")

    def test_redirect_temporary(self):
        Redirect.objects.create(old_path="/temp/", new_path="/new-temp/", is_permanent=False)
        resp = self.client.get("/temp/")
        self.assertEqual(resp.status_code, 302)

    def test_redirect_wp_post_id(self):
        Redirect.objects.create(old_path="/?p=42", new_path="/articles/mon-article/")
        resp = self.client.get("/?p=42")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "/articles/mon-article/")

    def test_redirect_wp_page_id(self):
        Redirect.objects.create(old_path="/?page_id=219", new_path="/ma-page/")
        resp = self.client.get("/?page_id=219")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "/ma-page/")

    def test_redirect_wp_cat(self):
        Redirect.objects.create(old_path="/?cat=71", new_path="/categorie/chiens/")
        resp = self.client.get("/?cat=71")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "/categorie/chiens/")

    def test_redirect_wp_tag(self):
        Redirect.objects.create(old_path="/?tag=adoption", new_path="/tag/adoption/")
        resp = self.client.get("/?tag=adoption")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "/tag/adoption/")


class ContactViewTest(TestCase):
    def test_contact_get(self):
        resp = self.client.get("/contact/")
        self.assertEqual(resp.status_code, 200)

    def test_contact_post_valid(self):
        resp = self.client.post("/contact/", {
            "name": "John",
            "email": "john@example.com",
            "subject": "Test",
            "message": "Hello!",
        })
        self.assertEqual(resp.status_code, 302)


class SQLParserTest(TestCase):
    def test_parse_simple_insert(self):
        from wordpress_import.sql_parser import SQLParser
        import tempfile
        import os

        sql = """
CREATE TABLE `wp_options` (
  `option_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `option_name` varchar(191) NOT NULL DEFAULT '',
  `option_value` longtext NOT NULL,
  `autoload` varchar(20) NOT NULL DEFAULT 'yes'
) ENGINE=InnoDB;

INSERT INTO `wp_options` (`option_id`, `option_name`, `option_value`, `autoload`) VALUES
(1, 'siteurl', 'http://example.com', 'yes'),
(2, 'blogname', 'Mon Blog', 'yes');

CREATE TABLE `wp_posts` (
  `ID` bigint(20) unsigned NOT NULL,
  `post_author` bigint(20) unsigned NOT NULL DEFAULT 0,
  `post_title` text NOT NULL,
  `post_name` varchar(200) NOT NULL DEFAULT '',
  `post_content` longtext NOT NULL,
  `post_excerpt` text NOT NULL,
  `post_status` varchar(20) NOT NULL DEFAULT 'publish',
  `post_type` varchar(20) NOT NULL DEFAULT 'post',
  `post_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_modified` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_parent` bigint(20) unsigned NOT NULL DEFAULT 0,
  `post_mime_type` varchar(100) NOT NULL DEFAULT '',
  `menu_order` int(11) NOT NULL DEFAULT 0,
  `guid` varchar(255) NOT NULL DEFAULT ''
) ENGINE=InnoDB;

INSERT INTO `wp_posts` VALUES
(1, 1, 'Hello World', 'hello-world', '<p>Welcome!</p>', '', 'publish', 'post', '2024-01-15 10:00:00', '2024-01-15 10:00:00', 0, '', 0, 'http://example.com/?p=1');
"""
        fd, path = tempfile.mkstemp(suffix=".sql")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(sql)

            parser = SQLParser(path)
            tables = parser.parse()

            self.assertIn("wp_options", tables)
            self.assertIn("wp_posts", tables)
            self.assertEqual(len(tables["wp_options"]["rows"]), 2)
            self.assertEqual(tables["wp_options"]["rows"][0]["option_name"], "siteurl")
            self.assertEqual(len(tables["wp_posts"]["rows"]), 1)
            self.assertEqual(tables["wp_posts"]["rows"][0]["post_title"], "Hello World")
            self.assertEqual(parser.table_prefix, "wp_")
            self.assertIn("options", parser.get_core_tables())
            self.assertIn("posts", parser.get_core_tables())
        finally:
            os.unlink(path)

    def test_columns_exclude_keys_and_indexes(self):
        """Ensure KEY/PRIMARY KEY/UNIQUE KEY lines are not parsed as columns."""
        from wordpress_import.sql_parser import SQLParser
        import tempfile
        import os

        sql = """
CREATE TABLE `wp_users` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_login` varchar(60) NOT NULL DEFAULT '',
  `user_email` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  KEY `user_login_key` (`user_login`),
  UNIQUE KEY `user_email` (`user_email`)
) ENGINE=InnoDB;

INSERT INTO `wp_users` VALUES (1, 'admin', 'admin@example.com');
"""
        fd, path = tempfile.mkstemp(suffix=".sql")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(sql)

            parser = SQLParser(path)
            tables = parser.parse()

            # Should only have 3 real columns, not 6 (with KEY names)
            self.assertEqual(tables["wp_users"]["columns"], ["ID", "user_login", "user_email"])
            self.assertEqual(len(tables["wp_users"]["rows"]), 1)
            # Values should map to column names, not index-based keys
            row = tables["wp_users"]["rows"][0]
            self.assertEqual(row["ID"], 1)
            self.assertEqual(row["user_login"], "admin")
            self.assertEqual(row["user_email"], "admin@example.com")
        finally:
            os.unlink(path)

    def test_parse_escaped_strings(self):
        from wordpress_import.sql_parser import SQLParser
        import tempfile
        import os

        sql = """
CREATE TABLE `wp_posts` (
  `ID` bigint(20) unsigned NOT NULL,
  `post_title` text NOT NULL
) ENGINE=InnoDB;

INSERT INTO `wp_posts` VALUES (1, 'It\\'s a test');
"""
        fd, path = tempfile.mkstemp(suffix=".sql")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(sql)

            parser = SQLParser(path)
            tables = parser.parse()
            self.assertEqual(tables["wp_posts"]["rows"][0]["post_title"], "It's a test")
        finally:
            os.unlink(path)


class AdoptionAndEmergencyFeaturesTest(TestCase):
    def setUp(self):
        from blog.models import Post
        self.dog = Post.objects.create(
            title="Max - Chien adorable",
            slug="max-chien-adorable",
            animal_name="Max",
            species="chien",
            sex="male",
            weight_kg=15.5,
            adoption_status="adoptable",
            is_adoptable=True,
            ok_dogs="oui",
            ok_cats="non",
            ok_children="oui",
            housing_requirement="maison",
            is_emergency=True,
            status="published",
        )
        self.cat = Post.objects.create(
            title="Bella - Chatte douce",
            slug="bella-chatte-douce",
            animal_name="Bella",
            species="chat",
            sex="femelle",
            adoption_status="recherche_fa",
            is_adoptable=False,
            ok_dogs="non",
            ok_cats="oui",
            ok_children="oui",
            housing_requirement="appartement",
            is_emergency=False,
            status="published",
        )

    def test_home_page_emergency_posts(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("emergency_posts", resp.context)
        emergency_slugs = [p.slug for p in resp.context["emergency_posts"]]
        self.assertIn("max-chien-adorable", emergency_slugs)
        self.assertIn("bella-chatte-douce", emergency_slugs)

    def test_post_list_filtering(self):
        # Filter dogs only
        resp = self.client.get("/articles/?species=chien")
        self.assertEqual(resp.status_code, 200)
        posts = resp.context["posts"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].slug, "max-chien-adorable")

        # Filter emergency only
        resp = self.client.get("/articles/?emergency=1")
        self.assertEqual(resp.status_code, 200)
        posts = resp.context["posts"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].slug, "max-chien-adorable")

        # Filter recherche_fa status
        resp = self.client.get("/articles/?status=recherche_fa")
        self.assertEqual(resp.status_code, 200)
        posts = resp.context["posts"]
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].slug, "bella-chatte-douce")

        # Filter search keyword q
        resp = self.client.get("/articles/?q=adorable")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["posts"]), 1)
        self.assertEqual(resp.context["posts"][0].animal_name, "Max")

        # Filter combined
        resp = self.client.get("/articles/?species=chat&status=recherche_fa&ok_cats=oui")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["posts"]), 1)
        self.assertEqual(resp.context["posts"][0].slug, "bella-chatte-douce")

    def test_post_list_ajax_response(self):
        resp = self.client.get("/articles/?species=chien", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "includes/_post_grid.html")
        self.assertContains(resp, "Max")
        self.assertNotContains(resp, "Bella")

    def test_category_unified_filter(self):
        Category.objects.get_or_create(name="Chiens", slug="chiens")
        resp = self.client.get("/categorie/chiens/")
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "blog/post_list.html")
        self.assertEqual(resp.context["filters"]["species"], "chien")
        self.assertEqual(len(resp.context["posts"]), 1)
        self.assertEqual(resp.context["posts"][0].slug, "max-chien-adorable")

        # Test AJAX on category page
        resp_ajax = self.client.get("/categorie/chiens/?q=adorable", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp_ajax.status_code, 200)
        self.assertTemplateUsed(resp_ajax, "includes/_post_grid.html")
        self.assertContains(resp_ajax, "Max")

    def test_category_alias_prefix(self):
        Category.objects.get_or_create(name="Chiens", slug="chiens")
        resp = self.client.get("/categorie/les-chiens/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["filters"]["species"], "chien")

    def test_contact_form_with_categories(self):
        from contact.models import ContactMessage
        resp = self.client.post("/contact/", {
            "name": "Marie Dupont",
            "email": "marie@example.com",
            "phone": "0601020304",
            "category": "adoption",
            "animal_name": "Max",
            "subject": "Candidature pour Max",
            "message": "Bonjour, je souhaite adopter Max !",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ContactMessage.objects.filter(email="marie@example.com", category="adoption").exists())

