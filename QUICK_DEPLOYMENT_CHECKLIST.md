# 🚀 NURVA AI - QUICK DEPLOYMENT CHECKLIST

## ✅ Pre-Deployment (On Your Local Machine)

### 1. Update Production Variables
```bash
cd "/Users/sami/Desktop/Nurva AI/nurva_project"

# Update .env
nano .env

# Ensure these are set:
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=nurvaai.com,www.nurvaai.com,localhost,127.0.0.1
STRIPE_SECRET_KEY=sk_live_... (LIVE key)
STRIPE_PUBLISHABLE_KEY=pk_live_... (LIVE key)
ANTHROPIC_API_KEY=sk-ant-...
```

### 2. Test Locally
```bash
# Test configuration
python manage.py check

# Test static files
python manage.py collectstatic --noinput

# Test migrations
python manage.py migrate

# Create test user if needed
python manage.py createsuperuser
```

### 3. Commit All Changes
```bash
git add .
git commit -m "Production deployment - nurvaai.com"
git push origin main
```

### 4. Verify All Config Files Exist
```bash
ls -la | grep -E "deploy|nginx|service|PRODUCTION"

# Should see:
# - deploy_production.sh
# - nginx_config.conf
# - nurva.service
# - PRODUCTION_DEPLOYMENT.md
# - requirements.txt
```

---

## ✅ Deployment Day (On Server - 62.171.166.40)

### STEP 1: SSH into Server
```bash
ssh root@62.171.166.40
```

### STEP 2: Prepare Application
```bash
# Create app directory
mkdir -p /var/www/nurva
cd /var/www/nurva

# Copy files from local machine (do this locally):
# scp -r /Users/sami/Desktop/Nurva\ AI/nurva_project/* root@62.171.166.40:/var/www/nurva/

# OR clone from Git (if using Git):
# git clone https://github.com/YOUR_REPO.git /var/www/nurva
```

### STEP 3: Verify Config Files
```bash
cd /var/www/nurva
ls -la | grep -E "deploy|nginx|service|PRODUCTION"

# Should have all config files
```

### STEP 4: Run Deployment Script
```bash
chmod +x deploy_production.sh
sudo bash deploy_production.sh
```

### STEP 5: Check Deployment Status
```bash
# Verify all services running
sudo systemctl status nurva
sudo systemctl status nginx

# Check for errors
sudo journalctl -u nurva -n 20

# View payment logs
tail -f /var/www/nurva/payments.log
```

### STEP 6: Test Website
```bash
# From your laptop
curl https://nurvaai.com
# Should return HTML (not 502 error)

# Visit in browser:
https://www.nurvaai.com
```

---

## ✅ Post-Deployment (On Server)

### Create Admin User
```bash
cd /var/www/nurva
source venv/bin/activate
python manage.py createsuperuser

# Username: admin
# Email: your-email@nurvaai.com
# Password: (strong password)
```

### Verify Database
```bash
# Check users
python manage.py shell
from django.contrib.auth.models import User
print(User.objects.all())
exit()
```

### Monitor Service
```bash
# Start monitoring services
sudo journalctl -u nurva -f
```

### Configure Domain DNS
At your domain registrar (GoDaddy, Namecheap, etc.):

```
Type    Name    Value           TTL
A       @       62.171.166.40   3600
A       www     62.171.166.40   3600
```

Wait 24-48 hours for DNS propagation.

---

## 🔐 Security Checklist - BEFORE GOING LIVE

- [ ] `DEBUG=False` in .env
- [ ] Strong `SECRET_KEY` (50+ characters, random)
- [ ] STRIPE uses LIVE keys (sk_live_..., not sk_test_...)
- [ ] `.env` has permissions 600: `chmod 600 /var/www/nurva/.env`
- [ ] SSL certificate installed and working
- [ ] HTTPS redirects (visit http://nurvaai.com should redirect to https)
- [ ] Admin password is strong
- [ ] Database backups configured
- [ ] Firewall enabled (UFW)
- [ ] SSH key-based auth enabled (password SSH disabled)

---

## 🚨 Troubleshooting During Deployment

### Can't SSH into server
```bash
# Check SSH connection
ssh -vvv root@62.171.166.40

# Verify IP is correct
ping 62.171.166.40

# Check if SSH port is open
telnet 62.171.166.40 22
```

### 502 Bad Gateway
```bash
# Check Gunicorn status
sudo systemctl status nurva

# Check if socket exists
ls -la /run/gunicorn.sock

# Check logs
sudo journalctl -u nurva -n 50
```

### Static files not loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check permissions
ls -la /var/www/nurva/staticfiles/

# Restart Nginx
sudo systemctl restart nginx
```

### SSL Certificate Error
```bash
# Check certificate
sudo certbot certificates

# Verify DNS is set correctly
nslookup nurvaai.com
dig nurvaai.com

# Try renewal
sudo certbot renew --force-renewal
```

### Payment not working
```bash
# Check Stripe keys
grep STRIPE /var/www/nurva/.env

# Verify connection
cd /var/www/nurva
source venv/bin/activate
python manage.py shell
import stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.Customer.list(limit=1)
exit()
```

---

## 📊 Monitoring Commands

After deployment, use these to monitor your app:

```bash
# Check all services
sudo systemctl status nurva nginx

# View application logs (real-time)
sudo journalctl -u nurva -f

# View payment logs
tail -f /var/www/nurva/payments.log

# Check disk space
df -h

# Check memory
free -h

# Test website availability
curl https://nurvaai.com

# Check SSL certificate expiry
sudo certbot certificates
```

---

## 💾 Backup Configuration

Add to crontab for automatic daily backups:

```bash
sudo crontab -e

# Add this line:
0 2 * * * cp /var/www/nurva/db.sqlite3 /var/www/nurva/backups/db_$(date +\%Y\%m\%d_\%H\%M\%S).sqlite3
```

---

## 📞 Emergency Contacts

- **Server:** root@62.171.166.40
- **Domain:** nurvaai.com
- **Stripe Support:** https://support.stripe.com
- **Let's Encrypt Help:** https://letsencrypt.org/support/

---

## ✅ Success Indicators

After deployment, you should see:

✅ Website loads at https://www.nurvaai.com
✅ HTTPS padlock is green
✅ Admin login works at https://www.nurvaai.com/admin
✅ Payments can be tested with Stripe test cards
✅ No errors in `sudo journalctl -u nurva`
✅ Static files load correctly (CSS, JS, images)
✅ Free tier works (3 messages before paywall)
✅ Paid users can chat unlimited

---

## 🎉 Deployment Complete!

Your Nurva AI app is now live at **https://www.nurvaai.com** 🚀

Keep monitoring the logs and enjoy your production deployment!
