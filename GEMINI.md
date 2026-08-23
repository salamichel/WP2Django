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
- `AnimalDataExtractor` : Extraction automatique des fiches animaux depuis les métadonnées WP, avec analyse narrative en langage naturel pour les ententes (`ok_dogs`, `ok_cats`, `ok_children`) et exclusion stricte du statut/tag Urgence si l'animal est adopté ou décédé.
- `image_optimizer.py` : Optimisation & redimensionnement automatique des photos WP (max 1600px, EXIF orientation). Support in-place et tolérance aux images tronquées (`LOAD_TRUNCATED_IMAGES = True`, `MAX_IMAGE_PIXELS = None`).

### 3. Application `contact`
- Formulaire de contact enregistré en base et connecté à l'API Brevo.

## ⚙️ Configuration Technique & Conventions
- **Règle Persistance Docker (Moka Studio)** : Ne JAMAIS utiliser de volumes nommés Docker. Persister toutes les données en local sur le serveur (`./data/postgres` pour PostgreSQL, `./media` pour les uploads, `./staticfiles` pour les assets compilés).
- **Stack** : Django 5.2, PostgreSQL 16 (ou SQLite pour les tests), Docker, Nginx, CKEditor 5.
- **Cache Statique Nginx & Cache-Busting** : Ne JAMAIS utiliser `immutable` sur des fichiers statiques sans hash de contenu. Utiliser `must-revalidate` dans Nginx et toujours ajouter un paramètre de version (`?v=X.Y`) dans `base.html` sur `style.css` et `main.js` pour garantir un affichage propre dès la première visite.
- **Variables d'environnement** : Voir `.env.example`.
- **Slugs** : Générés automatiquement via `slugify` dans les méthodes `save()`.
- **Sécurité Admin** : Préférer `format_html()` pour le rendu HTML sécurisé dans `admin.py`.

### 4. Standards UI/UX, Éditeur WYSIWYG & Intégration Front-End
- **Éditeur WYSIWYG (CKEditor 5)** : Toujours activer `htmlSupport` (GHS) dans `settings.py` pour préserver les attributs `style="..."` et classes custom. Déclarer dans `admin_custom.css` un miroir complet du CSS front-end pour `.ck-content` (polices `Playfair Display`/`Inter`, boutons `.btn`, grilles de cartes et alertes).
- **Règle d'Urgence Animaux** : Priorité absolue `Décédé > Adopté > Réservé > Urgence > Adoptable`. Un animal adopté ou décédé ne doit jamais recevoir `is_emergency = True` ni le tag `Urgence`.
- **Menus déroulants & Mega Menus** : Toujours inclure un pont invisible (`::before`) et un délai de grâce (150-200ms) pour éviter les fermetures prématurées au survol.
- **Champs de recherche** : Toujours neutraliser les pictogrammes natifs WebKit (`::-webkit-search-decoration`, etc.) pour éviter la superposition avec les icônes SVG custom.
- **Formulaires & Selects Admin** : Assurer une largeur minimale (`min-width: 200px`), un dégagement pour la flèche (`padding-right: 32px`) et le wrapping du texte dans les options et widgets Select2 pour éviter toute troncature.
- **Formulaires Mobiles (iOS Safari)** : Toujours fixer `font-size: 16px` et `min-height: 48px` sur les champs de saisie pour empêcher le zoom automatique indésirable lors du tap sur mobile.
- **Filtres Multi-Critères Mobiles** : Sur écran mobile (<= 680px), empiler la recherche textuelle en 100%, répartir les onglets espèces en grille `repeat(N, 1fr)` pour éviter tout overflow horizontal, et organiser les tags de compatibilité en grille 2x2 uniforme avec le bouton d'effacement pleine largeur en-dessous.
- **Fiches Animaux & Galerie Photos** : Toujours centrer la photo de présentation principale (`max-height: 520px`, `border-radius: 24px`) et l'associer à la galerie photo au sein de la même visionneuse plein écran GLightbox avec support du swipe tactile. Structurer la fiche en 4 blocs : Grille 2x2 des caractéristiques clés, boîte pastel des garanties sanitaires, badges tricolores d'ententes (Chiens/Chats/Enfants), et grand bouton CTA pleine largeur (50-54px).
