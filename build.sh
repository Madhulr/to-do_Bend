#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create static directory if it doesn't exist
mkdir -p static

# Print database configuration for debugging
echo "Database URL: $DATABASE_URL"
echo "Database Name: $DATABASE_NAME"
echo "Database User: $DATABASE_USER"
echo "Database Host: $DATABASE_HOST"

# Force remove any existing migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Create fresh migrations
python manage.py makemigrations auth
python manage.py makemigrations admin
python manage.py makemigrations contenttypes
python manage.py makemigrations sessions
python manage.py makemigrations todos

# Apply migrations with force
python manage.py migrate auth --noinput
python manage.py migrate admin --noinput
python manage.py migrate contenttypes --noinput
python manage.py migrate sessions --noinput
python manage.py migrate todos --noinput
python manage.py migrate --noinput

# Create superuser if it doesn't exist
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-admin}

python manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
END

# Collect static files
python manage.py collectstatic --no-input --clear

# Ensure static files are properly set up
mkdir -p staticfiles/admin
python manage.py collectstatic --no-input

# Create necessary directories
mkdir -p staticfiles/admin/css
mkdir -p staticfiles/admin/js

# Copy admin static files if they don't exist
if [ ! -f "staticfiles/admin/css/login.css" ]; then
    cp -r venv/lib/python*/site-packages/django/contrib/admin/static/admin/* staticfiles/admin/
fi 