FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

RUN poetry install --only-root

EXPOSE 8003

CMD ["poetry", "run", "uvicorn", "reservation_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
