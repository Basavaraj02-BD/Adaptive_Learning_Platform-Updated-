#!/usr/bin/env bash
echo "Building project on Vercel..."

# Install dependencies
python3 -m pip install -r requirements.txt

# Collect static files into STATIC_ROOT (staticfiles)
python3 manage.py collectstatic --no-input --clear

# Run database migrations if DATABASE_URL is configured
if [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL detected, running migrations..."
    python3 manage.py migrate --no-input || echo "Migrations skipped or failed, continuing..."
fi

echo "Build completed successfully!"
