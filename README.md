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
TEST_SERVICE=auth-service docker compose run --rm test
```