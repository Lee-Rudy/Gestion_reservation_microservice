@echo off
echo ==========================================
echo TESTS COVERAGE - TOUS LES SERVICES
echo ==========================================

set SERVICES=api-gateway auth-service user-service reservation-service paiement-service

for %%s in (%SERVICES%) do (
    echo.
    echo Testing %%s...
    docker compose run --rm %%s poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html
)

echo.
echo ==========================================
echo TESTS TERMINES
echo ==========================================
echo Rapports HTML dans chaque service/htmlcov/
pause
