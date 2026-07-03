#!/bin/sh
set -e

echo "Creating test database if it does not exist..."
PGPASSWORD=postgres createdb -h db -U postgres docprocessor_test 2>/dev/null || true

echo "Running migrations on main database..."
alembic upgrade head

echo "Running migrations on test database..."
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/docprocessor_test \
  alembic upgrade head

echo "All migrations applied. Starting application..."
exec "$@"
