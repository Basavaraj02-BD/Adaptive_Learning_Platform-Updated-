#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

echo "Seeding demo courses..."
python manage.py seed_courses || echo "WARNING: seed_courses failed or already seeded, continuing..."

echo "Seeding exam questions..."
python manage.py seed_exam_questions || echo "WARNING: seed_exam_questions failed or already seeded, continuing..."

echo "Build complete!"
