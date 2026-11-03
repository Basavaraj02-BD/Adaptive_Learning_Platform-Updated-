#!/usr/bin/env bash
echo "Building project on Vercel..."

# Install dependencies with --break-system-packages for modern Vercel/uv Linux containers
python3 -m pip install -r requirements.txt --break-system-packages || python3 -m pip install -r requirements.txt

# Ensure output directory exists
mkdir -p staticfiles_build/static

# Collect static files into STATIC_ROOT (staticfiles_build/static)
python3 manage.py collectstatic --no-input --clear

# Run database migrations if DATABASE_URL is configured
if [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL detected, running migrations..."
    python3 manage.py migrate --no-input || echo "Migrations skipped or failed, continuing..."
fi

echo "Build completed successfully!"
