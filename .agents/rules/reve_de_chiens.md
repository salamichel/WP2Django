# Rêves de Chiens - Project Rules & Guidelines

## 🎯 Objectif du Projet
Framework CMS et site web pour l'association **Rêves de Chiens** (refuge et protection animale - chiens, chats, rongeurs). Inclut le moteur de migration et d'importation de données depuis WordPress SQL.

## 🛠 Commandes Essentielles (Docker & Local)
- **Tests (Docker)** : `docker compose exec web python manage.py test`
- **Tests (Local)** : `python manage.py test` (bascule automatique sur SQLite)
- **Migrations** : `python manage.py makemigrations` puis `python manage.py migrate`
- **Initialiser le compte admin** :
  - *Interactif (Docker)* : `docker compose exec web python manage.py createsuperuser`
  - *Interactif (Local)* : `python manage.py createsuperuser`
  - *Automatisé (non-interactif)* : `docker compose exec -e DJANGO_SUPERUSER_PASSWORD=adminpwd web python manage.py createsuperuser --noinput --username admin --email contact@revesdechiens.fr`
- **Import WordPress** : `python manage.py import_wordpress dump.sql`
- **Docker Compose** : `docker compose up -d`
- **Accès Admin** : `http://localhost:8080/admin/` (ou `http://localhost/admin/`)

## 🏗 Structure du Projet

### 1. Application `blog` (CMS)
- **Modèles de base** : `Post`, `Page`, `Category`, `Tag`, `Media`.
- **Profils Animaux** : Intégrés au modèle `Post`. Champs : `species`, `breed`, `animal_name`, `is_adoptable`.
- **Navigation** : Modèles `Menu` et `MenuItem` avec support des clés étrangères vers le contenu.
- **Redirections** : Modèle `Redirect` et `WPRedirectMiddleware` pour gérer les anciennes URLs WordPress (`/index.php?p=123`, etc.).

### 2. Application `wordpress_import` (Moteur de Migration)
- `sql_parser.py` : Analyseur SQL personnalisé (évite de nécessiter une base MySQL).
- `importers.py` : Logique de conversion des données WP -> Django.
- `content_processor.py` : Nettoyage HTML, réécriture d'URLs d'images, et extraction de galeries.
- `AnimalDataExtractor` : Extrait les infos animales du texte brut ou des métadonnées WP.

### 3. Application `contact`
- Formulaire de contact avec intégration API Brevo.

## ⚙️ Configuration Technique & Conventions
- **Règle Persistance Docker (Moka Studio)** : Ne JAMAIS utiliser de volumes nommés Docker. Toutes les données (PostgreSQL dans `./data/postgres`, médias dans `./media`, static dans `./staticfiles`) doivent être persistées en local sur le serveur via des bind mounts.
- **Stack** : Django 5, PostgreSQL (ou SQLite pour tests), Docker, Nginx, CKEditor 5.
- **Interface & Langue** : Interface publique et admin en français. Code et commentaires en anglais.
- **Slugs** : Générés automatiquement via `slugify` dans les méthodes `save()`.
- **Récupération des Médias** : Images stockées dans `media/uploads/%Y/%m/`.
- **Sécurité** : Utiliser `format_html()` pour le HTML affiché dans l'admin Django.
