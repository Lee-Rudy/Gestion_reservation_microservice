# Paiement Service

Microservice de gestion des paiements, développé en **Python / FastAPI** selon les principes de l'**architecture hexagonale** (Ports & Adapters).

---

## Architecture hexagonale

```
src/paiement_service/
├── domain/                   # Couche métier pure (aucune dépendance externe)
│   ├── entities/             # Entité Paiement + enums Statut/Méthode
│   ├── events/               # Événements domaine (PaiementInitie, Valide…)
│   └── services/             # Règles métier transverses (montant, devise…)
├── application/              # Orchestration
│   ├── ports.py              # Interfaces (IPaiementRepository, IFournisseurPaiement)
│   └── use_cases.py          # Cas d'usage : Initier, Valider, Rembourser, Obtenir
└── adapters/                 # Implémentations concrètes des ports
    ├── http_controller.py    # API REST FastAPI
    ├── repository.py         # Stockage en mémoire
    └── payment_provider.py   # Fournisseur de paiement simulé (PSP)
```

> Le domaine et les cas d'usage ne dépendent jamais des adaptateurs.
> Pour changer de base de données ou de PSP, seul l'adaptateur concerné est remplacé.

---

## Cycle de vie d'un paiement

```
EN_ATTENTE ──► VALIDE ──► REMBOURSE
     │
     └──► REFUSE
```

---

## API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Statut du service |
| `POST` | `/paiements/` | Initier un paiement |
| `POST` | `/paiements/{id}/valider` | Valider via le PSP |
| `POST` | `/paiements/{id}/rembourser` | Rembourser un paiement validé |
| `GET` | `/paiements/{id}` | Consulter un paiement |

### Exemple — Initier un paiement

**Requête**
```bash
curl -X POST http://localhost:8004/paiements/ \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_id": "550e8400-e29b-41d4-a716-446655440000",
    "montant": "99.99",
    "devise": "EUR",
    "methode": "carte"
  }'
```

**Réponse** `201 Created`
```json
{
  "id": "a1b2c3d4-...",
  "reservation_id": "550e8400-...",
  "montant": "99.99",
  "devise": "EUR",
  "methode": "carte",
  "statut": "en_attente"
}
```

### Méthodes de paiement acceptées

| Valeur | Description |
|--------|-------------|
| `carte` | Carte bancaire |
| `virement` | Virement bancaire |
| `paypal` | PayPal |

### Devises acceptées

`EUR` · `USD` · `GBP`

### Règles métier

- Montant minimum : **0.01**
- Montant maximum : **100 000.00**

---

## Lancer le service

### Avec Docker (recommandé)

Depuis la **racine du projet** :

```bash
# Lancer uniquement le paiement-service
docker compose up paiement-service --build

# Lancer tous les services
docker compose up --build
```

Le service est disponible sur **http://localhost:8004**

La documentation interactive Swagger est disponible sur **http://localhost:8004/docs**

### En local

```bash
cd paiement-service
poetry install
poetry run uvicorn paiement_service.main:app --reload --port 8004
```

---

## Tests

### Via Docker

```bash
# Depuis la racine du projet
docker compose run --rm paiement-service poetry run pytest -v \
  --cov=src \
  --cov-report=term-missing \
  --cov-fail-under=80
```

### En local

```bash
cd paiement-service
poetry run pytest -v --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Résultats attendus

```
61 passed — coverage 100%
```

### Structure des tests

| Fichier | Couche testée |
|---------|---------------|
| `test_paiement_entity.py` | Entité — transitions d'état |
| `test_domain_service.py` | Service domaine — règles métier |
| `test_use_cases.py` | Cas d'usage — orchestration |
| `test_http_controller.py` | API HTTP — endpoints et codes de statut |

---

## Stack technique

| Outil | Rôle |
|-------|------|
| Python 3.13 | Langage |
| FastAPI | Framework HTTP |
| Pydantic | Validation des données |
| Poetry | Gestion des dépendances |
| pytest + pytest-cov | Tests et couverture (min. 80%) |
| black | Formatage du code |
| flake8 | Linting |
| mypy | Vérification des types |
