# Multi-stage Dockerfile for Odyssey Django app

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# System deps (build tools & libpq for psycopg2 if needed)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=odyssey.settings
WORKDIR /app

# Copy installed site-packages from builder
COPY --from=builder /install /usr/local

# Copy project
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Collect static at build time (optional; can also run at startup if dynamic)
RUN mkdir -p staticfiles && python manage.py collectstatic --noinput || true

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -fsS http://localhost:8000/healthz || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "odyssey.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "3", "--timeout", "60"]
