from django.apps import AppConfig


class WordpressImportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wordpress_import"
    verbose_name = "Import WordPress"
