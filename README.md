# 📦 BeBo — Box-Bestand-Organizer

*🇩🇪 Deutsche Version | 🇬🇧 [English version below](#-bebo--box-inventory-organizer)*

Eine Django-basierte Webanwendung zur Verwaltung von Lagerboxen und deren Inhalten. Perfekt für Keller, Dachböden, Lagerräume oder überall dort, wo du den Überblick behalten willst.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)

---

## ✨ Features

- 📦 **Box-Verwaltung** — Erstelle, bearbeite und durchsuche Lagerboxen
- 🏷️ **Kategorien & Tags** — Organisiere Boxen nach Kategorien
- 📍 **Lagerorte** — Definiere Standorte für deine Boxen
- 📸 **Bildupload** — Fotografiere Boxinhalte für schnelles Wiederfinden
- 📜 **Änderungsverlauf** — Vollständige Historie aller Änderungen
- 🔍 **Suche** — Schnelle Volltextsuche über alle Boxen
- 👥 **Benutzer-Authentifizierung** — Login-geschützter Zugang
- 📱 **Responsive Design** — Funktioniert auf Desktop und Mobilgeräten

---

## 🛠️ Tech Stack

| Komponente | Technologie |
|------------|-------------|
| Backend | Python 3.11, Django 5.x |
| Datenbank | PostgreSQL 15 |
| Webserver | Gunicorn (Production) |
| Static Files | WhiteNoise |
| Frontend | Bootstrap 5, Crispy Forms |
| Container | Docker & Docker Compose |
| Versionierung | django-simple-history |

---

## 🚀 Installation

### Voraussetzungen

- Docker & Docker Compose
- Git

### Schnellstart

```bash
# Repository klonen
git clone https://github.com/JOHBECHTOLD/BeBo.git
cd BeBo

# Umgebungsvariablen konfigurieren
cp .env.example .env
# → .env Datei anpassen (SECRET_KEY, DB-Passwort, etc.)

# Container starten
docker compose up -d

# Datenbank initialisieren
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# Static Files sammeln
docker compose exec web python manage.py collectstatic --noinput
Zugriff
Lokal: http://localhost:8000
Admin: http://localhost:8000/admin
⚙️ Konfiguration
Umgebungsvariablen (.env)

# Django
SECRET_KEY=dein-geheimer-key-hier
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,deine-domain.de

# Datenbank
DB_NAME=bebo_db
DB_USER=bebo_user
DB_PASSWORD=sicheres-passwort
DB_HOST=db
DB_PORT=5432

# CSRF (für HTTPS)
CSRF_TRUSTED_ORIGINS=https://deine-domain.de
Secret Key generieren

docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
🗂️ Projektstruktur

BeBo/
├── bebo_core/          # Django Projekt-Konfiguration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/          # Haupt-App
│   ├── models.py       # Box, Category, Location
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── templates/          # Globale Templates
├── static/             # CSS, JS, Bilder
├── media/              # Uploads (nicht in Git)
├── docker-compose.yml  # Production Config
├── Dockerfile
├── deploy.sh           # Deployment Script
├── requirements.txt
└── README.md
📋 Changelog
Siehe Changelog in der Anwendung.

Aktuelle Version: 1.6.4
✅ Production-Deployment-Workflow
✅ Gunicorn WSGI-Server
✅ Health-Checks für Container
✅ Automatische Backups
📄 Lizenz
Dieses Projekt steht unter der Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Lizenz (CC BY-NC-SA 4.0).

Was bedeutet das?
✅ Du darfst:

Das Projekt für private, nicht-kommerzielle Zwecke nutzen
Den Code ansehen, lernen und studieren
Eigene Anpassungen vornehmen
Das Projekt mit anderen teilen
🚫 Du darfst NICHT:

Das Projekt oder Teile davon kommerziell nutzen oder verkaufen
Es in kommerzielle Produkte einbinden ohne Genehmigung
📝 Du musst:

Den ursprünglichen Autor (Johannes Bechtold) nennen
Einen Link zu dieser Lizenz beifügen
Änderungen kennzeichnen
Abgeleitete Werke unter derselben Lizenz teilen
Vollständige Lizenz: CC BY-NC-SA 4.0

🙏 Danksagungen
Django
Bootstrap
Docker
👤 Autor
Johannes Bechtold — @JOHBECHTOLD

📦 BeBo — Box Inventory Organizer
🇬🇧 English Version | 🇩🇪 Deutsche Version oben

A Django-based web application for managing storage boxes and their contents. Perfect for basements, attics, storage rooms, or anywhere you need to keep track of your stuff.

Python
Django
PostgreSQL
Docker
License

✨ Features
📦 Box Management — Create, edit, and search storage boxes
🏷️ Categories & Tags — Organize boxes by categories
📍 Storage Locations — Define locations for your boxes
📸 Image Upload — Photograph box contents for quick identification
📜 Change History — Complete history of all changes
🔍 Search — Fast full-text search across all boxes
👥 User Authentication — Login-protected access
📱 Responsive Design — Works on desktop and mobile devices
🛠️ Tech Stack
Component	Technology
Backend	Python 3.11, Django 5.x
Database	PostgreSQL 15
Web Server	Gunicorn (Production)
Static Files	WhiteNoise
Frontend	Bootstrap 5, Crispy Forms
Container	Docker & Docker Compose
Versioning	django-simple-history
🚀 Installation
Prerequisites
Docker & Docker Compose
Git
Quick Start

# Clone repository
git clone https://github.com/JOHBECHTOLD/BeBo.git
cd BeBo

# Configure environment variables
cp .env.example .env
# → Edit .env file (SECRET_KEY, DB password, etc.)

# Start containers
docker compose up -d

# Initialize database
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput
Access
Local: http://localhost:8000
Admin: http://localhost:8000/admin
⚙️ Configuration
Environment Variables (.env)

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_NAME=bebo_db
DB_USER=bebo_user
DB_PASSWORD=secure-password
DB_HOST=db
DB_PORT=5432

# CSRF (for HTTPS)
CSRF_TRUSTED_ORIGINS=https://your-domain.com
Generate Secret Key

docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
🗂️ Project Structure

BeBo/
├── bebo_core/          # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/          # Main app
│   ├── models.py       # Box, Category, Location
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── templates/          # Global templates
├── static/             # CSS, JS, images
├── media/              # Uploads (not in Git)
├── docker-compose.yml  # Production config
├── Dockerfile
├── deploy.sh           # Deployment script
├── requirements.txt
└── README.md
📋 Changelog
See Changelog in the application.

Current Version: 1.6.4
✅ Production deployment workflow
✅ Gunicorn WSGI server
✅ Health checks for containers
✅ Automatic backups
📄 License
This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

What does this mean?
✅ You may:

Use the project for private, non-commercial purposes
View, learn from, and study the code
Make your own modifications
Share the project with others
🚫 You may NOT:

Use the project or parts of it commercially or sell it
Integrate it into commercial products without permission
📝 You must:

Credit the original author (Johannes Bechtold)
Provide a link to this license
Indicate if changes were made
Share derivative works under the same license
Full License: CC BY-NC-SA 4.0

🙏 Acknowledgments
Django
Bootstrap
Docker
👤 Author
Johannes Bechtold — @JOHBECHTOLD