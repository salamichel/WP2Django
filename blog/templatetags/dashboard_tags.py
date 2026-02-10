from django import template

from blog.models import Post, Page, Category, Tag, Comment, Media, Menu, Redirect
from contact.models import ContactMessage

register = template.Library()


@register.simple_tag
def dashboard_stats():
    return {
        "posts": Post.objects.filter(status="published").count(),
        "posts_draft": Post.objects.filter(status="draft").count(),
        "pages": Page.objects.filter(status="published").count(),
        "comments": Comment.objects.filter(status="approved").count(),
        "comments_pending": Comment.objects.filter(status="pending").count(),
        "messages": ContactMessage.objects.count(),
        "messages_unread": ContactMessage.objects.filter(is_read=False).count(),
        "categories": Category.objects.count(),
        "tags": Tag.objects.count(),
        "media": Media.objects.count(),
        "menus": Menu.objects.count(),
        "redirects": Redirect.objects.count(),
    }


@register.simple_tag
def recent_posts():
    return Post.objects.select_related("author").order_by("-created_at")[:5]


@register.simple_tag
def recent_comments():
    return Comment.objects.select_related("post").order_by("-created_at")[:5]


@register.simple_tag
def recent_messages():
    return ContactMessage.objects.order_by("-created_at")[:5]
