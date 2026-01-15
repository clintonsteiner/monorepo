FROM python:3.11-slim

WORKDIR /app

# Copy PEX binaries from Pants build context
COPY . .

# Default entrypoint runs the PEX binary
ENTRYPOINT ["/app/ercot_lmp.pex"]
