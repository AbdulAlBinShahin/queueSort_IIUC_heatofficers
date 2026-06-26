# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (only what we need; keep the image small).
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project.
COPY . /app

# Persistent storage for the SQLite database.
RUN mkdir -p /app/data
VOLUME ["/app/data"]

EXPOSE 8000

# Default to gunicorn for production; docker-compose passes PORT.
ENV PORT=8000

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 3 --access-logfile - --error-logfile -"]