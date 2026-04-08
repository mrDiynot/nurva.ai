# 🚀 NURVA AI - PRODUCTION DEPLOYMENT GUIDE

## Server Access
```
SSH: ssh root@62.171.166.40
Domain: nurvaai.com
```

---

## STEP 1: Connect to Server
```bash
ssh root@62.171.166.40
```

---

## STEP 2: Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python & dependencies
apt install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx

# Install Gunicorn (production server)
pip install gunicorn
```

---

## STEP 3: Clone & Setup App
```bash
cd /var/www
git clone <your-repo-url> nurva
cd nurva

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy .env file (from your local machine, use scp)
# Locally: scp .env root@62.171.166.40:/var/www/nurva/
```

---

## STEP 4: Django Setup
```bash
cd /var/www/nurva
source venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

---

## STEP 5: Configure Gunicorn
```bash
# Create gunicorn socket file
sudo nano /etc/systemd/system/gunicorn.socket
```

Paste:
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

---

## STEP 6: Create Gunicorn Service
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste:
```ini
[Unit]
Description=gunicorn daemon for nurva
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/nurva
ExecStart=/var/www/nurva/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/gunicorn.sock \
    nurva_config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable gunicorn.socket gunicorn.service
sudo systemctl start gunicorn
```

---

## STEP 7: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/nurva
```

Paste:
```nginx
server {
    listen 80;
    server_name nurvaai.com www.nurvaai.com;

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/nurva/staticfiles/;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/nurva /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl start nginx
```

---

## STEP 8: SSL Certificate (Let's Encrypt)
```bash
sudo certbot --nginx -d nurvaai.com -d www.nurvaai.com
```

**Answer prompts:**
- Email: your-email@domain.com
- Agree to terms
- Share email: Y/N (your choice)
- Skip redirect for now, then choose redirect to HTTPS after first test

---

## STEP 9: Update Django Settings for HTTPS
Once SSL is installed, SSH in and update .env:

```bash
ssh root@62.171.166.40
cd /var/www/nurva

# Edit .env - set these in a new PRODUCTION section
nano .env
```

Update in `.env`:
```
# Change to production
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Update in `nurva_config/settings.py` (on server):
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

---

## STEP 10: Auto-Renew SSL Certificate
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## VERIFICATION
```bash
# Check if app is running
sudo systemctl status gunicorn

# Check Nginx
sudo systemctl status nginx

# Visit website
# http://nurvaai.com (should redirect to https)
# https://nurvaai.com
```

---

## Troubleshooting
```bash
# View logs
sudo journalctl -u gunicorn -n 50
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## Secure Your Keys
```bash
# Make sure .env is not readable by others
chmod 600 /var/www/nurva/.env

# Remove keys from git history (if present)
git filter-branch --force --index-filter "git rm --cached -r .env" --prune-empty --tag-name-filter cat -- --all
```

---

✅ **App is now deployed with SSL!**
