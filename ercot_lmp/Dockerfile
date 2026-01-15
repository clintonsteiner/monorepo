FROM python:3.11-slim

WORKDIR /app

# Copy source code and PEX binaries from Pants build context
COPY . .

ENV PYTHONPATH=/app

# Default entrypoint runs main.py
ENTRYPOINT ["python", "/app/ercot_lmp/scripts/main.py"]
