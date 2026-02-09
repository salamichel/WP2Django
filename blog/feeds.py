from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.html import strip_tags

from blog.models import Post


class LatestPostsFeed(Feed):
    title = "Derniers articles"
    link = "/"
    description = "Les derniers articles publiés"

    def items(self):
        return Post.objects.filter(status="published")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.excerpt:
            return item.excerpt
        return strip_tags(item.content)[:300]

    def item_pubdate(self, item):
        return item.published_at
