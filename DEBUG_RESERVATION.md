# Debug Reservation - Erreur 400

## Corrections appliquees

1. Frontend : Ajout de `methode` et `devise` dans le payload
2. Frontend : Calcul correct de la date de fin (jour suivant)
3. Frontend : Logs console pour deboguer
4. Backend : Logs detailles dans saga_controller
5. API Gateway : Routes /categories et /reservations fixes

---

## Tester maintenant

### 1. Ouvrir console navigateur

1. Appuyer F12
2. Aller dans "Console"
3. Garder ouvert

### 2. Faire une reservation

1. Aller sur http://localhost:3000/reservation
2. Verifier que les categories s'affichent
3. Remplir :
   - Categorie : Hotel
   - Date : 2026-04-01
   - Heure debut : 14:00
   - Heure fin : 18:00
   - Personnes : 2
4. Cliquer "Confirmer"
5. Cliquer "Paiement"
6. Cliquer "Confirmer et payer"

### 3. Regarder les logs console

Dans la console (F12), vous devez voir :
```
Sending reservation: {category_id: 1, start_date: "2026-04-01T14:00:00", ...}
```

Si erreur, vous verrez :
```
Reservation error: {detail: "..."}
```

---

## Logs backend

```bash
docker compose logs reservation-service --tail=50
```

Vous devez voir :
```
INFO: Saga request: user=..., cat=1, dates=...
```

Si erreur, vous verrez :
```
ERROR: Saga ValueError: ...
```

---

## Test direct via Swagger

http://localhost:8003/docs

POST /reservations/saga

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

IMPORTANT : end_date doit etre APRES start_date

---

## Problemes possibles

### Erreur "categorie inconnue"

Cause : category_id invalide ou categorie non trouvee dans MySQL

Verifier :
```bash
docker exec mysql_db mysql -uroot -proot -e "USE reservation_db; SELECT * FROM categories WHERE id=1;"
```

Doit retourner la categorie Hotel

### Erreur "date de debut doit etre dans le futur"

Cause : Date choisie est passee

Solution : Choisir une date future (ex: 2026-04-01)

### Erreur "date de debut doit etre anterieure a date de fin"

Cause : end_date <= start_date

Solution : Le frontend calcule maintenant end_date = start_date + 1 jour automatiquement

---

## Payload correct frontend

```json
{
  "category_id": 1,
  "start_date": "2026-04-01T14:00:00",
  "end_date": "2026-04-02T18:00:00",
  "nb_persons": 2,
  "user_email": "admin@example.com",
  "methode": "carte",
  "devise": "EUR"
}
```

---

## Si ca bloque toujours

1. Voir logs console navigateur (F12)
2. Voir logs backend :
```bash
docker compose logs reservation-service --tail=100
docker compose logs paiement-service --tail=50
```

3. Tester directement sur Swagger avec le JSON ci-dessus

4. Verifier que MySQL a bien les categories :
```bash
docker exec mysql_db mysql -uroot -proot -e "USE reservation_db; SELECT COUNT(*) FROM categories;"
```

Doit retourner 3

---

## Rafraichir apres corrections

```bash
docker compose restart front
```

Puis F5 sur la page http://localhost:3000/reservation
