#!/bin/bash
# 🚀 NURVA AI - AUTO DEPLOYMENT SCRIPT
# Run on server: sudo bash deploy.sh

set -e

echo "🚀 Starting Nurva AI Deployment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo bash deploy.sh)"
    exit 1
fi

DOMAIN="nurvaai.com"
APP_DIR="/var/www/nurva"
EMAIL="admin@nurvaai.com"

echo "📋 Configuration:"
echo "  Domain: $DOMAIN"
echo "  App Directory: $APP_DIR"
echo "  Email: $EMAIL"
echo ""

# STEP 1: Install System Dependencies
echo "📦 Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx

# STEP 2: Setup App Directory
echo "📁 Setting up application directory..."
if [ ! -d "$APP_DIR" ]; then
    mkdir -p $APP_DIR
fi

cd $APP_DIR

# STEP 3: Create Virtual Environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
/var/www/nurva/venv/bin/pip install --upgrade pip
/var/www/nurva/venv/bin/pip install -r requirements.txt

# STEP 4: Django Setup
echo "⚙️  Setting up Django..."
python manage.py collectstatic --noinput
python manage.py migrate

# STEP 5: Create Gunicorn Service
echo "🔌 Configuring Gunicorn..."
cp nurva.service /etc/systemd/system/nurva.service

# Enable and start Gunicorn
systemctl daemon-reload
systemctl enable nurva.service
systemctl start nurva

# STEP 6: Configure Nginx
echo "🌐 Configuring Nginx..."
cp nginx_config.conf /etc/nginx/sites-available/nurva
ln -sf /etc/nginx/sites-available/nurva /etc/nginx/sites-enabled/
nginx -t
systemctl enable nginx
systemctl start nginx

# STEP 7: SSL Certificate
echo "🔒 Installing SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m $EMAIL

# STEP 8: Set Permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data $APP_DIR
chmod 600 $APP_DIR/.env
chmod 755 $APP_DIR

# STEP 9: Create backup directory
mkdir -p $APP_DIR/backups
chown -R www-data:www-data $APP_DIR/backups

# STEP 10: Verify
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🔍 Verification:"
systemctl status nurva --no-pager | head -n 3
echo ""
systemctl status nginx --no-pager | head -n 3
echo ""
echo "🌐 Visit: https://$DOMAIN"
echo ""
echo "📋 Next steps:"
echo "1. Create superuser: python manage.py createsuperuser"
echo "2. Check logs: sudo journalctl -u nurva -f"
echo "3. View payment logs: tail -f /var/www/nurva/payments.log"
echo ""
