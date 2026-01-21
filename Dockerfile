# Basis-Image: Schlankes Python 3.11
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Umgebungsvariablen für Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# System-Abhängigkeiten installieren (wichtig für Postgres & Bilder)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python-Bibliotheken installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den Rest des Codes kopieren
COPY . .