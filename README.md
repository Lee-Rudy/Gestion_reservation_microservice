# Gestion_reservation_microservice

## Docker (essentiel)

Lancer l'API Gateway :

```bash
docker compose up api --build
```

Lancer les tests (par defaut: `api-gateway`) :

```bash
docker compose run --rm test
```

Pour tester un autre service :

```bash
docker compose run --rm auth-service poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
```