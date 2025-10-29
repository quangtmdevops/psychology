#!/bin/bash

set -e
set -x

# Function to check if migrations need to be run
check_migrations() {
    # Chạy alembic current nhưng không dừng script nếu lỗi
    local current_migration
    current_migration=$(alembic current 2>/dev/null || true)

    # Nếu không có dòng nào, nghĩa là chưa có bảng alembic_version hoặc chưa migrate lần nào
    if [ -z "$current_migration" ]; then
        echo "No migrations applied yet, running initial setup..."
        return 0
    fi

    # Nếu alembic current trả về “head” hoặc revision cụ thể
    local head_migration
    head_migration=$(alembic heads | head -n 1 | awk '{print $1}')

    local current_revision
    current_revision=$(echo "$current_migration" | grep -oE '^[a-f0-9]+' || true)

    if [ "$current_revision" != "$head_migration" ]; then
        echo "Migrations are not up to date (current=$current_revision, head=$head_migration)"
        return 0
    else
        echo "Migrations already up to date (current=$current_revision)"
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
