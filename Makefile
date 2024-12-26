.DEFAULT_GOAL := up

.PHONY: up down logs ps rebuild clean

up:
	docker-compose -f docker/docker-compose.yml up -d

down:
	docker-compose -f docker/docker-compose.yml down

logs:
	docker-compose -f docker/docker-compose.yml logs -f

ps:
	docker-compose -f docker/docker-compose.yml ps

rebuild:
	docker-compose -f docker/docker-compose.yml build --no-cache
	docker-compose -f docker/docker-compose.yml up -d --force-recreate

clean:
	docker-compose -f docker/docker-compose.yml down -v --remove-orphans