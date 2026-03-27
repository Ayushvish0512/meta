#!/bin/bash
# Laiqa Growth Agent - Local Setup Script

set -e

echo "=== Laiqa Growth Agent Setup ==="

# 1. Copy env file
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ Created .env from .env.example — EDIT IT before continuing"
  echo "   Required: META_ACCESS_TOKEN, META_AD_ACCOUNT_ID, GEMINI_API_KEY"
  exit 1
fi

# 2. Start all services
echo "Starting Docker services..."
docker compose up -d --build

# 3. Wait for Postgres
echo "Waiting for Postgres..."
until docker compose exec postgres pg_isready -U laiqa; do sleep 2; done
echo "✅ Postgres ready"

# 4. Wait for n8n
echo "Waiting for n8n..."
sleep 15
echo "✅ Services started"

echo ""
echo "=== Access Points ==="
echo "n8n UI:        http://localhost:5678"
echo "Chroma:        http://localhost:8000"
echo "Sanitiser:     http://localhost:8001/health"
echo "Vector Bridge: http://localhost:8002/health"
echo ""
echo "=== Next Steps ==="
echo "1. Open n8n at http://localhost:5678"
echo "2. Import workflows from ./n8n-workflows/ (Settings > Import)"
echo "3. Set environment variables in n8n (Settings > Variables)"
echo "4. Activate Workflow 01 (Ingestion) first"
echo "5. Upload your business docs via POST http://localhost:8002/upsert"
