# Rêves de Chiens

Plateforme web et CMS pour l'association **Rêves de Chiens** (refuge et protection animale). Inclut un moteur autonome de migration depuis WordPress.

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

### 4. Initialiser le compte administrateur (Superuser)

**Option A - Mode interactif (Recommandé) :**
```bash
# Dans Docker
docker compose exec web python manage.py createsuperuser
# Ou avec le Makefile
make createsuperuser
# En local
python manage.py createsuperuser
```
Vous serez invité à saisir :
- **Username** : votre identifiant (ex: `admin`)
- **Email** : votre adresse email (ex: `contact@revesdechiens.fr`)
- **Password** : votre mot de passe (saisie masquée, min. 8 caractères)

**Option B - Mode automatique (non-interactif) :**
```bash
docker compose exec -e DJANGO_SUPERUSER_PASSWORD=VotreMotDePasseSecurise web python manage.py createsuperuser --noinput --username admin --email contact@revesdechiens.fr
```

### 5. Accéder au site & à l'administration

- **Site public** : http://localhost:8080/ (ou http://localhost/)
- **Administration Django** : http://localhost:8080/admin/ (ou http://localhost/admin/)

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
make up             # Démarrer les conteneurs
make down           # Arrêter les conteneurs
make logs           # Voir les logs en direct
make migrate        # Appliquer les migrations de base de données
make shell          # Ouvrir le shell interactif Django
make createsuperuser# Initialiser le compte administrateur
make seed           # Ensemencer les pages CMS et menus (seed_rdc_pages)
make import-wp SQL=dump.sql # Importer un dump SQL WordPress
```

## Base de données & Persistance (Standard Moka Studio)

Conformément aux standards Moka Studio, la persistance est exclusivement assurée par des **montages liés locaux (bind mounts)** sans aucun volume nommé Docker :
- **Données PostgreSQL** : `./data/postgres/`
- **Fichiers Médias (Uploads)** : `./media/`
- **Fichiers Statiques compilés** : `./staticfiles/`

### Initialisation & Ensemencement (Seed)
Pour initialiser ou restaurer la structure complète des pages CMS (Conditions d'adoption, Familles d'accueil, Tarifs, Mentions légales...) et les menus dynamiques (Header, Sidebar, Footer) :
```bash
docker compose exec web python manage.py seed_rdc_pages
```

---

## Schéma de Base de Données & Modèles

### 1. Modèle `blog.Post` (Articles & Profils Animaux)
- **Champs de base** : `title`, `slug`, `content` (CKEditor 5), `excerpt`, `status` (`draft`, `published`, `private`, `trash`), `author`, `featured_image` (FK `Media`), `published_at`, `created_at`, `updated_at`.
- **Taxonomies** : ManyToMany vers `Category` et `Tag`.
- **Profils Animaux (Champs dédiés)** :
  - `animal_name` : Nom de l'animal.
  - `species` : Espèce (`chien`, `chat`, `rongeur`).
  - `breed` : Race ou croisement.
  - `sex` : Sexe (`male`, `femelle`).
  - `birth_date` : Date de naissance (calcul automatique de l'âge).
  - `weight_kg` : Poids en kg.
  - `identification` : Numéro d'identification électronique (ICAD).
  - `is_vaccinated`, `is_sterilized` : Statut sanitaire.
  - `is_adoptable` : Indicateur de mise à l'adoption.
  - `adoption_status` : Statut (`adoptable`, `reserve`, `recherche_fa`, `adopte`).
  - `ok_dogs`, `ok_cats`, `ok_children` : Ententes et compatibilités (`oui`, `non`, `inconnu`).
  - `housing_requirement` : Exigences d'habitat (`indifferent`, `maison`, `appartement`).
  - `is_emergency` : Marqueur d'urgence vitale ou recherche urgente de Famille d'Accueil.

### 2. Modèle `blog.PostGalleryImage` (Galeries Photos)
- `post` : Clé étrangère vers `Post` (Cascade).
- `media` : Clé étrangère vers `Media` (Cascade).
- `position` : Ordre d'affichage dans la galerie Lightbox.

### 3. Modèle `blog.Page` (Pages CMS Institutionnelles)
- `title`, `slug`, `content` (CKEditor 5), `status`, `author`, `parent` (arborescence hiérarchique), `template`, `menu_order`.
- Champs SEO : `seo_title`, `seo_description`.
- `wp_post_id` : Référence de l'ID WordPress source lors de la migration.

### 4. Modèles `blog.Menu` & `blog.MenuItem` (Navigation Dynamique)
- `Menu` : Identifiant par slug (`main`, `adoptions`, `plus_infos`, `footer`).
- `MenuItem` : Liens hiérarchiques avec support de clés étrangères polymorphiques vers `linked_page`, `linked_post`, `linked_category` ou `url` personnalisée.

### 5. Modèles `blog.Category` & `blog.Tag` (Taxonomies)
- Catégories animales et thématiques avec résolution flexible des slugs et support des alias canoniques (`chiens`, `chats`, `rongeurs`, `urgences`, et alias `les-chiens`, `les-chats`...).

### 6. Modèle `blog.Redirect` (Redirections SEO WordPress)
- `old_path`, `new_url`, `is_permanent` (301/302). Géré via le middleware `WPRedirectMiddleware` pour préserver 100% de l'historique d'indexation Google (`/?p=123`, etc.).

---

## Ce qui est importé depuis WordPress

| WordPress | Django / PostgreSQL |
|---|---|
| `wp_users` | `auth.User` |
| `wp_posts` (post) | `blog.Post` (+ extraction automatique des profils animaux) |
| `wp_posts` (page) | `blog.Page` |
| `wp_posts` (attachment) | `blog.Media` + `blog.PostGalleryImage` |
| `wp_terms` + `wp_term_taxonomy` (category) | `blog.Category` |
| `wp_terms` + `wp_term_taxonomy` (post_tag) | `blog.Tag` |
| `wp_comments` | `blog.Comment` (avec hiérarchie parent/enfants) |
| `wp_terms` (nav_menu) | `blog.Menu` + `blog.MenuItem` |
| `wp_postmeta` (Yoast / RankMath / ACF) | `seo_title`, `seo_description`, profils animaux |
| Tables plugins tierces | `blog.PluginData` (structure JSONB) |
| Permaliens & anciennes URLs | `blog.Redirect` |
