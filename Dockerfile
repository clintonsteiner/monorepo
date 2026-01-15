FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests>=2.31.0 pandas>=2.0.0 beautifulsoup4>=4.12.0 lxml>=5.0.0 html5lib>=1.1

# Copy application code
COPY ercot_lmp/ /app/ercot_lmp/
COPY lib_ercot/ /app/lib_ercot/

ENV PYTHONPATH=/app

CMD ["python", "/app/ercot_lmp/scripts/main.py"]
