FROM python:3.14-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
# Install dependencies into the system environment for simplicity in Docker
RUN uv pip install --system -r pyproject.toml

COPY . .

# Run seeder, then start the dashboard
CMD python seed_data.py && python app.py
