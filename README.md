# Gestion Reservation - Microservices

Architecture microservices avec architecture hexagonale, Python 3.13, FastAPI, MySQL, SQLite, NextJS et Docker.

## Services

- **api-gateway** (8000) - Gateway principal
- **auth-service** (8001) - Authentification JWT (SQLite)
- **user-service** (8002) - Gestion utilisateurs CRUD (SQLite)
- **reservation-service** (8003) - Reservations (MySQL)
- **paiement-service** (8004) - Paiements (MySQL)
- **front** (3000) - Interface NextJS
- **mysql** (3306) - Base de donnees MySQL

## Demarrage complet

### Lancer tous les services

```bash
docker compose up --build
```

Initialiser les bases SQLite (auth + user) :

```bash
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py
```

### Arreter tous les services

```bash
docker compose down
```

## Lancer les services separement

### Backend uniquement (sans frontend)

```bash
docker compose up api auth-service user-service reservation-service paiement-service mysql --build -d
```

### API Gateway seul

```bash
docker compose up api --build
```

### Auth + User services

```bash
docker compose up auth-service user-service --build -d
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py
```

### Reservation + Paiement + MySQL

```bash
docker compose up reservation-service paiement-service mysql --build -d
```

### Frontend seul

```bash
docker compose up front --build
```

## Tests

### Tests tous services confondus (coverage global)

```bash
docker compose run --rm auth-service poetry run pytest -v --cov=src --cov-report=html
docker compose run --rm user-service poetry run pytest -v --cov=src --cov-report=html
docker compose run --rm reservation-service poetry run pytest -v --cov=src --cov-report=html
docker compose run --rm paiement-service poetry run pytest -v --cov=src --cov-report=html
docker compose run --rm api poetry run pytest -v --cov=src --cov-report=html
```

### Test d'un service specifique

```bash
docker compose run --rm auth-service poetry run pytest -v --cov=src --cov-report=term-missing
```

## Acces aux services

- Frontend : http://localhost:3000
- API Gateway : http://localhost:8000/docs
- Auth Service : http://localhost:8001/docs
- User Service : http://localhost:8002/docs
- Reservation Service : http://localhost:8003/docs
- Paiement Service : http://localhost:8004/docs

## Comptes de test

Apres initialisation SQLite :

- User : user@example.com / User@123
- Admin : admin@example.com / Admin@123

## Workflow

1. User s'inscrit ou se connecte (auth-service)
2. User fait une reservation (reservation-service)
3. Systeme calcule devis et cree paiement (paiement-service via saga)
4. Si paiement valide, reservation confirmee
5. Admin peut voir dashboard, logs, et gerer utilisateurs

## Commandes utiles

```bash
docker compose logs api
docker compose logs auth_service
docker compose restart reservation-service
docker ps
```
