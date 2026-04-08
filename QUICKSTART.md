# 🚀 QUICK START GUIDE

## Installation Complete! ✅

Your Django project is fully set up with environment configuration and HTML templates integrated.

### Get Started in 30 Seconds

#### Option 1: Using the Quick Start Script
```bash
cd "/Users/sami/Desktop/Nurva AI/nurva_project"
chmod +x run.sh
./run.sh
```

#### Option 2: Manual Startup
```bash
cd "/Users/sami/Desktop/Nurva AI/nurva_project"
source venv/bin/activate
python manage.py runserver
```

### Access the Application

Once the server is running, visit:
- **Home Page**: http://localhost:8000/
- **Chatbot**: http://localhost:8000/chatbot/
- **Admin Panel**: http://localhost:8000/admin/ (create user first)

---

## What Was Set Up

✅ **Virtual Environment (venv/)**
- Isolated Python environment for this project
- All dependencies installed inside

✅ **Django Project Structure**
- `nurva_config/` - Main project configuration
- `chat/` - App with your HTML templates
- Standard Django folder organization

✅ **HTML Templates Moved**
- `home.html` → `chat/templates/chat/home.html` (2.1 MB)
- `chatbot.html` → `chat/templates/chat/chatbot.html` (384 KB)
- ✨ All original code preserved!

✅ **Environment Configuration**
- `.env` file with default settings
- Loads settings using python-dotenv
- Easy to manage different environments (dev, prod)

✅ **Database**
- SQLite3 database initialized (db.sqlite3)
- All migrations applied
- Ready for development

---

## File Structure

```
/Users/sami/Desktop/Nurva AI/nurva_project/
├── venv/                    # Python virtual environment
├── chat/
│   ├── templates/
│   │   └── chat/
│   │       ├── home.html          # ⭐ Your home page
│   │       └── chatbot.html       # ⭐ Your chatbot page
│   ├── views.py             # Handles page rendering
│   ├── urls.py              # Routes for chat app
│   ├── models.py            # Database models (empty)
│   └── admin.py             # Django admin config
├── nurva_config/
│   ├── settings.py          # Django settings (loads .env)
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # Production server config
│   └── asgi.py              # Async worker config
├── manage.py                # Django command tool
├── db.sqlite3               # Development database
├── .env                     # Environment variables 🔐
├── requirements.txt         # Python dependencies
├── .gitignore               # Git configuration
├── run.sh                   # Quick start script
├── README.md                # Full documentation
└── QUICKSTART.md            # This file
```

---

## Environment Variables (.env)

Located at: `/Users/sami/Desktop/Nurva AI/nurva_project/.env`

```
DEBUG=True                           # Change to False in production
SECRET_KEY=django-insecure-...       # Generate new key for production
ALLOWED_HOSTS=localhost,127.0.0.1    # Add your domain in production
DATABASE_URL=sqlite:///db.sqlite3    # Current database
APP_NAME=Nurva AI                    # Used in templates
```

---

## Common Commands

### Activate Virtual Environment
```bash
cd "/Users/sami/Desktop/Nurva AI/nurva_project"
source venv/bin/activate
```

### Run Development Server
```bash
python manage.py runserver
```

### Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### Make Database Changes
```bash
python manage.py makemigrations
python manage.py migrate
```

### Access Django Shell
```bash
python manage.py shell
```

### Collect Static Files (Production)
```bash
python manage.py collectstatic
```

---

## Deactivate Virtual Environment

When you're done working on the project:
```bash
deactivate
```

---

## Troubleshooting

### Port 8000 Already In Use
```bash
# Run on different port
python manage.py runserver 8001
```

### Database Issues
```bash
# Reset database (dev only!)
rm db.sqlite3
python manage.py migrate
```

### Permission Denied on run.sh
```bash
chmod +x run.sh
```

### Missing Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

1. ✅ Start the development server
2. Visit http://localhost:8000/ to see your home page
3. Create a superuser with `python manage.py createsuperuser`
4. Access admin panel at http://localhost:8000/admin/
5. Customize the HTML templates in `chat/templates/chat/`
6. Add more URLs and views as needed

---

## Need Help?

- **Django Docs**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Python Dotenv**: https://python-dotenv.readthedocs.io/

---

**Happy coding! 🎉**
