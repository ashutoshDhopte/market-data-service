#!/bin/bash
set -e

echo "Cleaning up old containers..."
docker-compose down -v

echo "Starting backend (api, db, kafka, redis)..."
docker-compose up --build -d

echo "Waiting for backend services to be ready..."
sleep 20  # Optional: use wait-for-it or Docker healthchecks

echo "Starting consumer..."
python3 scripts/ma_consumer.py