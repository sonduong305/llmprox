#!/bin/bash

# Set error handling
set -o errexit
set -o pipefail
set -o nounset

# Load .env file if it exists
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE"
    set -a # automatically export all variables
    source "$ENV_FILE"
    set +a
else
    echo "Warning: .env file not found. Using default values."
fi

# Default PostgreSQL settings (will be overridden by .env if it exists)
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_DB="${POSTGRES_DB:-llmprox}"

# Construct DATABASE_URL
export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

# Default Django settings (will be overridden by .env if it exists)
export DJANGO_DEBUG="${DJANGO_DEBUG:-True}"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.local}"
export DJANGO_SECRET_KEY="${DJANGO_SECRET_KEY:-your-secret-key-here}"
export DJANGO_ADMIN_URL="${DJANGO_ADMIN_URL:-admin/}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1}"

# Print current settings (useful for debugging)
echo "Current settings:"
echo "DATABASE_URL: $DATABASE_URL"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "DJANGO_DEBUG: $DJANGO_DEBUG"
echo "DJANGO_ALLOWED_HOSTS: $DJANGO_ALLOWED_HOSTS"

# Check if PostgreSQL is available
check_postgres() {
    echo "Checking PostgreSQL connection..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up - executing command"
}

# Function to run Django/Daphne server
run_server() {
    echo "Running migrations..."
    python manage.py migrate

    echo "Installing or upgrading daphne if not present..."
    pip install --upgrade daphne channels

    echo "Starting Daphne ASGI server..."
    daphne -b 0.0.0.0 -p 8000 config.asgi:application
}

# Main execution
check_postgres
run_server
