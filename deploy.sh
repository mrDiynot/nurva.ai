#!/bin/bash
# 🚀 NURVA AI - AUTO DEPLOYMENT SCRIPT
# Run on server: bash deploy.sh

set -e

echo "🚀 Starting Nurva AI Deployment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo)"
    exit 1
fi

DOMAIN="nurvaai.com"
APP_DIR="/var/www/nurva"
REPO_URL=""  # ADD YOUR GIT REPO URL

# STEP 1: Install System Dependencies
echo "📦 Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx

# STEP 2: Clone Repository
echo "📥 Cloning repository..."
if [ ! -d "$APP_DIR" ]; then
    mkdir -p /var/www
    git clone $REPO_URL $APP_DIR
else
    cd $APP_DIR
    git pull origin main
fi

cd $APP_DIR

# STEP 3: Create Virtual Environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# STEP 4: Django Setup
echo "⚙️  Setting up Django..."
python manage.py collectstatic --noinput
python manage.py migrate

# STEP 5: Create Gunicorn Socket
echo "🔌 Configuring Gunicorn..."
cat > /etc/systemd/system/gunicorn.socket << EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

# STEP 6: Create Gunicorn Service
cat > /etc/systemd/system/gunicorn.service << EOF
[Unit]
Description=gunicorn daemon for nurva
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn \\
    --workers 4 \\
    --bind unix:/run/gunicorn.sock \\
    nurva_config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Gunicorn
systemctl daemon-reload
systemctl enable gunicorn.socket gunicorn.service
systemctl start gunicorn

# STEP 7: Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/nurva << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $APP_DIR/staticfiles/;
    }
}
EOF

ln -sf /etc/nginx/sites-available/nurva /etc/nginx/sites-enabled/
nginx -t
systemctl enable nginx
systemctl start nginx

# STEP 8: SSL Certificate
echo "🔒 Installing SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

# STEP 9: Set Permissions
echo "🔐 Setting permissions..."
chmod 600 $APP_DIR/.env
chown -R www-data:www-data $APP_DIR

# STEP 10: Verify
echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🔍 Verification:"
systemctl status gunicorn --no-pager | head -n 3
systemctl status nginx --no-pager | head -n 3
echo ""
echo "🌐 Visit: https://$DOMAIN"
echo ""
