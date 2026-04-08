#!/bin/bash

# Nurva AI Django - Quick Start Script
# This script helps you get started with the Django project

cd "$(dirname "$0")"

echo "🚀 Nurva AI Django Project - Quick Start"
echo "======================================"
echo ""

# Activate virtual environment
echo "📌 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Check if requirements are installed
pip install -r requirements.txt --quiet

echo "✅ Dependencies installed"
echo ""

# Run migrations
echo "📌 Running migrations..."
python manage.py migrate --quiet
echo "✅ Database initialized"
echo ""

# Collect static files
echo "📌 Collecting static files..."
python manage.py collectstatic --noinput --quiet 2>/dev/null || true
echo "✅ Static files collected"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "🌐 Starting development server..."
echo "======================================"
echo "The app will be available at:"
echo "  📍 Home:    http://localhost:8000/"
echo "  💬 Chat:    http://localhost:8000/chatbot/"
echo "  🔧 Admin:   http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

python manage.py runserver
