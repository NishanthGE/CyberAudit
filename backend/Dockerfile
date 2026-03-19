# ── Backend Dockerfile ─────────────────────────────────────────────────────────
# Python 3.11-slim base
FROM python:3.11-slim

WORKDIR /app

# System deps for scikit-learn and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libssl-dev libffi-dev curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Entrypoint that trains models if needed and starts the server
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose API port
EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
