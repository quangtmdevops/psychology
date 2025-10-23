#!/bin/bash

set -e
set -x

# Function to check if migrations need to be run
check_migrations() {
    local last_migration=$(alembic current 2>/dev/null | head -1 | cut -d" " -f1)
    if [ -z "$last_migration" ]; then
        echo "No migrations applied yet, running initial setup..."
        return 0
    else
        echo "Migrations already applied. Current migration: $last_migration"
        return 1
    fi
}

echo "Waiting for database..."
while ! nc -z db 5432; do
    sleep 1
done

echo "Database is ready!"

# Check if we need to run migrations
if check_migrations; then
    echo "Running database migrations..."
    alembic upgrade head
    
    echo "Importing initial data..."
    python -m app.scripts.import_datas
else
    echo "Skipping migrations and data import - already applied"
fi

echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
