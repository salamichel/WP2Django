from django.conf import settings

from blog.models import Menu, Category, SiteSettings


def site_context(request):
    menus = {}
    for menu in Menu.objects.prefetch_related("items__children").all():
        menus[menu.slug] = menu

    site_settings = SiteSettings.get_solo()

    return {
        "site_name": site_settings.association_name or settings.SITE_NAME,
        "site_url": settings.SITE_URL,
        "site_settings": site_settings,
        "menus": menus,
        "all_categories": Category.objects.filter(parent__isnull=True),
    }

