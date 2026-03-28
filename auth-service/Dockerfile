FROM python:3.13-slim

WORKDIR /app

ENV POETRY_REQUESTS_TIMEOUT=600 \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --without dev --no-interaction

COPY . .

RUN poetry install --only-root --no-interaction

EXPOSE 8001

CMD ["poetry", "run", "uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
