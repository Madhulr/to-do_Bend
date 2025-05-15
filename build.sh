#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create static directory if it doesn't exist
mkdir -p static

# Print database configuration for debugging
echo "Database URL: $DATABASE_URL"

# Drop and recreate the database
python manage.py dbshell << END
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
END

# Create fresh migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-admin}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-admin}

python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL

# Set superuser password
python manage.py shell << END
from django.contrib.auth.models import User
user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME')
user.set_password('$DJANGO_SUPERUSER_PASSWORD')
user.save()
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