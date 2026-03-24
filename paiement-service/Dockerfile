FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

RUN poetry install --only-root

EXPOSE 8004

CMD ["poetry", "run", "uvicorn", "paiement_service.main:app", "--host", "0.0.0.0", "--port", "8004"]
