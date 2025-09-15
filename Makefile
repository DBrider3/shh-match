.PHONY: up down logs sh-fe sh-be psql migrate clean restart status

# Docker Compose commands
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

restart:
	docker compose restart

status:
	docker compose ps

clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# Container shell access
sh-fe:
	docker exec -it km-frontend /bin/bash

sh-be:
	docker exec -it km-backend /bin/bash

# Container shell access without TTY (for CI/CD)
exec-fe:
	docker exec km-frontend sh -c

exec-be:
	docker exec km-backend sh -c

# Database related
psql:
	docker exec -it km-db psql -U app -d kakao_match

migrate:
	docker exec km-backend alembic upgrade head

migrate-create:
	docker exec km-backend alembic revision --autogenerate -m "$(msg)"

migrate-downgrade:
	docker exec km-backend alembic downgrade -1

# Development setup
dev-setup:
	cp frontend/.env.local.example frontend/.env.local
	cp backend/.env.example backend/.env
	make up
	make migrate

# Individual service logs
logs-fe:
	docker compose logs -f frontend

logs-be:
	docker compose logs -f backend

logs-db:
	docker compose logs -f db

# Testing
test-fe:
	docker exec km-frontend npm test

test-be:
	docker exec km-backend python -m pytest

# Build
build:
	docker compose build

build-fe:
	docker compose build frontend

build-be:
	docker compose build backend