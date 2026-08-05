# 1. Use a slim image to reduce attack surface and image size (Cloud Optimization)
FROM python:3.11-slim

WORKDIR /app

# 2. Prevent Python from writing pyc files and ensure logs are sent to terminal in real-time
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Install system dependencies required for mysqlclient
# Cleaning up apt cache in the same layer to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

ENV PIP_NO_CACHE_DIR=1

RUN pip install --upgrade --force-reinstall pip "setuptools>=78.1.1" "msgpack>=1.2.1" wheel && \
    pip install -r requirements.txt

# 5. Copy project files
COPY . .

# 6. SECURITY LAYER (DevSecOps)
# Create a non-privileged system user to avoid running as root
RUN useradd -u 8888 django-user && \
    chown -R django-user:django-user /app

# Switch to the non-root user
USER django-user

# Port exposed by Django
EXPOSE 8000

# Start command
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]