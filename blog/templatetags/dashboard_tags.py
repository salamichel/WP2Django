from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from blog.models import (
    Post, Animal, Article, Page, Category, Tag, Comment, Media, Menu, Redirect, AdoptionTariff
)
from contact.models import ContactMessage

register = template.Library()


@register.filter(name="render_cms_content")
def render_cms_content(content):
    if not content:
        return ""
    if "<!-- ADOPTION_TARIFFS_TABLE_DYNAMIC -->" in content:
        tariffs = AdoptionTariff.objects.filter(is_active=True).order_by("species", "order", "amount")
        rendered_tariffs = render_to_string("includes/_adoption_tariffs.html", {
            "dog_tariffs": [t for t in tariffs if t.species == "chien"],
            "cat_tariffs": [t for t in tariffs if t.species == "chat"],
            "other_tariffs": [t for t in tariffs if t.species not in ("chien", "chat")],
        })
        content = content.replace("<!-- ADOPTION_TARIFFS_TABLE_DYNAMIC -->", rendered_tariffs)
    return mark_safe(content)



@register.simple_tag
def dashboard_stats():
    return {
        "animals": Animal.objects.filter(adoption_status="adoptable").count(),
        "animals_urgent": Animal.objects.filter(is_emergency=True).exclude(adoption_status="adopte").count(),
        "animals_adopted": Animal.objects.filter(adoption_status="adopte").count(),
        "articles": Article.objects.filter(status="published").count(),
        "articles_draft": Article.objects.filter(status="draft").count(),
        "pages": Page.objects.filter(status="published").count(),
        "comments": Comment.objects.filter(status="approved").count(),
        "comments_pending": Comment.objects.filter(status="pending").count(),
        "messages": ContactMessage.objects.count(),
        "messages_unread": ContactMessage.objects.filter(is_read=False).count(),
        "categories": Category.objects.count(),
        "tags": Tag.objects.count(),
        "media": Media.objects.count(),
        "menus": Menu.objects.count(),
        "tariffs": AdoptionTariff.objects.filter(is_active=True).count(),
        "redirects": Redirect.objects.count(),
        "posts": Post.objects.filter(status="published").count(),
        "posts_draft": Post.objects.filter(status="draft").count(),
    }


@register.simple_tag
def recent_animals():
    return Animal.objects.select_related("featured_image").prefetch_related("gallery_images__media").order_by("-created_at")[:6]


@register.simple_tag
def recent_articles():
    return Article.objects.select_related("author").order_by("-created_at")[:5]


@register.simple_tag
def recent_posts():
    return Post.objects.select_related("author").order_by("-created_at")[:5]


@register.simple_tag
def recent_comments():
    return Comment.objects.select_related("post").order_by("-created_at")[:5]


@register.simple_tag
def recent_messages():
    return ContactMessage.objects.order_by("-created_at")[:6]


@register.inclusion_tag("includes/_adoption_tariffs.html")
def render_adoption_tariffs():
    from blog.models import AdoptionTariff
    tariffs = AdoptionTariff.objects.filter(is_active=True).order_by("species", "order", "amount")
    dog_tariffs = [t for t in tariffs if t.species == "chien"]
    cat_tariffs = [t for t in tariffs if t.species == "chat"]
    other_tariffs = [t for t in tariffs if t.species not in ("chien", "chat")]
    return {
        "dog_tariffs": dog_tariffs,
        "cat_tariffs": cat_tariffs,
        "other_tariffs": other_tariffs,
    }

