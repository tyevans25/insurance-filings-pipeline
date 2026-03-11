FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY pipeline/ /app/pipeline/
COPY src/ /app/src/

# CRITICAL: Copy data files INTO the image (not mounted)
# This avoids Mac file system issues
COPY data/input/ /data/input/
RUN mkdir -p /data/output

# Set Python path
ENV PYTHONPATH=/app

CMD ["python", "/app/pipeline/run_ingest.py"]