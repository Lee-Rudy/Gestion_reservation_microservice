#!/bin/bash

echo "=========================================="
echo "TESTS COVERAGE - TOUS LES SERVICES"
echo "=========================================="

SERVICES=("api-gateway" "auth-service" "user-service" "reservation-service" "paiement-service")

for service in "${SERVICES[@]}"; do
  echo ""
  echo ">>> Testing $service..."
  docker compose run --rm $service poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html || true
done

echo ""
echo "=========================================="
echo "TESTS TERMINES"
echo "=========================================="
echo "Rapports HTML dans chaque service/htmlcov/"
