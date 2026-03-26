# Auth Service - Architecture Hexagonale

Service d'authentification avec JWT, architecture hexagonale, Python 3.13, FastAPI et SQLite.

## Architecture

```
auth-service/
├── src/auth_service/
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
poetry run uvicorn auth_service.main:app --host 0.0.0.0 --port 8001 --reload
```

## Swagger / Documentation API

Accédez à **http://localhost:8001/docs**

### Endpoints disponibles

- `POST /auth/login` - Connexion (retourne un JWT)
- `GET /auth/verify` - Vérifier un token JWT
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

1. Ouvrir **http://localhost:8001/docs**
2. Cliquer sur `POST /auth/login`
3. Cliquer "Try it out"
4. Entrer :
   - **username** : `user@example.com`
   - **password** : `User@123`
5. Cliquer "Execute"
6. Copier le `access_token` retourné
7. Cliquer sur le bouton "Authorize" en haut de la page
8. Coller le token (préfixe `Bearer` automatique)
9. Tester `GET /auth/verify` pour valider le token
