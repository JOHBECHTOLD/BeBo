# Wir nutzen ein schlankes Python Linux Image
FROM python:3.11-slim

# Arbeitsverzeichnis im Container setzen
WORKDIR /app

# Umgebungsvariablen setzen (verhindert .pyc Dateien und Pufferung)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# System-Abhängigkeiten installieren (nötig für manche Python Pakete)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den Rest des Codes kopieren
COPY . .

# Standard-Befehl (wird später von docker-compose überschrieben)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]