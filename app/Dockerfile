FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction

COPY . .

RUN mkdir -p /tmp/uploads
