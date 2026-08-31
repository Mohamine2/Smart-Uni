# ==========================================
# Stage 1: Builder (Package compilation)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tools strictly required for C compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create an isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runtime (Final production image)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Prepend the virtualenv to PATH to run python/gunicorn directly
ENV PATH="/opt/venv/bin:$PATH"

# Runtime dynamic libraries only
# No gcc, no lib*-dev, no pkg-config
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the ready-to-use virtualenv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non-root user before copying the application code
RUN useradd -u 8888 -d /app django-user && \
    mkdir -p /app/staticfiles /app/mediafiles && \
    chown -R django-user:django-user /app

# Copy application code
COPY --chown=django-user:django-user . .

USER django-user

EXPOSE 8000