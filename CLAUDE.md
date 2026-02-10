# CLAUDE.md - WP2Django Project Guide

## Project Overview
WordPress-to-Django migration tool and blog for an **animal protection association** (dogs, cats, rodents).
Django 5.2 + PostgreSQL 16 + Nginx, all running in Docker Compose.

## Architecture
- **3 Django apps**: `blog` (core models/views), `contact` (Brevo email integration), `wordpress_import` (SQL dump parser)
- **Frontend**: Vanilla CSS/JS, warm orange palette (#e8734a), Playfair Display headings, responsive with left sidebar
- **Admin**: Custom themed admin with dashboard cards, stat counters, and quick actions

## Key Commands

```bash
# Run tests (uses SQLite automatically, no PostgreSQL needed)
python manage.py test --verbosity=1

# Run a specific test class
python manage.py test blog.tests.PostViewTest

# Generate migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Import WordPress dump
python manage.py import_wordpress dump.sql

# Docker
docker compose up -d
docker compose exec web python manage.py migrate
```

## Project Structure

```
config/            # Django project config (settings, urls, wsgi)
blog/              # Core app: Post, Page, Category, Tag, Comment, Menu, Media, Redirect
  admin.py         # Custom admin with status badges, thumbnails, autocomplete
  models.py        # All blog models with French verbose_names
  views.py         # Views with select_related/prefetch_related optimizations
  context_processors.py  # Provides menus dict and all_categories to all templates
  templatetags/    # Dashboard stats tags for admin
contact/           # Contact form app with Brevo API email sending
wordpress_import/  # SQL parser + 7 importers (User, Taxonomy, Post, Comment, Menu, Plugin, Redirect)
  sql_parser.py    # Handles WP table prefix auto-detection, escaped strings, multi-row INSERTs
  importers.py     # Maps WP data to Django models
  content_processor.py  # Rewrites HTML content (URLs, shortcodes)
templates/         # Django templates
  base.html        # Master layout with header, sidebar, footer
  includes/sidebar.html  # Left sidebar with 2 dynamic menus (slugs: adoptions, plus_infos)
  admin/           # Custom admin templates (base_site, login, index)
static/
  css/style.css         # Full frontend theme (~1500 lines)
  css/admin_custom.css  # Admin theme override
  js/main.js            # Animations, mobile menu, sidebar toggle
```

## Important Conventions

- **Language**: French UI (templates, admin labels, verbose_names). Code and comments in English.
- **Menus**: Dynamic via Menu model. Slugs: `main` (header nav), `adoptions` (sidebar), `plus_infos` (sidebar). Fallback static content when menus not configured.
- **Tests**: Always run `python manage.py test` before committing. Tests use SQLite (settings.py detects `"test" in sys.argv`).
- **Migrations**: Always run `python manage.py makemigrations` after model changes. Without migration files, DB queries fail with "relation does not exist".
- **Templates**: Pages with sidebar use `{% block content %}`. Full-width pages (home, contact) override `{% block page_content %}` instead.
- **Admin display**: Use `format_html()` for safe HTML in list_display methods. Never use `mark_safe()` with user data.

## Environment Variables (via .env)

```
SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL
BREVO_API_KEY, BREVO_SENDER_EMAIL, CONTACT_RECIPIENT_EMAIL
SITE_NAME, SITE_URL
```

## Known Improvement Areas

### High Priority
- Fix contact email logic (`and` → `or` in contact/views.py)
- Add N+1 query fixes in admin (annotate post_count)
- Cache context processor menu queries
- Add robots.txt and sitemap.xml

### Medium Priority
- SEO: canonical tags, Open Graph meta, JSON-LD structured data
- Performance: Redis caching, PostgreSQL full-text search
- Security: Nginx HSTS/CSP headers, bleach for content sanitization
- Tests: Expand contact app tests, add admin UI tests

### Low Priority
- Features: comment form, related posts, breadcrumbs, newsletter, dark mode
- Frontend: CSS minification, WebP images, favicon
