FROM python:3.11.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /uvx /bin/

WORKDIR /app

COPY ingestion /app/ingestion
COPY config/ingestion.logconf /app/config/
COPY pyproject.toml uv.lock /app/

RUN mkdir logs && touch ingestion.log
RUN uv sync --frozen

ENTRYPOINT ["uv", "run", "-m", "ingestion.pipeline"]
