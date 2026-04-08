# Production Deployment Guide
# Nurva AI Application - nurvaai.com

## Server Details
- **Public IP:** 62.171.166.40
- **Domain:** www.nurvaai.com / nurvaai.com
- **SSL:** Let's Encrypt (Certbot)
- **Framework:** Django 6.0.3
- **Database:** SQLite (upgradeable to PostgreSQL)

## Prerequisites
1. Ubuntu/Debian server with root access
2. Python 3.9+
3. Domain DNS configured (A record pointing to 62.171.166.40)
4. Git repository access

## Deployment Steps

### 1. Upload Files to Server
```bash
# On your local machine
cd "/Users/sami/Desktop/Nurva AI/nurva_project"
tar -czf nurva_app.tar.gz --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' --exclude='db.sqlite3' --exclude='.git' .

# Upload to server
scp nurva_app.tar.gz root@62.171.166.40:/home/
```

### 2. Setup on Server
```bash
# SSH into server
ssh root@62.171.166.40

# Extract files
cd /var/www
mkdir -p nurva
cd nurva
tar -xzf /home/nurva_app.tar.gz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 3. Configure Files
Edit the following files with correct paths:
```bash
# Update configuration files
nano .env                      # Update SECRET_KEY and database settings
nano nurva_config/settings.py  # Verify ALLOWED_HOSTS and security settings
nano nginx_config.conf         # Already provided (verify paths)
nano nurva.service             # Already provided (verify paths)
nano deploy.sh                 # Update APP_DIR, DOMAIN, EMAIL if needed
```

### 4. Run Deployment Script
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### 5. Configure DNS
Add these DNS records at your domain registrar:

```
Type    Name    Value           TTL
A       @       62.171.166.40   3600
A       www     62.171.166.40   3600
```

## Manual Configuration (if needed)

### Gunicorn Service
```bash
sudo cp nurva.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nurva
sudo systemctl start nurva
```

### Nginx Configuration
```bash
sudo cp nginx_config.conf /etc/nginx/sites-available/nurva
sudo ln -s /etc/nginx/sites-available/nurva /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Certbot)
```bash
sudo certbot --nginx -d www.nurvaai.com -d nurvaai.com
```

## Maintenance Commands

### Application Management
```bash
# Restart application
sudo systemctl restart nurva

# View logs
sudo journalctl -u nurva -f

# Stop application
sudo systemctl stop nurva

# Check status
sudo systemctl status nurva

# View recent logs
sudo journalctl -u nurva -n 50
```

### Nginx Management
```bash
# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Test configuration
sudo nginx -t

# View Nginx errors
sudo tail -f /var/log/nginx/error.log
```

### SSL Certificate Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Force renewal
sudo certbot renew --force-renewal

# View certificates
sudo certbot certificates
```

### Database Management
```bash
cd /var/www/nurva
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Access Django shell
python manage.py shell
```

### Update Application
```bash
cd /var/www/nurva
source venv/bin/activate

# Pull latest changes (if using git)
git pull origin main

# Install new/updated dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart nurva
```

### Payment & Subscription Management
```bash
cd /var/www/nurva
source venv/bin/activate
python manage.py shell

# View all payments
from chat.models import Payment
Payment.objects.all()

# View user subscriptions
from chat.models import Subscription, User
user = User.objects.get(username='username')
user.subscription

# Check payment logs
exit()
tail -f /var/www/nurva/payments.log
```

## File Locations

### Application Files
- App Directory: `/var/www/nurva`
- Virtual Environment: `/var/www/nurva/venv`
- Database: `/var/www/nurva/db.sqlite3`
- Static Files: `/var/www/nurva/staticfiles`
- Templates: `/var/www/nurva/chat/templates`
- Payment Logs: `/var/www/nurva/payments.log`
- Media Files: `/var/www/nurva/media` (if needed)

### Configuration Files
- Nginx: `/etc/nginx/sites-available/nurva`
- Systemd: `/etc/systemd/system/nurva.service`
- Gunicorn: `/var/www/nurva/gunicorn_config.py`
- Django Settings: `/var/www/nurva/nurva_config/settings.py`
- Environment: `/var/www/nurva/.env` (KEEP SECURE)

### Log Files
- Application Logs: `sudo journalctl -u nurva -f`
- Application (payments): `/var/www/nurva/payments.log`
- Gunicorn/WSGI: `/var/log/gunicorn/nurva.log` (if configured)
- Nginx Access: `/var/log/nginx/access.log`
- Nginx Error: `/var/log/nginx/error.log`
- Systemd: `sudo journalctl -u nurva`

### SSL Certificates
- Certificate: `/etc/letsencrypt/live/www.nurvaai.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/www.nurvaai.com/privkey.pem`

## Troubleshooting

### Application won't start
```bash
# Check Systemd logs
sudo journalctl -u nurva -n 50

# Check status
sudo systemctl status nurva

# Check for Python errors
cd /var/www/nurva
source venv/bin/activate
python manage.py check
```

### 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo systemctl status nurva

# Check Gunicorn socket
ls -la /run/gunicorn.sock

# Restart Gunicorn
sudo systemctl restart nurva
```

### Static files not loading
```bash
cd /var/www/nurva
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Database locked errors
```bash
# Check for lock files
ls -la /var/www/nurva/db.sqlite3*

# Remove lock if needed
rm /var/www/nurva/db.sqlite3-shm /var/www/nurva/db.sqlite3-wal 2>/dev/null

# Restart application
sudo systemctl restart nurva
```

### Stripe payments not working
```bash
# Check payment logs
tail -f /var/www/nurva/payments.log

# Verify Stripe keys in .env
nano /var/www/nurva/.env | grep STRIPE

# Test Stripe connection
cd /var/www/nurva
source venv/bin/activate
python manage.py shell
import stripe
import os
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
customers = stripe.Customer.list(limit=1)
print(customers)
exit()
```

### SSL certificate issues
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/www.nurvaai.com/fullchain.pem -text -noout
```

### Permission issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/nurva

# Fix permissions
sudo chmod -R 755 /var/www/nurva
sudo chmod 600 /var/www/nurva/.env
```

### Out of memory / High CPU
```bash
# Check running processes
top

# Check Gunicorn workers
ps aux | grep gunicorn

# Reduce workers if needed (edit nurva.service)
# Change --workers 4 to --workers 2
sudo systemctl edit nurva
sudo systemctl restart nurva
```

## Security Checklist
- [x] DEBUG = False in .env
- [x] Strong SECRET_KEY generated (50+ chars)
- [x] ALLOWED_HOSTS configured for domain
- [x] CSRF_TRUSTED_ORIGINS set
- [x] SSL certificate installed
- [x] HTTPS redirect enabled
- [x] SECURE_SSL_REDIRECT = True (when HTTPS ready)
- [x] SESSION_COOKIE_SECURE = True
- [x] CSRF_COOKIE_SECURE = True
- [x] .env permissions: chmod 600
- [x] Database backups configured
- [x] Stripe keys are LIVE (not test)
- [x] Firewall enabled (UFW)
- [x] Only ports 80, 443, 22 open
- [x] SSH key-based auth enabled
- [x] Regular system updates

## Backup Strategy

### Manual Backup
```bash
# Backup database
cd /var/www/nurva
mkdir -p backups
cp db.sqlite3 backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Backup media files (if any)
tar -czf backups/media_$(date +%Y%m%d_%H%M%S).tar.gz media/ 2>/dev/null || true

# Backup .env (keep separate and secure)
cp .env backups/.env_$(date +%Y%m%d_%H%M%S)
chmod 600 backups/.env*
```

### Automated Backup (Cron)
```bash
# Create backup script
sudo nano /usr/local/bin/nurva_backup.sh
```

Paste:
```bash
#!/bin/bash
BACKUP_DIR="/var/www/nurva/backups"
DB_FILE="/var/www/nurva/db.sqlite3"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database with timestamp
cp $DB_FILE $BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sqlite3" -mtime +30 -delete

# Create tar of entire app (excluding venv)
cd /var/www
tar -czf $BACKUP_DIR/nurva_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    --exclude='nurva/venv' \
    --exclude='nurva/staticfiles/__pycache__' \
    nurva/

# Keep only last 5 backups
ls -t $BACKUP_DIR/nurva_backup_*.tar.gz | tail -n +6 | xargs rm -f
```

Make executable and add to cron:
```bash
sudo chmod +x /usr/local/bin/nurva_backup.sh

# Add to crontab (runs daily at 2 AM)
sudo crontab -e
# Add line: 0 2 * * * /usr/local/bin/nurva_backup.sh
```

## Monitoring

### Health Check Script
```bash
# Create monitoring script
sudo nano /usr/local/bin/check_nurva.sh
```

Paste:
```bash
#!/bin/bash
echo "=== Nurva AI Health Check ==="
echo ""

# Check if app is running
echo "1. Application Status:"
sudo systemctl status nurva --no-pager | head -n 3

echo ""
echo "2. Nginx Status:"
sudo systemctl status nginx --no-pager | head -n 3

echo ""
echo "3. Recent Errors (last 5):"
sudo journalctl -u nurva -n 5 --no-pager

echo ""
echo "4. Disk Usage:"
df -h /var/www/nurva | tail -n 1

echo ""
echo "5. Certificate Status:"
sudo certbot certificates | grep nurva

echo ""
echo "=== End Health Check ==="
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/check_nurva.sh

# Run anytime
check_nurva.sh
```

## Performance Optimization

### Database Optimization
```bash
# For larger deployments, upgrade to PostgreSQL
# Edit .env to use PostgreSQL instead of SQLite
# This is recommended for production with multiple users
```

### Static Files CDN (Optional)
```bash
# Configure CloudFlare or similar
# Point to nurva.staticfiles.* subdomain
# Reduces server load for assets
```

### Caching Headers
```bash
# Already configured in nginx_config.conf
# Nginx caches static files for 1 year
# Browser cache headers configured for best performance
```

## Emergency Recovery

### Restore from Backup
```bash
# Stop application
sudo systemctl stop nurva

# Restore database
cd /var/www/nurva
cp db.sqlite3 db.sqlite3.broken
cp backups/db_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

# Restart application
sudo systemctl start nurva
```

### Emergency Maintenance Mode
```bash
# Put app in maintenance mode
sudo nano /etc/nginx/sites-available/nurva

# Add before proxy_pass:
# return 503;

# Reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# Perform maintenance
# ...

# Restore by removing the return 503 line
sudo systemctl reload nginx
```

## Stripe Integration Notes

### Live vs Test Mode
- **Test Keys:** Start with `pk_test_` and `sk_test_`
- **Live Keys:** Start with `pk_live_` and `sk_live_`
- Currently configured with LIVE keys in production

### Testing Payments
```bash
# View all payments in database
cd /var/www/nurva
source venv/bin/activate
python manage.py shell

from chat.models import Payment
for p in Payment.objects.all():
    print(f"{p.user.username}: ${p.amount} ({p.status})")
    
exit()
```

### Webhook Testing (Optional)
```bash
# If enabling webhooks in future:
stripe listen --forward-to https://nurvaai.com/webhook/stripe/
# Copy webhook signing secret to .env
```

## Support & Resources

### Common Issues
1. **502 Gateway Error** → Check Gunicorn: `sudo systemctl status nurva`
2. **Static files missing** → Run: `python manage.py collectstatic --noinput`
3. **Payment errors** → Check: `tail -f /var/www/nurva/payments.log`
4. **SSL errors** → Verify: `sudo certbot certificates`

### Log Files to Check
```bash
# Application
sudo journalctl -u nurva -f

# Nginx
sudo tail -f /var/log/nginx/error.log

# Payments (app-specific)
tail -f /var/www/nurva/payments.log

# System
sudo dmesg | tail -n 20
```

### Contact & Debugging
- **Django Debug:** Set `DEBUG=True` in .env (development only!)
- **Error Email:** Configure EMAIL_BACKEND in settings.py for alerts
- **Sentry Integration:** Optional error tracking service

---

✅ **Deployment Complete!**
Visit: https://www.nurvaai.com
