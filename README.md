# Gestion_reservation_microservice

## Docker

Lancer l'API Gateway :

```bash
docker compose up api --build
```

Lancer les tests (par defaut: `api-gateway`) :

```bash
docker compose run --rm test
```

Pour tester un autre service :

changer uniquement "auth-service" par le nom de dossier pour tester autre service , exemple : "paiement-service"
```bash
docker compose run --rm auth-service poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
```