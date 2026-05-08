#!/bin/bash
# ═══════════════════════════════════════════
#  AdaptLearn — Quick Setup Script
#  Usage: bash setup.sh
# ═══════════════════════════════════════════

set -e

echo ""
echo "🧠  AdaptLearn Setup"
echo "━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Virtual environment
if [ ! -d "venv" ]; then
  echo "▸ Creating virtual environment..."
  python -m venv venv
fi

# 2. Activate
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi
echo "✓ Virtual environment activated"

# 3. Install dependencies
echo "▸ Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# 4. Environment file
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "✓ .env created (edit it to add your API keys)"
fi

# 5. Migrations
echo "▸ Running migrations..."
python manage.py makemigrations learning --verbosity 0
python manage.py migrate --verbosity 0
echo "✓ Database migrated"

# 6. Seed data
echo "▸ Seeding demo data..."
python manage.py seed_data
echo "✓ Demo data seeded"

# 7. Collect static (optional)
# python manage.py collectstatic --noinput -v 0

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅  All done! Start with:"
echo ""
echo "   python manage.py runserver"
echo ""
echo "   Open: http://127.0.0.1:8000/"
echo ""
echo "   Admin login:  admin / admin123"
echo "   Admin URL:    http://127.0.0.1:8000/admin-login/"
echo "   Django admin: http://127.0.0.1:8000/admin/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
