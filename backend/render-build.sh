#!/usr/bin/env bash
set -e

echo "Starting backend build..."

# Install python dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo "Running alembic migrations..."
alembic upgrade head

echo "Backend build completed successfully."
