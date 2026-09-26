from django.urls import reverse_lazy


def badge_adoptable_animals(request):
    """Returns badge count of currently adoptable animals."""
    from blog.models import Animal
    count = Animal.objects.filter(adoption_status="adoptable").count()
    return str(count) if count > 0 else ""


def badge_unread_messages(request):
    """Returns badge count of unread contact messages."""
    from contact.models import ContactMessage
    count = ContactMessage.objects.filter(is_read=False).count()
    return str(count) if count > 0 else ""


def badge_pending_comments(request):
    """Returns badge count of pending comments."""
    from blog.models import Comment
    count = Comment.objects.filter(status="pending").count()
    return str(count) if count > 0 else ""


def dashboard_callback(request, context):
    """Populates dashboard context with shelter metrics and recent items for Unfold."""
    from blog.models import Animal, Article, Page, Comment, Media, AdoptionTariff
    from contact.models import ContactMessage

    context.update({
        "animals_count": Animal.objects.filter(adoption_status="adoptable").count(),
        "animals_urgent": Animal.objects.filter(is_emergency=True).exclude(adoption_status="adopte").count(),
        "animals_adopted": Animal.objects.filter(adoption_status="adopte").count(),
        "messages_unread": ContactMessage.objects.filter(is_read=False).count(),
        "messages_total": ContactMessage.objects.count(),
        "pages_count": Page.objects.filter(status="published").count(),
        "articles_count": Article.objects.filter(status="published").count(),
        "media_count": Media.objects.count(),
        "tariffs_count": AdoptionTariff.objects.filter(is_active=True).count(),
        "recent_animals": Animal.objects.select_related("featured_image").prefetch_related("gallery_images__media").order_by("-created_at")[:6],
        "recent_messages": ContactMessage.objects.order_by("-created_at")[:6],
        "recent_articles": Article.objects.select_related("author").order_by("-created_at")[:5],
    })
    return context
