# Smart-Uni: Connected University Residence

**Smart-Uni** is an intelligent web management platform designed for university residence students. The project integrates **home automation (IoT), gamification**, and **collaborative services** (study room bookings, resident directory) to enhance students' daily campus lives.

## 🏗️ Architecture & Deployment

> ⚠️ **Important note on project organization**: This repository exclusively contains the **application source code** for Smart-Uni. 
> 
> Everything related to infrastructure, Docker configuration, CI/CD pipelines, and deployment scripts is centralized in a separate repository:
> **[smart-uni-infra](https://github.com/Mohamine2/smart-uni-infra)**

### 📁 Separation of Concerns
* **`Smart-Uni` (this repository)**: Feature development, business logic, data model management, and application views.
* **`smart-uni-infra`**: Container orchestration, network configuration, and final deployment.

### 🗺️ Application Architecture

To understand how the application components interact when deployed via the infrastructure repository, here is the architecture diagram:
<img width="949" height="1071" alt="smart-uni-application architecture diagram" src="https://github.com/user-attachments/assets/8e7b3e1b-299c-4a15-982f-a3483bfb43a4" />


## 🛡️ DevSecOps & Security Practices
This project follows modern enterprise DevSecOps practices to ensure environment security and automated code quality gating:

### 1. Hardened Container Security (Non-Root Execution)
To implement the principle of least privilege, the Docker image is hardened against container-breakout vulnerabilities:
- A dedicated unprivileged system user (django-user) is created within the Dockerfile.
- The application runs entirely under this user's context rather than defaulting to root.
- Directory permissions are strictly constrained to the /app workspace.

### 2. Automated CI/CD Pipeline (GitHub Actions)
A Continuous Integration pipeline is triggered on every push or pull_request to the main branch `.github/workflows/ci-devsecops.yml`:

- **Automated Build:** Validates Dockerfile compilation and layer caching.
- **Automated Testing & Coverage:** Executes Django unit and integration test suites using an isolated, fast SQLite in-memory database to validate core business logic, API endpoints, and database interactions, enforcing a strict **80% minimum code coverage threshold** configured via `.coveragerc`.
- **Vulnerability Scanning (Aqua Security Trivy):** Before any deployment, Trivy scans the container's base operating system `python:3.11-slim` and deep-scans transitive Python dependencies (resolving underlying risks in tools like setuptools and wheel). It blocks the pipeline `exit code 1` if any `HIGH` or `CRITICAL` vulnerabilities are discovered.
- **Automated Secure Publishing:** Upon passing all security gates, the verified production-ready image is securely authenticated via GitHub Repository Secrets and pushed to DockerHub using a unique Git short-SHA commit tag.

#### Orchestration & Environments
To support this automated pipeline and local testing, the project relies on two distinct orchestrators:

* **Production (`docker-compose.prod.yml`)**: 
  Automatically triggered and referenced during the CD phase of our GitHub Actions workflow. It handles the live orchestration on the remote **AWS EC2** instance, spawning NGINX as a reverse proxy, Gunicorn, MySQL, and managing persistent volumes.
  
* **Development (`docker-compose.yml`)**: 
  Used strictly for local development. It boots up the `Django runserver` (with hot-reload enabled via a bind-mount) and a local `MySQL` database without going through NGINX or the cloud pipeline.

---

## Key Features

### 🎮 Gamification & Experience Points (XP) System
Access to home automation features is restricted by a leveling system based on experience points earned through user engagement and logins:
- **Beginner (0-2 XP) :** Basic access—viewing the platform dashboard, resident directory, and campus news.
- **Intermediate (3+ XP) :** Smart home management enabled—residents can add and rename smart devices inside their assigned accommodation.
- **Advanced (5+ XP) :** Granular device operations—residents can delete devices and adjust precise controls (e.g., power levels, dimmers, toggle states).
- **Expert (7+ XP) :** Smart Grid Access—unlocks the comprehensive energy consumption statistics dashboard.

*Note: Level promotions must be triggered manually by students from their profile dashboard once the required XP threshold is fulfilled.*

### 🏠 Smart Home Management
- Visual representation of connected devices per room (Living Room, Bedroom, etc.).
- Remote interface for smart appliances (Lamps, Thermostats, etc.).
- Real-time power consumption and energy metric tracking.

### 📅 Campus & Residence Services
- **Study Room Bookings :** Interactive booking engine with automated schedule conflict detection and reservation blocking.
- **Booking Ledger :** Dedicated citizen workspace to view, track, or cancel active room reservations.
- **Resident Directory :** Interactive internal directory of fellow campus residents to foster social connections.
- **Campus Newsfeed :** Real-time bulletin board for official university residence updates and social events.

---

## 🛠️ Technical Stack

- **Backend :** Python 3.11, Django 5.2
- **Frontend :** HTML5, CSS3 (Modern, mobile-responsive, centralized style sheets)
- **Database :** MySQL
- **Deployment :** Docker & Docker Compose

---

## 📦 Local Installation & Setup (Docker)

The repository is fully Dockerized to guarantee reproducible environments and eliminate local runtime setup friction.

### 1. Prerequisites
- Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) configured on your machine.

### 2. Environment Configuration
   Secure application settings are managed dynamically through decoupled environment scopes:

1. **Initialize your local configuration file from the distributed blueprint:**

   ```bash
   cp .env.example .env
   ```
2. **Generate a secure cryptographic signing key for your local Django instance:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
3. **Update your .env:**
   Copy the generated key and paste it into your .env file:

### 3. Resolving Local Port Conflicts
If you have MySQL installed natively on your machine, it will conflict with the Docker container. Before launching the project, stop the local service:
```bash
   sudo systemctl stop mysql
```

### 4. Running the Multi-Container Cluster
Build and start your service topology from the repository root (this orchestrates the network layer, spins up the MySQL schema engine, compiles the hardened Python runner, and binds the Django server):
```bash
docker compose up --build
```
The application will be exposed locally at: http://127.0.0.1:8000.

### 5. Database Initializations & Migrations
The database container automatically initializes the core instance layout using the schema bootstrap file located at `docker/mysql/init.sql`. In a separate shell terminal, map the Django ORM schema constraints to the database:
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### 6. Administrative Access (Optional)
To create an administrative operator to access the Django native administration panel (http://127.0.0.1:8000/admin):
```bash
docker compose exec web python manage.py createsuperuser
```

### 7. Seeding Mock Data (Development & Testing)
To instantly populate your local instance with deterministic, realistic data records (mock student profiles, pre-configured study rooms, smart devices, and structured bulletin stories), execute the seeding scripts:
```bash
docker compose exec web python populate_students.py
docker compose exec web python populate_news.py
docker compose exec web python populate_study_rooms.py
```

## 📂 Project Architecture

The workspace strictly adheres to enterprise Django architectural boundaries optimized for isolated multi-stage container tracking.

```text
Smart-Uni/
├── .github/workflows/          # CI/CD Automation
│   └── ci-devsecops.yml        # DevSecOps GitHub Actions workflow (Trivy + Push)
│
├── core/                       # Global project configuration application
│   ├── settings.py             # Global settings (Database mappings, Auth, Static assets)
│   ├── urls.py                 # Core routing definitions and URL entry points
│   └── wsgi.py / asgi.py       # WSGI/ASGI web server interface hooks
│
├── residence_connectee/        # Core business logic application
│   ├── migrations/             # Database version history logs
│   ├── admin.py                # Django Admin dashboard representations
│   ├── apps.py                 # Application configuration bootstrap
│   ├── forms.py                # Django form declarations
│   ├── models.py               # ORM Entities (Student, Device, StudyRoom, Booking)
│   ├── signals.py              # Event-driven triggers (Automated XP allocation)
│   ├── tests.py                # Automated unit and integration test suites validating business logic, endpoints, and database interactions
│   └── views.py                # Controller layers (Automation UI, Ledger, Directory, Bookings)
│
├── static/                     # Global static assets
│   └── style.css               # Centralized layout styling and responsive directives
│
├── templates/                  # Presentation layers (HTML5 Interfaces utilizing Django Template Language)
│   ├── base.html               # Main structural layout blueprint (Navbar, Footer, Global scripts)
│   ├── index.html              # Landing portal and newsfeed interface
│   ├── dashboard.html          # Student control desk (Gamification status & IoT devices overview)
│   ├── login.html              # User authentication login interface
│   ├── register.html           # Resident registration interface
│   ├── edit_profile.html       # Profile adjustment and personal info workspace
│   ├── student_list.html       # Interactive campus resident directory
│   ├── book_room.html          # Study room scheduling and conflict-validation forms
│   ├── my_reservations.html    # Active booking tracker and cancellation dashboard
│   ├── news_detail.html        # Comprehensive article view for campus bulletins
│   ├── add_device.html         # Smart home onboarding interface (Intermediate tier +)
│   ├── configure_device.html   # Granular power/state management interface (Advanced tier +)
│   ├── rename_device.html      # Device labeling setup
│   ├── search_devices.html     # Real-time IoT inventory query component
│   └── statistics.html         # Advanced Smart Grid energy tracking (Expert tier exclusive)
│
├── Dockerfile                  # Hardened, unprivileged instructions for the Python builder
├── docker-compose.yml          # # Local development orchestrator (Django runserver + MySQL)
├── docker-compose.prod.yml     # Production orchestrator (NGINX + Gunicorn + MySQL + Volumes)
├── manage.py                   # Execution entrypoint for Django terminal utility scripts
├── requirements.txt            # Python structural constraints manifest (Django, drivers, etc.)
├── .coveragerc                 # Coverage configuration defining measurement rules, exclusions, and thresholds for automated testing
├── .trivyignore                # Security scanner whitelist for documenting and bypassing verified false positives and unfixable CVEs
├── populate_students.py        # Database mock data seeder (Student datasets)
├── populate_news.py            # Database mock data seeder (Residence news bulletins)
└── populate_study_rooms.py     # Database mock data seeder (Study rooms & scheduling)
```

## 📝 Autors
Project developed as part of the ING1 Computer Science Engineering Curriculum at CY Tech (2025-2026).
