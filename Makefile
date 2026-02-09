.PHONY: build up down logs migrate shell import-wp createsuperuser

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

shell:
	docker compose exec web python manage.py shell

createsuperuser:
	docker compose exec web python manage.py createsuperuser

# Usage: make import-wp SQL=path/to/dump.sql
import-wp:
	docker compose exec web python manage.py import_wordpress /app/$(SQL)

collectstatic:
	docker compose exec web python manage.py collectstatic --noinput
