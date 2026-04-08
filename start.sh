#!/bin/bash

# Nurva AI Django - Full Setup & Startup Script
# This script sets up and launches the complete Django application

set -e

echo "🚀 Nurva AI Chatbot - Full Setup & Launch"
echo "=========================================="
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📌 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📌 Installing dependencies..."
pip install -r requirements.txt --quiet 2>/dev/null || true

# Run migrations
echo "📌 Applying database migrations..."
python manage.py migrate --quiet

# Initialize agents if needed
echo "📌 Initializing agents..."
python setup_db.py 2>/dev/null || true

# Clear old sessions
echo "📌 Clearing old sessions..."
python manage.py clearsessions --quiet 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Database Status:"
echo "   Database: SQLite3 (db.sqlite3)"
python manage.py dbshell --stdin <<EOF 2>/dev/null || true
SELECT COUNT(*) as agents FROM chat_agent;
.exit
EOF

echo ""
echo "🌐 Starting Django Development Server..."
echo "=========================================="
echo ""
echo "✦ The app is now running at:"
echo "   🏠 Home Page:      http://localhost:8000/"
echo "   💬 Chatbot:        http://localhost:8000/chatbot/"
echo "   🔧 Admin Panel:    http://localhost:8000/admin/"
echo ""
echo "📝 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "💳 Payment Password:"
echo "   nurva2024"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Start development server
python manage.py runserver 0.0.0.0:8000
