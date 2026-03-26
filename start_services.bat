@echo off
echo ========================================
echo DEMARRAGE DES MICROSERVICES
echo ========================================
echo.

echo [1/4] Arret des anciens conteneurs...
docker compose down

echo.
echo [2/4] Construction et demarrage des services...
docker compose up auth-service user-service --build -d

echo.
echo [3/4] Attente du demarrage des services (15 secondes)...
timeout /t 15 /nobreak

echo.
echo [4/4] Initialisation des bases de donnees...
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py

echo.
echo ========================================
echo SERVICES DEMARRES AVEC SUCCES
echo ========================================
echo.
echo Auth Service : http://localhost:8001/docs
echo User Service : http://localhost:8002/docs
echo.
echo Comptes de test :
echo - user@example.com / User@123
echo - admin@example.com / Admin@123
echo.
echo Appuyez sur une touche pour quitter...
pause > nul
