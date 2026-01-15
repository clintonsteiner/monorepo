FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    requests>=2.31.0 \
    pandas>=2.0.0 \
    beautifulsoup4>=4.12.0 \
    lxml>=5.0.0 \
    html5lib>=1.1

# Copy source code
COPY ercot_lmp/ /app/ercot_lmp/
COPY lib_ercot/ /app/lib_ercot/
COPY hello_world/ /app/hello_world/

# Copy PEX binaries
COPY dist/ercot_lmp.pex /app/bin/ercot_lmp.pex
COPY dist/hello_world.pex /app/bin/hello_world.pex

ENV PYTHONPATH=/app
ENV PATH="/app/bin:${PATH}"

# Default entrypoint
ENTRYPOINT ["python", "/app/ercot_lmp/scripts/main.py"]
