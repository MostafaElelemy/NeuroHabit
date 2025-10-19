#!/bin/bash

# NeuroHabit Startup Script
# This script automates the complete setup and startup process

set -e  # Exit on error

echo "============================================================"
echo "           NeuroHabit - AI Habit Coach Setup"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 1: Environment setup
echo "Step 1: Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping${NC}"
fi
echo ""

# Step 2: Build images
echo "Step 2: Building Docker images..."
echo "This may take 5-10 minutes on first run..."
docker-compose build
echo -e "${GREEN}✓ Docker images built successfully${NC}"
echo ""

# Step 3: Start services
echo "Step 3: Starting services..."
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Step 4: Run migrations
echo "Step 4: Running database migrations..."
docker-compose exec -T backend alembic upgrade head
echo -e "${GREEN}✓ Database migrations completed${NC}"
echo ""

# Step 5: Train ML model
echo "Step 5: Training ML model..."
docker-compose exec -T backend python -m app.ml.trainer
echo -e "${GREEN}✓ ML model trained${NC}"
echo ""

# Step 6: Seed data
echo "Step 6: Seeding demo data..."
docker-compose exec -T backend python seed.py
echo -e "${GREEN}✓ Demo data seeded${NC}"
echo ""

# Final status check
echo "============================================================"
echo "           Setup Complete! 🎉"
echo "============================================================"
echo ""
echo "Services Status:"
docker-compose ps
echo ""
echo "Access Points:"
echo -e "  ${GREEN}Frontend:${NC}     http://localhost:5173"
echo -e "  ${GREEN}Backend API:${NC}  http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}     http://localhost:8000/docs"
echo ""
echo "Demo Credentials:"
echo -e "  ${YELLOW}Email:${NC}    demo@neurohabit.com"
echo -e "  ${YELLOW}Password:${NC} demo123"
echo ""
echo "Useful Commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo "  Run tests:        docker-compose exec backend pytest -v"
echo ""
echo "For more information, see RUNBOOK.md"
echo "============================================================"
