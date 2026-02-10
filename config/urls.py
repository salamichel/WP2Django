from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from blog.sitemaps import PostSitemap, PageSitemap, CategorySitemap
from blog.feeds import LatestPostsFeed

# Admin site customization
admin.site.site_header = settings.SITE_NAME + " — Administration"
admin.site.site_title = settings.SITE_NAME + " Admin"
admin.site.index_title = "Tableau de bord"

sitemaps = {
    "posts": PostSitemap,
    "pages": PageSitemap,
    "categories": CategorySitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("feed/", LatestPostsFeed(), name="rss-feed"),
    path("contact/", include("contact.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", include("blog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
