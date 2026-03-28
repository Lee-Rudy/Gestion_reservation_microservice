# Guide des chemins (`path`) — API Gateway

Ce document explique **quoi saisir dans le champ `path`** de Swagger pour les routes proxy, en se basant sur `api-gateway/src/api_gateway/main.py`.

## Principe

La gateway préfixe l’URL par un service, puis **recolle** la valeur de `path` pour reconstruire l’URL du microservice.

| Route gateway | Cible réelle sur le service |
|---------------|----------------------------|
| `/auth/{path}` | `http://auth-service:8001` **+** `/auth/` **+** `{path}` |
| `/users/{path}` | `http://user-service:8002` **+** `/users/` **+** `{path}` |
| `/reservations/{path}` | `http://reservation-service:8003` **+** `/reservations/` **+** `{path}` |
| `/categories/{path}` | `http://reservation-service:8003` **+** `/categories/` **+** `{path}` |
| `/paiements/{path}` | `http://paiement-service:8004` **+** `/` **+** `{path}` (voir cas particulier ci-dessous) |

Dans Swagger, **`path` est uniquement la partie variable** : vous ne retapez pas `/auth` ni le host.

---

## 1. Authentification — `POST/GET /auth/{path}`

Le service auth expose le préfixe `/auth` côté backend. La gateway appelle donc `/auth/{path}` sur le service.

| À mettre dans `path` | Méthode | URL équivalente (via gateway) | Rôle |
|----------------------|---------|-------------------------------|------|
| `login` | POST | `POST /auth/login` | Connexion (formulaire OAuth2 : `username`, `password`) |
| `verify` | GET | `GET /auth/verify` | Vérifier le JWT (header `Authorization: Bearer …`) |

**Exemple Swagger :** pour tester le login, endpoint `POST /auth/{path}`, champ `path` = `login` (sans slash au début).

---

## 2. Utilisateurs — `/users/{path}`

Préfixe backend : `/users`.

| `path` | Méthode | Exemple d’URL gateway |
|--------|---------|------------------------|
| *(vide, si l’UI l’autorise)* ou selon l’outil | POST | `POST /users/` — création |
| *(vide)* | GET | `GET /users/` — liste |
| `{id}` | GET / PUT / DELETE | ex. `1` → `GET /users/1` |
| `by-email/{email}` | GET | réservé usage interne auth (peu utile dans Swagger) |

Si Swagger n’accepte pas un `path` vide, utilisez un client HTTP (curl, Postman) avec l’URL exacte `http://<gateway>/users/`.

---

## 3. Réservations — routes dédiées + `/reservations/{path}`

Certaines URLs sont **sans** paramètre `path` dans Swagger :

| URL gateway (fixe) | Méthode | Rôle |
|--------------------|---------|------|
| `/reservations` | GET | Liste des réservations (agrégation SQL) |

Ensuite, le proxy avec paramètre :

| `path` | Méthode | Rôle |
|--------|---------|------|
| *(vide)* | POST | `POST /reservations/` — créer |
| `{id}` | GET / PUT / DELETE | ex. `42` — lire / modifier / supprimer |
| `{id}/quote` | GET | Devis pour la réservation `id` |
| `{id}/confirm` | PUT | Confirmer la réservation `id` |
| `saga` | POST | Saga réservation + paiement (`POST /reservations/saga`) |

Exemple saga : `path` = `saga` (une seule partie, sans `reservations/` devant).

---

## 4. Catégories — route dédiée + `/categories/{path}`

| URL gateway (fixe) | Méthode | Rôle |
|--------------------|---------|------|
| `/categories` | GET | Liste des catégories |

Proxy :

| `path` | Méthode | Rôle |
|--------|---------|------|
| *(vide)* | POST | Créer une catégorie |
| `{id}` | GET / PUT / DELETE | ex. `3` — détail / mise à jour / suppression |

---

## 5. Paiements — `/paiements/{path}` (cas particulier)

Dans le code, la cible est `f"/{path}"` sur le service paiement **sans** rajouter `/paiements/` automatiquement. Le service expose pourtant des routes sous **`/paiements/...`**. Il faut donc que **`path` commence par `paiements/`**.

| `path` | Méthode | URL finale sur le service |
|--------|---------|---------------------------|
| `paiements/` | POST | `POST /paiements/` — initier un paiement |
| `paiements/{uuid}` | GET | Détail d’un paiement |
| `paiements/{uuid}/valider` | POST | Valider |
| `paiements/{uuid}/rembourser` | POST | Rembourser |

Exemple : `path` = `paiements/a1b2c3d4-e5f6-7890-abcd-ef1234567890/valider`.

---

## 6. Routes admin (pas de `path` à deviner)

Ces endpoints sont implémentés **directement** sur la gateway :

| URL | Méthode | Rôle |
|-----|---------|------|
| `/admin/stats` | GET | Statistiques agrégées |
| `/admin/logs` | GET | Logs (query `limit` optionnel) |

---

## 7. Rappels pratiques

1. **Pas de slash initial** dans `path` sauf pour les segments internes (ex. `5/quote`, pas `/5/quote`).
2. **Paiements** : pensez au préfixe `paiements/` dans `path`, contrairement aux autres services.
3. **Corps et en-têtes** : identiques à ce qu’attend le microservice (JSON, formulaire login, `Authorization`, etc.).
4. Port gateway local typique : **8000** (voir `docker-compose` / votre lancement).

Pour des exemples de corps JSON et captures Swagger, voir aussi `GUIDE_SWAGGER_API_GATEWAY.md` à la racine du dépôt.
