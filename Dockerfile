FROM python:3.11

WORKDIR /app

# PYTHONDONTWRITEBYTECODE=1 -> Évite de créer des fichiers inutiles (.pyc).
# PYTHONUNBUFFERED=1 -> Affiche les erreurs directement dans ton terminal sans attendre.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dépendances système : On installe les clients mysql pour python ainsi que gcc
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

# On installe toutes les bibliothèques nécessaires au projet
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du projet : On prend tout le dossier et on le met dans le conteneur.
COPY . /app/