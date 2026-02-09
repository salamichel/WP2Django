from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone

from blog.models import Post, Page, Category, Tag, Comment, Menu, MenuItem, Redirect


class CategoryModelTest(TestCase):
    def test_auto_slug(self):
        cat = Category.objects.create(name="Test Category")
        self.assertEqual(cat.slug, "test-category")

    def test_str(self):
        cat = Category.objects.create(name="Tech", slug="tech")
        self.assertEqual(str(cat), "Tech")

    def test_get_absolute_url(self):
        cat = Category.objects.create(name="Tech", slug="tech")
        self.assertEqual(cat.get_absolute_url(), "/categorie/tech/")

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
