---
name: moka-docker-persistence
description: >-
  Règle et standard Moka Studio pour la persistance Docker.
  Interdit l'utilisation de volumes nommés Docker et impose la persistance exclusive
  sur le système de fichiers local du serveur via des montages liés (bind mounts).
---

# Moka Studio - Règle de Persistance Docker

> [!IMPORTANT]
> **RÈGLE FONDAMENTALE MOKA STUDIO :**
> **Ne JAMAIS utiliser de volumes nommés ou anonymes Docker** (`volumes: postgres_data:`).
> Toutes les données, bases de données, médias et fichiers statiques doivent être **strictement persistés en local sur le système de fichiers du serveur** via des montages relatifs / bind mounts (`./data/...`, `./media/...`, etc.).

---

## 🎯 Objectifs & Avantages

1. **Sauvegardes et Backups Simples** : Accès direct aux fichiers de la base de données et aux uploads sans dépendre de l'arborescence interne Docker (`/var/lib/docker/volumes/...`).
2. **Transparence & Migration Immédiate** : Déplacement ou clonage du projet avec toutes ses données par simple copie de dossier (`rsync`, `tar`, `git` + dossier de données).
3. **Visibilité & Inspection** : Contrôle immédiat des logs, médias et dumps directement depuis l'explorateur ou le terminal du serveur.

---

## 🛠 Configuration Standard `docker-compose.yml`

### 1. Base de Données (PostgreSQL ou MySQL/MariaDB)

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      # PERSISTANCE LOCALE OBLIGATOIRE
      - ./data/postgres:/var/lib/postgresql/data
    env_file:
      - .env
```

### 2. Fichiers Médias & Statiques (Django / CMS)

```yaml
services:
  web:
    build: .
    volumes:
      - .:/app
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media

  nginx:
    image: nginx:1.27-alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
```

### 3. Section `volumes:` Interdite

Ne jamais ajouter de bloc `volumes:` en bas du fichier `docker-compose.yml` pour déclarer des volumes gérés par le démon Docker.

---

## 🔒 Configuration `.gitignore`

Les dossiers contenant les données locales volumineuses ou binaires doivent être ignorés dans Git :

```gitignore
# Données locales Docker (Persistance serveur)
data/
data/postgres/
data/mysql/

# Médias et fichiers collectés
media/uploads/
staticfiles/
```
