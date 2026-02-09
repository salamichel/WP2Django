from django.contrib.sitemaps import Sitemap
from blog.models import Post, Page, Category


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Page.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.all()
