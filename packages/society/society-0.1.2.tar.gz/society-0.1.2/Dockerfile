FROM python:3.12-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install -e .

# Build frontend
WORKDIR /app/src/society/web/frontend
COPY src/society/web/frontend/package*.json ./
RUN npm install
COPY src/society/web/frontend/ ./
RUN npm run build

WORKDIR /app

# Expose port
EXPOSE 8000

# Start server (Railway provides PORT env var)
CMD uvicorn society.web.api:app --host 0.0.0.0 --port ${PORT:-8000}
