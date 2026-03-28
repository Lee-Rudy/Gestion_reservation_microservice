# Guide Swagger - API Gateway

## Acces Swagger API Gateway

URL : http://localhost:8000/docs

L'API Gateway expose tous les endpoints de tous les services via des routes proxy.

---

## IMPORTANT : Comment utiliser les routes proxy

Les endpoints proxy utilisent un parametre `path` qui represente le chemin apres le prefixe.

### Exemple : POST /auth/login

Pour appeler `POST /auth/login` via le gateway :

1. Chercher l'endpoint : `POST /auth/{path}`
2. Cliquer "Try it out"
3. Dans le champ `path`, entrer : `login`
4. Remplir le body selon l'endpoint voulu

---

## ENDPOINTS DISPONIBLES

### 1. Authentification (via /auth/{path})

#### POST /auth/login

Champ `path` : `login`

Body (OAuth2 form) :
- username : `admin@example.com`
- password : `Admin@123`

Reponse : Token JWT

#### GET /auth/verify

Champ `path` : `verify`

Headers :
- Authorization : `Bearer <votre_token>`

Reponse : Email et role

---

### 2. Utilisateurs (via /users/{path})

#### POST /users/ (Creer utilisateur)

Champ `path` : (laisser vide ou mettre `/`)

Body JSON :
```json
{
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "password": "Jean@2024",
  "role": "USER"
}
```

#### GET /users/ (Liste utilisateurs)

Champ `path` : (laisser vide)

Reponse : Array d'utilisateurs

#### GET /users/1 (Utilisateur par ID)

Champ `path` : `1`

Reponse : Details de l'utilisateur ID 1

---

### 3. Categories (via /categories ou /categories/{path})

#### GET /categories (Liste categories)

Utiliser l'endpoint direct `GET /categories` (pas le proxy)

Reponse : Array avec 3 categories

OU via proxy :

Endpoint : `GET /categories/{path}`
Champ `path` : (laisser vide)

---

### 4. Reservations (via /reservations/{path})

#### POST /reservations/saga (Creer reservation + paiement)

Endpoint : `POST /reservations/{path}`
Champ `path` : `saga`

Body JSON :
```json
{
  "user_email": "admin@example.com",
  "category_id": 1,
  "start_date": "2026-04-01T14:00:00",
  "end_date": "2026-04-02T18:00:00",
  "nb_persons": 2,
  "methode": "carte",
  "devise": "EUR"
}
```

Reponse : Reservation CONFIRMED avec paiement valide

#### GET /reservations (Liste reservations)

Utiliser l'endpoint direct `GET /reservations`

Reponse : Array de reservations

#### GET /reservations/1 (Reservation par ID)

Endpoint : `GET /reservations/{path}`
Champ `path` : `1`

Reponse : Details reservation ID 1

---

### 5. Paiements (via /paiements/{path})

#### GET /paiements/{id}

Champ `path` : `<id_du_paiement>`

Reponse : Details du paiement

---

### 6. Admin (endpoints directs)

#### GET /admin/stats

Endpoint direct (pas de proxy)

Reponse :
```json
{
  "users": 2,
  "reservations": 5,
  "paiements": 3
}
```

#### GET /admin/logs

Endpoint direct

Parametres :
- limit : 50 (par defaut)

Reponse : Array de logs

---

## WORKFLOW COMPLET VIA SWAGGER

### Etape 1 : Creer un utilisateur

Endpoint : `POST /users/{path}`
Path : (vide)
Body :
```json
{
  "name": "Test Swagger",
  "email": "swagger@test.com",
  "password": "Swagger@123",
  "role": "USER"
}
```

Copier l'ID retourne (exemple : 3)

### Etape 2 : Se connecter

Endpoint : `POST /auth/{path}`
Path : `login`
Form :
- username : `swagger@test.com`
- password : `Swagger@123`

Copier le `access_token`

### Etape 3 : Autoriser avec le token

1. Cliquer sur le bouton "Authorize" en haut a droite
2. Coller le token
3. Cliquer "Authorize"
4. Cliquer "Close"

### Etape 4 : Verifier le token

Endpoint : `GET /auth/{path}`
Path : `verify`

Reponse : Votre email et role

### Etape 5 : Faire une reservation

Endpoint : `POST /reservations/{path}`
Path : `saga`
Body :
```json
{
  "user_email": "swagger@test.com",
  "category_id": 1,
  "start_date": "2026-04-10T14:00:00",
  "end_date": "2026-04-12T11:00:00",
  "nb_persons": 2,
  "methode": "carte",
  "devise": "EUR"
}
```

Reponse : Reservation CONFIRMED

### Etape 6 : Voir les reservations

Endpoint : `GET /reservations`

Reponse : Liste avec votre reservation

### Etape 7 : Voir les stats admin

Endpoint : `GET /admin/stats`

Reponse : Stats mises a jour

---

## EXEMPLES DE CHEMINS (path)

| Endpoint voulu | Proxy a utiliser | Valeur du champ `path` |
|----------------|------------------|------------------------|
| POST /auth/login | POST /auth/{path} | `login` |
| GET /auth/verify | GET /auth/{path} | `verify` |
| POST /users/ | POST /users/{path} | (vide) |
| GET /users/1 | GET /users/{path} | `1` |
| GET /categories | GET /categories | (pas de path) |
| POST /reservations/saga | POST /reservations/{path} | `saga` |
| GET /reservations/1 | GET /reservations/{path} | `1` |
| GET /paiements/abc123 | GET /paiements/{path} | `abc123` |

---

## ENDPOINTS DIRECTS (sans proxy)

Ces endpoints sont implementes directement dans le gateway :

- `GET /` - Status du gateway
- `GET /health` - Health check
- `GET /categories` - Liste categories
- `GET /reservations` - Liste reservations
- `GET /admin/stats` - Statistiques
- `GET /admin/logs` - Logs

Pour ces endpoints, PAS besoin du parametre `path`.

---

## ERREURS COURANTES

### Erreur : "Field required" pour path

Cause : Vous essayez d'appeler un endpoint direct avec un proxy

Solution : Utilisez l'endpoint direct si disponible, ou mettez une valeur dans path

### Erreur : 404 Not Found

Cause : Le chemin est incorrect

Exemples INCORRECTS :
- Path : `/login` (ne pas mettre le slash)
- Path : `auth/login` (ne pas mettre le prefixe)

Exemples CORRECTS :
- Path : `login`
- Path : `1`
- Path : `saga`

### Erreur : 307 Temporary Redirect

Cause : FastAPI ajoute automatiquement un slash

Solution : Cela fonctionne quand meme, ignorez cette redirection

---

## TEST RAPIDE

### 1. Test connexion

Endpoint : `POST /auth/{path}`
Path : `login`
Username : `admin@example.com`
Password : `Admin@123`

DOIT RETOURNER : Token JWT

### 2. Test categories

Endpoint : `GET /categories`

DOIT RETOURNER : 3 categories avec prix

### 3. Test reservation

Endpoint : `POST /reservations/{path}`
Path : `saga`
Body :
```json
{
  "user_email": "admin@example.com",
  "category_id": 1,
  "start_date": "2026-04-01T14:00:00",
  "end_date": "2026-04-02T11:00:00",
  "nb_persons": 2,
  "methode": "carte",
  "devise": "EUR"
}
```

DOIT RETOURNER : 201 avec reservation CONFIRMED

---

## ALTERNATIVE : Tester directement sur les services

Au lieu d'utiliser le gateway (8000), vous pouvez tester directement :

- Auth : http://localhost:8001/docs
- User : http://localhost:8002/docs
- Reservation : http://localhost:8003/docs
- Paiement : http://localhost:8004/docs

Sur ces Swagger, les endpoints n'ont PAS besoin du parametre `path`.

Exemple direct sur port 8001 :
- `POST /auth/login` (pas de path a remplir)

---

## RECOMMANDATION

Pour les tests, utilisez plutot les Swagger directs :

- http://localhost:8001/docs pour auth
- http://localhost:8003/docs pour reservations

Le gateway est surtout utilise par le frontend.

Mais si vous voulez tester le gateway, suivez les exemples ci-dessus avec le parametre `path`.
