# Nurva AI Django Project

A Django application for the Nurva AI chat interface with beautiful, modern styling.

## Project Structure

```
nurva_project/
├── venv/                          # Virtual environment
├── nurva_config/                  # Main Django project configuration
│   ├── settings.py               # Django settings (loads from .env)
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py                   # ASGI configuration
│   └── wsgi.py                   # WSGI configuration
├── chat/                          # Main Django app
│   ├── templates/
│   │   └── chat/
│   │       ├── home.html         # Home page
│   │       └── chatbot.html      # Chatbot interface
│   ├── views.py                  # View logic
│   ├── urls.py                   # Chat app URL routing
│   ├── models.py                 # Database models
│   └── admin.py                  # Django admin configuration
├── manage.py                     # Django management script
├── .env                          # Environment variables (keep secret!)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Setup Instructions

### 1. Activate Virtual Environment

```bash
cd /Users/sami/Desktop/Nurva\ AI/nurva_project
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

The `.env` file is already configured with default settings:
- `DEBUG=True` (Change to False in production)
- `SECRET_KEY` (Change in production!)
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- `APP_NAME=Nurva AI`

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The app will be available at:
- Home Page: `http://localhost:8000/`
- Chatbot: `http://localhost:8000/chatbot/`
- Admin Panel: `http://localhost:8000/admin/`

## Available Routes

| URL | View | Purpose |
|-----|------|---------|
| `/` | HomeView | Main landing page |
| `/chatbot/` | ChatbotView | Chatbot interface |
| `/admin/` | Django Admin | Admin panel |

## Configuration

### Environment Variables (.env)

```
# Django Settings
DEBUG=True                        # Set to False in production
SECRET_KEY=your-secret-key-here   # Generate a new key for production
ALLOWED_HOSTS=localhost,127.0.0.1 # Add your domain in production

# App Settings
APP_NAME=Nurva AI                 # Used in templates
```

## Production Deployment

Before deploying to production:

1. **Change SECRET_KEY**: Generate a new secret key in `settings.py`
2. **Set DEBUG=False**: In `.env` file
3. **Update ALLOWED_HOSTS**: Add your domain
4. **Use a production database**: PostgreSQL or MySQL instead of SQLite
5. **Collect static files**: `python manage.py collectstatic`
6. **Use a WSGI server**: Gunicorn, uWSGI, etc.

## Common Commands

```bash
# Create new app
python manage.py startapp app_name

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Django shell
python manage.py shell
```

## HTML Files

Your HTML files have been moved to:
- `chat/templates/chat/home.html` - Home page template
- `chat/templates/chat/chatbot.html` - Chatbot interface template

These are fully functional with all original styling intact. You can modify them as needed.

## Support

For Django documentation: https://docs.djangoproject.com/
For environment setup help: https://python-dotenv.readthedocs.io/
