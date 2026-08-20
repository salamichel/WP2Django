# Rêves de Chiens - Guide pour l'IA (Gemini / Antigravity)

Ce fichier fournit le contexte complet et les règles pour les assistants IA travaillant sur le projet **Rêves de Chiens**.

## 🎯 Objectif du Projet
Site CMS et plateforme de gestion pour l'association **Rêves de Chiens** (refuge animalier pour chiens, chats et rongeurs). Le projet inclut un outil de migration permettant d'importer directement un site WordPress à partir d'un dump SQL.

## 🛠 Commandes Essentielles (Docker & Local)
- `make build` : Construit les conteneurs Docker.
- `make up` : Lance le projet en arrière-plan.
- `docker compose exec web python manage.py test` : Exécute toute la suite de tests (65+ tests) dans le conteneur.
- `python manage.py test` : Exécute les tests en local (bascule automatiquement sur SQLite).
- `make migrate` ou `python manage.py migrate` : Applique les migrations Django.
- `make import-wp SQL=chemin/vers/dump.sql` ou `python manage.py import_wordpress dump.sql` : Importe les données WordPress.
- `make createsuperuser` ou `docker compose exec web python manage.py createsuperuser` : Initialise le compte administrateur (invite interactive pour nom d'utilisateur, email, mot de passe).
- `docker compose exec -e DJANGO_SUPERUSER_PASSWORD=motdepasse web python manage.py createsuperuser --noinput --username admin --email contact@revesdechiens.fr` : Initialisation automatique sans prompt.

## 🏗 Structure du Projet

### 1. Application `blog` (CMS)
- **Modèles de base** : `Post`, `Page`, `Category`, `Tag`, `Media`.
- **Profils Animaux** : Intégrés au modèle `Post` via les champs `species`, `breed`, `animal_name`, `is_adoptable`.
- **Navigation** : Modèles `Menu` et `MenuItem` avec support de clés étrangères vers le contenu. Slugs principaux : `main` (en-tête), `adoptions` (barre latérale), `plus_infos` (barre latérale), `footer` (pied de page).
- **Redirections** : Modèle `Redirect` et middleware `WPRedirectMiddleware` pour préserver les anciennes URLs WordPress (`/index.php?p=123`, etc.).

### 2. Application `wordpress_import` (Moteur de Migration)
- `sql_parser.py` : Analyseur SQL sans dépendance MySQL.
- `importers.py` : Conversion des données WP en modèles Django.
- `content_processor.py` : Nettoyage HTML, réécriture d'URLs d'images, extraction de galeries.
- `AnimalDataExtractor` : Extraction automatique des fiches animaux depuis les métadonnées WP.

### 3. Application `contact`
- Formulaire de contact enregistré en base et connecté à l'API Brevo.

## ⚙️ Configuration Technique & Conventions
- **Règle Persistance Docker (Moka Studio)** : Ne JAMAIS utiliser de volumes nommés Docker. Persister toutes les données en local sur le serveur (`./data/postgres` pour PostgreSQL, `./media` pour les uploads, `./staticfiles` pour les assets compilés).
- **Stack** : Django 5.2, PostgreSQL 16 (ou SQLite pour les tests), Docker, Nginx, CKEditor 5.
- **Variables d'environnement** : Voir `.env.example`.
- **Slugs** : Générés automatiquement via `slugify` dans les méthodes `save()`.
- **Sécurité Admin** : Préférer `format_html()` pour le rendu HTML sécurisé dans `admin.py`.

### 4. Standards UI/UX & Intégration Front-End
- **Menus déroulants & Mega Menus** : Toujours inclure un pont invisible (`::before`) et un délai de grâce (150-200ms) pour éviter les fermetures prématurées au survol.
- **Champs de recherche** : Toujours neutraliser les pictogrammes natifs WebKit (`::-webkit-search-decoration`, etc.) pour éviter la superposition avec les icônes SVG custom.
- **Formulaires & Selects Admin** : Assurer une largeur minimale (`min-width: 200px`), un dégagement pour la flèche (`padding-right: 32px`) et le wrapping du texte dans les options et widgets Select2 pour éviter toute troncature.
