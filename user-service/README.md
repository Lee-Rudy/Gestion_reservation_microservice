# User Service - Architecture Hexagonale

Service de gestion des utilisateurs (CRUD complet), architecture hexagonale, Python 3.13, FastAPI et SQLite.

## Architecture

```
user-service/
├── src/user_service/
│   ├── domain/              # Entités et ports (interfaces)
│   ├── application/         # Use cases (logique métier)
│   └── infrastructure/      # Adapters (API, DB, sécurité)
├── tests/
│   ├── unit/               # Tests unitaires
│   └── integration/        # Tests d'intégration
└── init_db.py              # Script d'initialisation DB
```

## Démarrage rapide

### 1. Installer les dépendances

```bash
poetry install
```

### 2. Initialiser la base de données

```bash
poetry run python init_db.py
```

Cela crée 2 utilisateurs :
- **User** : `user@example.com` / `User@123`
- **Admin** : `admin@example.com` / `Admin@123`

### 3. Lancer le service

```bash
poetry run uvicorn user_service.main:app --host 0.0.0.0 --port 8002 --reload
```

## Swagger / Documentation API

Accédez à **http://localhost:8002/docs**

### Endpoints disponibles (CRUD complet)

- `POST /users/` - Créer un utilisateur
- `GET /users/` - Lister tous les utilisateurs
- `GET /users/{id}` - Récupérer un utilisateur
- `PUT /users/{id}` - Mettre à jour un utilisateur
- `DELETE /users/{id}` - Supprimer un utilisateur
- `GET /health` - Health check

## Tests

### Tests unitaires + intégration

```bash
poetry run pytest -v
```

### Tests avec couverture

```bash
poetry run pytest --cov=src --cov-report=html --cov-report=term-missing
```

## Tester sur Swagger

1. Ouvrir **http://localhost:8002/docs**
2. Tester `GET /users/` pour voir les 2 utilisateurs initiaux
3. Tester `POST /users/` pour créer un nouvel utilisateur :
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "password": "Secure@123",
     "role": "USER"
   }
   ```
4. Tester `GET /users/1` pour récupérer l'utilisateur ID 1
5. Tester `PUT /users/1` pour modifier
6. Tester `DELETE /users/1` pour supprimer
