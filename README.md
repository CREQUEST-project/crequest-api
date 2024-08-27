# crequest-api
Start project
```
docker compose -f "docker-compose.yml" up -d --build
```
Create a Migration Script
```
alembic revision -m "create int table" --autogenerate
```
Run migrations
```
alembic upgrade head
```
To check the logs of a specific service, add the name of the service, e.g.:
```
docker compose logs backend
```
To get inside the container with a bash session you can start the stack with:
```
docker compose exec backend bash
```
Run pre-commit
```
pre-commit run --all-files
```
