from django.conf import settings

from blog.models import Menu, Category


def site_context(request):
    menus = {}
    for menu in Menu.objects.prefetch_related("items__children").all():
        menus[menu.slug] = menu

    return {
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
        "menus": menus,
        "all_categories": Category.objects.filter(parent__isnull=True),
    }
