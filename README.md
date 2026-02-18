# 📦 BeBo — Box-Bestand-Organizer

*🇩🇪 Deutsche Version | 🇬🇧 English version below*

Eine moderne Webanwendung zur Verwaltung von Lagerboxen und deren Inhalten – entwickelt mit **Python 3.11** und **Django 5**.
Perfekt für Keller, Dachboden, Lagerraum oder überall dort, wo Ordnung dauerhaft bleiben soll.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)

---

# 🇩🇪 Deutsche Version

## ✨ Features

* 📦 **Box-Verwaltung** – Erstellen, Bearbeiten & Durchsuchen von Lagerboxen
* 🏷️ **Kategorien & Tags** – Flexible Organisation
* 📍 **Lagerorte** – Verwaltung mehrerer Standorte
* 📸 **Bildupload** – Fotos für schnelle Wiedererkennung
* 📜 **Änderungsverlauf** – Vollständige Historie aller Änderungen
* 🔍 **Volltextsuche** – Schnelles Finden von Inhalten
* 👥 **Benutzer-Authentifizierung** – Geschützter Login-Bereich
* 📱 **Responsive Design** – Desktop & Mobile optimiert

---

## 🛠️ Tech Stack

| Bereich           | Technologie                      |
| ----------------- | -------------------------------- |
| Backend           | Python 3.11, Django 5.x          |
| Datenbank         | PostgreSQL 15                    |
| Webserver         | Gunicorn                         |
| Static Files      | WhiteNoise                       |
| Frontend          | Bootstrap 5, Django Crispy Forms |
| Containerisierung | Docker & Docker Compose          |
| Versionierung     | django-simple-history            |

---

## 🚀 Installation

### Voraussetzungen

* Docker
* Docker Compose
* Git

---

### 🔹 Schnellstart

```bash
# Repository klonen
git clone https://github.com/JOHBECHTOLD/BeBo.git
cd BeBo

# Umgebungsvariablen kopieren
cp .env.example .env

# .env anpassen (SECRET_KEY, DB_PASSWORD, etc.)

# Container starten
docker compose up -d

# Migrationen ausführen
docker compose exec web python manage.py migrate

# Admin-User erstellen
docker compose exec web python manage.py createsuperuser

# Statische Dateien sammeln
docker compose exec web python manage.py collectstatic --noinput
```

---

## 🌍 Zugriff

| Bereich     | URL                                                        |
| ----------- | ---------------------------------------------------------- |
| Anwendung   | [http://localhost:8000](http://localhost:8000)             |
| Admin Panel | [http://localhost:8000/admin](http://localhost:8000/admin) |

---

## ⚙️ Konfiguration

### Umgebungsvariablen (`.env`)

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_NAME=bebo_db
DB_USER=bebo_user
DB_PASSWORD=secure-password
DB_HOST=db
DB_PORT=5432

# CSRF (für HTTPS)
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

---

### 🔐 Secret Key generieren

```bash
docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🗂️ Projektstruktur

```
BeBo/
├── bebo_core/          # Django Projekt-Konfiguration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/          # Haupt-App
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── templates/          # Globale Templates
├── static/             # CSS, JS, Bilder
├── media/              # Uploads (nicht versioniert)
├── docker-compose.yml
├── Dockerfile
├── deploy.sh
├── requirements.txt
└── README.md
```

---

## 📋 Changelog

Siehe Changelog innerhalb der Anwendung.

**Aktuelle Version:** `1.6.4`

### Enthaltene Produktionsfeatures

* ✅ Gunicorn WSGI-Server
* ✅ Container Health Checks
* ✅ Deployment-Workflow
* ✅ Automatische Backups

---

## 📄 Lizenz

Dieses Projekt steht unter der
**[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/)** (CC BY-NC-SA 4.0)

### ✅ Erlaubt

* Private, nicht-kommerzielle Nutzung
* Code studieren und anpassen
* Weitergabe unter gleicher Lizenz

### 🚫 Nicht erlaubt

* Kommerzielle Nutzung
* Integration in kommerzielle Produkte ohne Genehmigung

### 📝 Verpflichtend

* Namensnennung: *Johannes Bechtold*
* Lizenzverweis
* Kennzeichnung von Änderungen
* Weitergabe unter gleicher Lizenz

---

## 🙏 Danksagungen

* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com/)
* [Docker](https://www.docker.com/)

---

## 👤 Autor

**Johannes Bechtold** — [@JOHBECHTOLD](https://github.com/JOHBECHTOLD)

---
---

*🇬🇧 English Version | 🇩🇪 [German version above](#-bebo--box-bestand-organizer)*

# 📦 BeBo — Box Inventory Organizer

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)

---

## ✨ Features

* 📦 **Box Management** – Create, edit & search storage boxes  
* 🏷️ **Categories & Tags** – Flexible organization  
* 📍 **Storage Locations** – Manage multiple locations  
* 📸 **Image Uploads** – Photos for quick identification  
* 📜 **Change History** – Complete tracking of all modifications  
* 🔍 **Full-Text Search** – Quickly find stored items  
* 👥 **User Authentication** – Secure login-protected access  
* 📱 **Responsive Design** – Optimized for desktop & mobile  

---

## 🛠️ Tech Stack

| Area | Technology |
|------|------------|
| Backend | Python 3.11, Django 5.x |
| Database | PostgreSQL 15 |
| Web Server | Gunicorn |
| Static Files | WhiteNoise |
| Frontend | Bootstrap 5, Django Crispy Forms |
| Containerization | Docker & Docker Compose |
| Versioning | django-simple-history |

---

## 🚀 Installation

### Prerequisites

* Docker  
* Docker Compose  
* Git  

---

### 🔹 Quick Start

```bash
# Clone repository
git clone https://github.com/JOHBECHTOLD/BeBo.git
cd BeBo

# Copy environment variables
cp .env.example .env

# Edit .env file (SECRET_KEY, DB_PASSWORD, etc.)

# Start containers
docker compose up -d

# Run migrations
docker compose exec web python manage.py migrate

# Create admin user
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput
````

---

## 🌍 Access

| Area        | URL                                                        |
| ----------- | ---------------------------------------------------------- |
| Application | [http://localhost:8000](http://localhost:8000)             |
| Admin Panel | [http://localhost:8000/admin](http://localhost:8000/admin) |

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Django
SECRET_KEY=your-secret-key
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
```

---

### 🔐 Generate Secret Key

```bash
docker compose exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🗂️ Project Structure

```
BeBo/
├── bebo_core/          # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/          # Main app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── templates/          # Global templates
├── static/             # CSS, JS, images
├── media/              # Uploads (not versioned)
├── docker-compose.yml
├── Dockerfile
├── deploy.sh
├── requirements.txt
└── README.md
```

---

## 📋 Changelog

See changelog within the application.

**Current Version:** `1.6.4`

### Included Production Features

* ✅ Gunicorn WSGI server
* ✅ Container health checks
* ✅ Deployment workflow
* ✅ Automatic backups

---

## 📄 License

This project is licensed under the
**[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/)** (CC BY-NC-SA 4.0)

### ✅ You may

* Use the project for private, non-commercial purposes
* Study and modify the code
* Share it under the same license

### 🚫 You may NOT

* Use the project commercially
* Integrate it into commercial products without permission

### 📝 You must

* Credit the original author: *Johannes Bechtold*
* Provide a link to the license
* Indicate if changes were made
* Distribute derivative works under the same license

---

## 🙏 Acknowledgments

* [Django](https://www.djangoproject.com/)
* [Bootstrap](https://getbootstrap.com/)
* [Docker](https://www.docker.com/)

---

## 👤 Author

**Johannes Bechtold** — [@JOHBECHTOLD](https://github.com/JOHBECHTOLD)

---
