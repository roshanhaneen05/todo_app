# TaskMaster Pro - Containerized Full-Stack To-Do Management Application

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Alpine-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

---

## 📌 Project Overview

**TaskMaster Pro** is a production-ready, containerized full-stack To-Do Management Application engineered for Cloud & DevOps deployment demonstrations. It features a modern Python Flask backend, a persistent MySQL 8.0 database, an interactive glassmorphism JavaScript UI, an Nginx reverse proxy, and a complete GitHub Actions CI/CD pipeline integrated with Trivy security scanning and Pytest automated testing.

---

## 🏛 Architecture Diagram

```
+-------------------------------------------------------------------------+
|                              CLIENT BROWSER                             |
+-------------------------------------------------------------------------+
                                    |
                                HTTP (Port 80)
                                    v
+-------------------------------------------------------------------------+
|                          NGINX REVERSE PROXY                            |
|                          (Container: todo_nginx)                        |
+-------------------------------------------------------------------------+
                                    |
                            Custom Docker Network
                               (todo-network)
                                    v
+-------------------------------------------------------------------------+
|                         PYTHON FLASK APP (GUNICORN)                     |
|                          (Container: todo_flask_app)                    |
+-------------------------------------------------------------------------+
                                    |
                            Custom Docker Network
                               (todo-network)
                                    v
+-------------------------------------------------------------------------+
|                            MYSQL DATABASE 8.0                           |
|                           (Container: todo_mysql)                       |
|                       Volume: todo-app_mysql-data                       |
+-------------------------------------------------------------------------+
```

---

## ✨ Features

- **Full Task Lifecycle Management**: Create, view, update, delete, mark completed, or revert tasks to pending status.
- **Modern Responsive Interface**: Custom glassmorphism UI with real-time counters, search filters, toast notifications, and modal editing.
- **Production WSGI Server**: Powered by Gunicorn with multi-worker process handling.
- **Multi-Stage Non-Root Dockerization**: Container runs under dedicated non-root user `appuser` (UID 10001).
- **Persistent Data Storage**: Named Docker volume `mysql-data` ensures data survives container updates or teardowns (`docker compose down`).
- **Health Checks & Observability**: Dedicated `/health` endpoint and Prometheus `/metrics` route.
- **Security & CI/CD**: Automated linting (`black`, `flake8`), vulnerability auditing (`pip-audit`, `trivy`), and Docker Hub delivery via GitHub Actions.

---

## 🛠 Technology Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Responsive Glassmorphism SPA with `fetch()` API |
| **Backend** | Python 3.11, Flask 3.0, Gunicorn | REST API with structured logging & Prometheus metrics |
| **Database** | MySQL 8.0, PyMySQL | Relational database storage with init schema scripts |
| **Reverse Proxy** | Nginx Alpine | Port 80 reverse proxy with security headers |
| **Containerization** | Docker, Docker Compose | Custom `todo-network`, multi-stage builds |
| **Testing** | Pytest, Pytest-Flask | Isolated unit test suite with mock DB fixtures |
| **CI/CD** | GitHub Actions | Automated build, lint, test, Trivy scan, and Docker Hub push |

---

## 📂 Project Structure

```
todo-app/
├── app/
│   ├── __init__.py         # Flask app factory, logging & blueprint registration
│   ├── config.py           # Environment configuration loader
│   ├── database.py         # MySQL connection pooling & health checks
│   ├── models.py           # Task CRUD business logic & database queries
│   └── routes.py           # REST API endpoints & UI routing
├── templates/
│   └── index.html          # Main HTML5 application interface
├── static/
│   ├── css/
│   │   └── style.css       # Custom Glassmorphism styles & responsive rules
│   └── js/
│       └── app.js          # Client-side API fetch client & DOM renderer
├── tests/
│   ├── __init__.py         # Test package initialization
│   └── test_app.py         # Pytest automated test suite
├── mysql/
│   └── init.sql            # Database schema & initial seed data
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # GitHub Actions CI/CD pipeline workflow
├── requirements.txt        # Production Python dependencies
├── requirements-dev.txt    # Development, linting & testing dependencies
├── Dockerfile              # Multi-stage production Docker build definition
├── docker-compose.yml      # Service orchestration for mysql, app, nginx
├── nginx.conf              # Nginx reverse proxy configuration
├── .dockerignore           # Excluded files for Docker build context
├── .gitignore              # Excluded files for Git version control
├── .env.example            # Environment variables template
└── README.md               # Extensive project documentation & viva guide
```

---

## 🚀 Prerequisites

- **Docker Desktop** (v20.10+) or Docker Engine & Docker Compose (v2.0+)
- **Git**
- **Python 3.11+** (for optional local non-containerized development)

---

## 🔑 Environment Configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

`.env` content structure:

```ini
MYSQL_ROOT_PASSWORD=root_password_secure
MYSQL_DATABASE=todo_db
MYSQL_USER=todo_user
MYSQL_PASSWORD=todo_password_secure
MYSQL_HOST=mysql
MYSQL_PORT=3306
SECRET_KEY=super-secret-production-key
```

> ⚠️ **Security Warning**: Never commit `.env` or plain-text credentials to version control. `.env` is listed in `.gitignore`.

---

## 🐳 Quick Start with Docker Compose

### 1. Build and Launch Containers
```bash
docker compose up -d --build
```

### 2. Verify Running Containers
```bash
docker compose ps
```

Expected Output:
```
NAME               IMAGE          COMMAND                  SERVICE   CREATED         STATUS                   PORTS
todo_flask_app     todo-app_app   "gunicorn --bind 0.0…"   app       2 minutes ago   Up 2 minutes (healthy)   5000/tcp
todo_mysql         mysql:8.0      "docker-entrypoint.s…"   mysql     2 minutes ago   Up 2 minutes (healthy)   3306/tcp, 33060/tcp
todo_nginx_proxy   nginx:alpine   "/docker-entrypoint.…"   nginx     2 minutes ago   Up 2 minutes             0.0.0.0:80->80/tcp
```

### 3. Access Application
Open your browser and navigate to:
`http://localhost`

---

## 📊 Database Persistence: `down` vs `down -v`

- `docker compose down`: Stops and removes application containers and networks. **Your task data is preserved** in the `mysql-data` volume.
- `docker compose down -v`: Stops containers AND **permanently deletes all volumes**, destroying all stored task data.

---

## 📡 API Endpoints Documentation

| Method | Endpoint | Description | Sample Request Body | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Renders Single Page UI | N/A | `200 OK` |
| `GET` | `/health` | Application & DB Health Status | N/A | `200 OK` / `503 Service Unavailable` |
| `GET` | `/metrics` | Prometheus Metrics Stream | N/A | `200 OK` |
| `GET` | `/api/tasks` | Fetch all tasks | N/A | `200 OK` |
| `POST` | `/api/tasks` | Create new task | `{"title": "Setup CI/CD", "description": "Configure GitHub Actions"}` | `201 Created` |
| `PUT` | `/api/tasks/<id>` | Update task fields | `{"title": "New Title", "completed": true}` | `200 OK` / `404 Not Found` |
| `PATCH` | `/api/tasks/<id>/complete` | Mark task as completed | N/A | `200 OK` / `404 Not Found` |
| `PATCH` | `/api/tasks/<id>/pending` | Mark task as pending | N/A | `200 OK` / `404 Not Found` |
| `DELETE` | `/api/tasks/<id>` | Delete task by ID | N/A | `200 OK` / `404 Not Found` |

---

## 🧪 Testing & Code Quality

### Run Pytest Suite
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

### Run Formatting & Linting Checks
```bash
black --check .
flake8 .
```

---

## 🔒 Security & Vulnerability Scanning

### Dependency Audit with `pip-audit`
```bash
pip-audit
```

### Container Vulnerability Scan with `Trivy`
```bash
trivy image username/todo-app:latest
```

---

## 🔄 GitHub Actions CI/CD Workflow

The `.github/workflows/ci-cd.yml` automates end-to-end delivery:
1. **Checkout Code & Python Setup**
2. **Format & Linting Verification**: Runs `black` and `flake8`.
3. **Dependency Vulnerability Audit**: Executes `pip-audit`.
4. **Automated Unit Testing**: Runs `pytest`.
5. **Docker Multi-Stage Build**: Compiles lightweight image.
6. **Security Scanning**: Scans built image using **Trivy**.
7. **Docker Hub Publishing**: Pushes `latest` and `v1.0.0` tags upon push to `main`.

---

## 📜 Log Management

View application logs:
```bash
# All service logs
docker compose logs -f

# Specific container logs
docker compose logs -f app
docker compose logs -f mysql
docker compose logs -f nginx
```

---

## 📋 Comprehensive viva & Student Defense Guide

### Q1: Why do we use Nginx as a reverse proxy in front of Gunicorn/Flask?
**Answer**: Nginx handles SSL termination, client buffering, security header injection, static file caching, and request rate limiting. Gunicorn is an application WSGI worker manager and should not be directly exposed to public internet traffic.

### Q2: What is the difference between `docker compose down` and `docker compose down -v`?
**Answer**: `docker compose down` stops and removes containers and networks while retaining persistent data volumes. `docker compose down -v` additionally deletes named volumes (`mysql-data`), leading to permanent database data loss.

### Q3: Why is multi-stage Docker build used?
**Answer**: Multi-stage builds separate build-time dependencies (compilers, build headers) from the runtime environment. This produces significantly smaller Docker image sizes and reduces the security attack surface by excluding unnecessary build tools.

---

## 🧰 Summary Command Cheatsheet

```bash
# Build and run containers
docker compose up -d --build

# View container status & network
docker compose ps
docker network inspect todo-network
docker volume inspect todo-app_mysql-data

# Run tests locally
pytest -v

# Stop containers gracefully
docker compose down
```
