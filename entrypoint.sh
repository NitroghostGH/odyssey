#!/usr/bin/env bash
set -euo pipefail

# Apply migrations if requested (default yes)
if [[ "${RUN_MIGRATIONS:-1}" == "1" ]]; then
  echo "Applying migrations..."
  python manage.py migrate --noinput
fi

# Optionally create a superuser
if [[ "${DJANGO_SUPERUSER_USERNAME:-}" != "" ]]; then
  echo "Ensuring superuser ${DJANGO_SUPERUSER_USERNAME}";
  python manage.py shell <<'EOF'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL') or f"{username}@example.com"
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
EOF
fi

exec "$@"
