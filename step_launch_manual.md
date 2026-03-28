# Guide de lancement - Microservices Gestion Reservation

## ETAPE 1 : Demarrage MySQL et services backend

### 1.1 Demarrer MySQL et les services backend

```bash
docker compose up mysql auth-service user-service reservation-service paiement-service --build -d
```

Attendre environ 30 secondes que MySQL soit pret (healthcheck).

### 1.2 Initialiser les bases SQLite

```bash
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py
```

Resultats attendus :
- User cree : user@example.com / User@123
- Admin cree : admin@example.com / Admin@123

### 1.3 Verifier que les services sont actifs

```bash
docker ps
```

Vous devez voir :
- auth_service (port 8001)
- user_service (port 8002)
- reservation_service (port 8003)
- paiement_service (port 8004)
- mysql_db (port 3306)

## ETAPE 2 : Demarrer l'API Gateway

```bash
docker compose up api --build -d
```

Verifier : http://localhost:8000/docs

## ETAPE 3 : Demarrer le frontend

```bash
docker compose up front --build -d
```

Attendre 1-2 minutes le build NextJS.

Verifier : http://localhost:3000

## ETAPE 4 : Tester l'application

### 4.1 Test via Frontend (http://localhost:3000)

1. Cliquer sur "Inscription"
2. Creer un compte :
   - Nom : Jean Dupont
   - Email : jean@example.com
   - Mot de passe : Jean@2024
3. Se connecter avec ce compte
4. Faire une reservation
5. Verifier le paiement

### 4.2 Test Admin via Frontend

1. Se connecter avec admin@example.com / Admin@123
2. Acceder au Dashboard
3. Voir les statistiques
4. Consulter les logs

### 4.3 Test via Swagger

**Auth Service** (http://localhost:8001/docs)
```
POST /auth/login
username: admin@example.com
password: Admin@123
```

**User Service** (http://localhost:8002/docs)
```
GET /users/
```

**Reservation Service** (http://localhost:8003/docs)
```
GET /categories
```

**API Gateway** (http://localhost:8000/docs)
```
Tous les endpoints de tous les services sont accessibles via le gateway
```

## ETAPE 5 : Lancer les tests

### Test tous services

Windows :
```bash
run_all_tests.bat
```

Linux/Mac :
```bash
bash run_all_tests.sh
```

### Test service specifique

```bash
docker compose run --rm auth-service poetry run pytest -v --cov=src --cov-report=html
docker compose run --rm user-service poetry run pytest -v --cov=src --cov-report=html
docker compose run --rm reservation-service poetry run pytest -v --cov=src --cov-report=html
docker compose run --rm paiement-service poetry run pytest -v --cov=src --cov-report=html
```

Rapports HTML generes dans chaque `service/htmlcov/`

## COMMANDES ANNEXES

### Voir les logs

```bash
docker compose logs api
docker compose logs auth_service
docker compose logs user_service
docker compose logs reservation_service
docker compose logs paiement_service
docker compose logs mysql_db
docker compose logs front
```

### Suivre les logs en temps reel

```bash
docker compose logs -f api
```

### Redemarrer un service

```bash
docker compose restart auth_service
docker compose restart reservation_service
```

### Arreter tout

```bash
docker compose down
```

### Arreter et supprimer les volumes (reinitialisation complete)

```bash
docker compose down -v
```

### Reconstruire un service specifique

```bash
docker compose up auth-service --build -d
```

### Verifier l'etat des conteneurs

```bash
docker ps -a
```

### Entrer dans un conteneur

```bash
docker exec -it auth_service /bin/sh
docker exec -it mysql_db mysql -uroot -proot
```

### Voir les reseaux Docker

```bash
docker network ls
```

## ORDRE DE LANCEMENT RECOMMANDE

### Methode 1 : Tout en une fois

```bash
docker compose up --build
```

Puis dans un autre terminal :
```bash
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py
```

### Methode 2 : Etape par etape (recommandee)

```bash
# 1. MySQL d'abord
docker compose up mysql --build -d

# 2. Attendre 30 secondes

# 3. Services backend
docker compose up auth-service user-service reservation-service paiement-service --build -d

# 4. Initialiser SQLite
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py

# 5. API Gateway
docker compose up api --build -d

# 6. Frontend
docker compose up front --build -d
```

### Methode 3 : Backend seulement (pour tests Swagger)

```bash
docker compose up mysql api auth-service user-service reservation-service paiement-service --build -d
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py
```

Acceder : http://localhost:8000/docs

## TROUBLESHOOTING

### Probleme : "no such file or directory: Dockerfile"

Solution : Verifier que le Dockerfile existe dans chaque service

```bash
ls api-gateway/Dockerfile
ls auth-service/Dockerfile
ls user-service/Dockerfile
ls reservation-service/Dockerfile
ls paiement-service/Dockerfile
ls front/Dockerfile
```

### Probleme : MySQL ne demarre pas

```bash
docker compose logs mysql
docker compose down -v
docker compose up mysql --build -d
```

### Probleme : Service ne se connecte pas a MySQL

Verifier les variables d'environnement dans docker-compose.yml et que MySQL est healthy :

```bash
docker compose ps
```

### Probleme : Port deja utilise

```bash
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

Tuer le processus ou changer le port dans docker-compose.yml

### Probleme : Frontend affiche erreur 500

Verifier que l'API Gateway est demarre :

```bash
docker compose ps api
docker compose logs api
```

## WORKFLOW COMPLET DE TEST

1. Lancer tous les services
2. Initialiser les bases SQLite
3. Ouvrir http://localhost:3000
4. S'inscrire (nouveau compte)
5. Se connecter
6. Faire une reservation
7. Se deconnecter
8. Se connecter en admin (admin@example.com / Admin@123)
9. Voir dashboard et reservations
10. Tester endpoints via Swagger (http://localhost:8000/docs)

## ACCES RAPIDES

- Frontend : http://localhost:3000
- API Gateway Swagger : http://localhost:8000/docs
- Auth Service Swagger : http://localhost:8001/docs
- User Service Swagger : http://localhost:8002/docs
- Reservation Service Swagger : http://localhost:8003/docs
- Paiement Service Swagger : http://localhost:8004/docs


Vérifier que la catégorie existe dans MySQL :
docker compose logs reservation-service --tail=30
