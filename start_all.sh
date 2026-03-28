#!/bin/bash

echo "=========================================="
echo "LANCEMENT COMPLET - MICROSERVICES"
echo "=========================================="
echo ""

echo "[1/3] Lancement de tous les services..."
echo "Cette etape peut prendre 2-3 minutes la premiere fois"
docker compose up --build -d

if [ $? -ne 0 ]; then
    echo "ERREUR lors du lancement des services"
    exit 1
fi

echo ""
echo "[2/3] Attente du demarrage complet (15 secondes)..."
sleep 15

echo ""
echo "[3/3] Initialisation des bases SQLite..."
docker exec -it auth_service poetry run python init_db.py
docker exec -it user_service poetry run python init_db.py

echo ""
echo "=========================================="
echo "APPLICATION PRETE"
echo "=========================================="
echo ""
echo "Frontend : http://localhost:3000"
echo "API Gateway : http://localhost:8000/docs"
echo ""
echo "Comptes de test :"
echo "- user@example.com / User@123"
echo "- admin@example.com / Admin@123"
echo ""
echo "Pour arreter : docker compose down"
echo ""
