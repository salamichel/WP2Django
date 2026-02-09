# WP2Django

Outil autonome de migration WordPress vers Django. Analyse un dump SQL WordPress, détecte automatiquement les tables (core + plugins), et génère un site Django complet.

## Stack technique

- **Backend** : Django 5.2 + Gunicorn
- **Frontend** : Templates Django + CSS vanilla + JS vanilla
- **Base de données** : PostgreSQL 16 (Docker)
- **Reverse proxy** : Nginx
- **Médias** : Pillow
- **Email** : Brevo API v3
- **Conteneurisation** : Docker Compose

## Démarrage rapide

### 1. Configuration

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

### 2. Lancer les services

```bash
docker compose up -d --build
```

### 3. Importer un site WordPress

```bash
# Analyser le dump sans importer (dry-run)
docker compose exec web python manage.py import_wordpress /app/dump.sql --dry-run

# Importer
docker compose exec web python manage.py import_wordpress /app/dump.sql

# Avec les médias
docker compose exec web python manage.py import_wordpress /app/dump.sql --media-dir /app/wp-content/uploads
```

### 4. Créer un super utilisateur

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Accéder au site

- **Site** : http://localhost
- **Admin** : http://localhost/admin/

## Commande d'import

```
python manage.py import_wordpress <fichier.sql> [options]
```

**Options :**
- `--dry-run` : analyse le dump sans importer
- `--skip-plugins` : ignore les tables de plugins
- `--media-dir <path>` : chemin vers le dossier wp-content/uploads

**L'importeur détecte automatiquement :**
- Le préfixe des tables (wp_, wp2_, etc.)
- Les tables core WordPress (posts, pages, users, comments, menus, taxonomies)
- Les plugins installés (WooCommerce, Yoast SEO, ACF, Contact Form 7, WPML, etc.)
- Les données SEO (Yoast, Rank Math)
- La structure des permaliens pour générer les redirections

## Structure du projet

```
WP2Django/
├── config/              # Configuration Django (settings, urls, wsgi)
├── blog/                # App principale (posts, pages, catégories, tags, commentaires, menus)
├── contact/             # Formulaire de contact (Brevo)
├── wordpress_import/    # Outil d'import WordPress
│   ├── sql_parser.py        # Parser SQL autonome
│   ├── importers.py         # Importeurs par entité
│   ├── content_processor.py # Réécriture du contenu HTML
│   └── management/commands/ # Commande Django
├── templates/           # Templates HTML
├── static/              # CSS + JS
├── nginx/               # Configuration Nginx
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

## Makefile

```bash
make build          # Build Docker
make up             # Démarrer
make down           # Arrêter
make logs           # Voir les logs
make migrate        # Lancer les migrations
make shell          # Shell Django
make createsuperuser
make import-wp SQL=dump.sql
```

## Ce qui est importé

| WordPress | Django |
|-----------|--------|
| wp_users | auth.User |
| wp_posts (post) | blog.Post |
| wp_posts (page) | blog.Page |
| wp_posts (attachment) | blog.Media |
| wp_terms + wp_term_taxonomy (category) | blog.Category |
| wp_terms + wp_term_taxonomy (post_tag) | blog.Tag |
| wp_comments | blog.Comment |
| wp_terms (nav_menu) | blog.Menu + blog.MenuItem |
| wp_postmeta (SEO) | Champs seo_title / seo_description |
| Tables plugins | blog.PluginData (JSON) |
| Permaliens | blog.Redirect |
