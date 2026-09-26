import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")

DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,web").split(",") if h.strip()] + ["testserver"]

# CSRF trusted origins (required when behind reverse proxy with HTTPS)
_csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(",") if o.strip()]

from django.urls import reverse_lazy

INSTALLED_APPS = [
    # Unfold Modern Tailwind Admin Theme (must precede django.contrib.admin)
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Third-party
    "django_ckeditor_5",
    # Local apps
    "blog.apps.BlogConfig",
    "contact.apps.ContactConfig",
    "wordpress_import.apps.WordpressImportConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "blog.middleware.WPRedirectMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blog.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if os.getenv("USE_SQLITE", "0") == "1" or "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "wp2django"),
            "USER": os.getenv("POSTGRES_USER", "wp2django"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CKEditor 5
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|",
            "bold", "italic", "underline", "strikethrough", "|",
            "link", "blockQuote", "code", "codeBlock", "|",
            "bulletedList", "numberedList", "todoList", "|",
            "insertImage", "mediaEmbed", "sourceEditing", "|",
            "undo", "redo",
        ],
        "htmlSupport": {
            "allow": [
                {
                    "name": "/.*/",
                    "attributes": True,
                    "classes": True,
                    "styles": True,
                }
            ]
        },
    },
}
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PATH = "ckeditor/"

# Brevo (email)
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "contact@revesdechiens.fr")
CONTACT_RECIPIENT_EMAIL = os.getenv("CONTACT_RECIPIENT_EMAIL", "contact@revesdechiens.fr")

# Site settings
SITE_NAME = os.getenv("SITE_NAME", "Rêves de Chiens")
SITE_URL = os.getenv("SITE_URL", "http://localhost")

# Pagination
POSTS_PER_PAGE = 10

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Security (production)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "wordpress_import": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# ==============================================================================
# DJANGO UNFOLD MODERN ADMIN CONFIGURATION
# ==============================================================================

UNFOLD = {
    "SITE_TITLE": "Rêves de Chiens",
    "SITE_HEADER": "Rêves de Chiens",
    "SITE_SUBHEADER": "Refuge Solidaire & Protection Animale",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "/media/site/logo_reves_de_chiens.png",
        "dark": lambda request: "/media/site/logo_reves_de_chiens.png",
    },
    "SITE_LOGO": {
        "light": lambda request: "/media/site/logo_reves_de_chiens.png",
        "dark": lambda request: "/media/site/logo_reves_de_chiens.png",
    },
    "DASHBOARD_CALLBACK": "blog.admin_callbacks.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Refuge & Animaux",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Animaux à l'adoption",
                        "icon": "pets",
                        "link": reverse_lazy("admin:blog_animal_changelist"),
                        "badge": "blog.admin_callbacks.badge_adoptable_animals",
                    },
                    {
                        "title": "Tarifs d'adoption",
                        "icon": "payments",
                        "link": reverse_lazy("admin:blog_adoptiontariff_changelist"),
                    },
                ],
            },
            {
                "title": "Contenu & Communication",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Pages du site (CMS)",
                        "icon": "description",
                        "link": reverse_lazy("admin:blog_page_changelist"),
                    },
                    {
                        "title": "Articles de blog",
                        "icon": "newspaper",
                        "link": reverse_lazy("admin:blog_article_changelist"),
                    },
                    {
                        "title": "Médiathèque (Photos)",
                        "icon": "photo_library",
                        "link": reverse_lazy("admin:blog_media_changelist"),
                    },
                    {
                        "title": "Commentaires",
                        "icon": "chat",
                        "link": reverse_lazy("admin:blog_comment_changelist"),
                        "badge": "blog.admin_callbacks.badge_pending_comments",
                    },
                ],
            },
            {
                "title": "Navigation & Structure",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Menus de navigation",
                        "icon": "menu",
                        "link": reverse_lazy("admin:blog_menu_changelist"),
                    },
                    {
                        "title": "Catégories",
                        "icon": "category",
                        "link": reverse_lazy("admin:blog_category_changelist"),
                    },
                    {
                        "title": "Étiquettes (Tags)",
                        "icon": "label",
                        "link": reverse_lazy("admin:blog_tag_changelist"),
                    },
                ],
            },
            {
                "title": "Demandes & Contact",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Messages & Candidatures",
                        "icon": "mail",
                        "link": reverse_lazy("admin:contact_contactmessage_changelist"),
                        "badge": "blog.admin_callbacks.badge_unread_messages",
                    },
                ],
            },
            {
                "title": "Paramètres & Système",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Paramètres du Site & Logo",
                        "icon": "settings",
                        "link": reverse_lazy("admin:blog_sitesettings_changelist"),
                    },
                    {
                        "title": "Redirections d'URLs (SEO)",
                        "icon": "alt_route",
                        "link": reverse_lazy("admin:blog_redirect_changelist"),
                    },
                    {
                        "title": "Données d'import (WordPress)",
                        "icon": "archive",
                        "link": reverse_lazy("admin:blog_plugindata_changelist"),
                    },
                ],
            },
            {
                "title": "Utilisateurs & Accès",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Utilisateurs",
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Groupes & Rôles",
                        "icon": "badge",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}

