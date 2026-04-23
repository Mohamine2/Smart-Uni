# Smart-Uni : Résidence Universitaire Connectée

**Smart-Uni** est une plateforme web de gestion intelligente destinée aux résidents d'une cité universitaire. Le projet intègre des concepts de **domotique (IoT)**, de **gamification** et de **services collaboratifs** (réservation de salles, annuaire) pour améliorer le quotidien des étudiants.

## Fonctionnalités Principales

### 🎮 Système de Gamification (XP)
L'accès aux fonctionnalités est restreint par un système de niveaux basé sur des points d'expérience (points gagnés lors des connexions et actions) :
- **Débutant (0-2 pts) :** Consultation simple du site, de l'annuaire et des actualités.
- **Intermédiaire (3+ pts) :** Possibilité d'ajouter et de renommer des objets connectés dans son logement.
- **Avancé (5+ pts) :** Possibilité de supprimer des objets et d'accéder aux réglages précis (puissance, état d'allumage).
- **Expert (7+ pts) :** Accès au tableau de bord des statistiques de consommation énergétique.

*Note : Le passage au niveau supérieur s'effectue manuellement par l'étudiant depuis son profil une fois le palier de points atteint.*

### 🏠 Gestion du Logement Connecté
- Visualisation des objets par pièce (Salon, Chambre, etc.).
- Contrôle des équipements (Lampe, Thermostat, etc.).
- Suivi de la consommation en temps réel.

### 📅 Services de la Résidence
- **Réservation de salles d'étude :** Système de réservation avec vérification automatique des conflits d'horaires.
- **Gestion des réservations :** Consultation et annulation des créneaux réservés depuis un espace dédié.
- **Annuaire des résidents :** Liste interactive des étudiants de la résidence pour faciliter le lien social.
- **Actualités :** Flux d'informations et d'événements de la cité U.

---

## 🛠️ Stack Technique

- **Backend :** Python 3.11, Django 5.2
- **Frontend :** HTML5, CSS3 (Design moderne, responsive, et centralisé)
- **Base de données :** MySQL
- **Déploiement :** Docker & Docker-Compose

---

## 📦 Installation et Lancement (Docker)

Ce projet est entièrement "Dockerisé" pour faciliter son déploiement en local.

### 1. Prérequis
- [Docker](https://docs.docker.com/get-docker/) et [Docker Compose](https://docs.docker.com/compose/install/) installés sur votre machine.

### 2. Lancement des conteneurs
À la racine du projet, construisez et lancez les conteneurs (cela téléchargera les images, configurera la base de données MySQL et lancera le serveur Django) :
```bash
docker-compose up --build
```
Le site sera alors accessible à l'adresse : http://127.0.0.1:8000.

### 3. Initialiser la base de données (Migrations)
Dans un nouveau terminal, exécutez les migrations pour créer les tables :
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 4. Créer un compte administrateur (Optionnel)
Pour accéder à l'interface d'administration Django (http://127.0.0.1:8000/admin) :
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. 🧪 Peupler la base de données (Test)
Pour tester immédiatement le projet avec des données réalistes (utilisateurs, salles d'étude, objets connectés, actualités), utilisez nos scripts de population :
```bash
docker-compose exec web python populate_students.py
docker-compose exec web python populate_news.py
docker-compose exec web python populate_study_rooms.py
```

## 📂 Structure détaillée du projet

Le projet suit la structure standard d'une application **Django**, optimisée pour le déploiement via **Docker**.

```text
Smart-Uni/
├── core/                       # Configuration globale du projet
│   ├── settings.py             # Paramètres (BDD, Emails, Auth, Static)
│   ├── urls.py                 # Routage principal du site
│   └── wsgi.py / asgi.py       # Points d'entrée du serveur web
│
├── residence_connectee/        # Application métier principale
│   ├── migrations/             # Historique des versions de la base de données
│   ├── admin.py                # Configuration de l'interface d'administration
│   ├── apps.py                 # Configuration de l'application & Signaux
│   ├── models.py               # Définition des tables (Etudiant, Objet, Salle, Réservation)
│   ├── signals.py              # Logique automatique (Attribution des points d'XP)
│   └── views.py                # Logique des pages (Logement, Stats, Annuaire, Réservations)
│
├── static/                     # Fichiers statiques
│   └── style.css               # Design centralisé et responsive du projet
│
├── templates/                  # Interfaces HTML
│   ├── index.html              # Page d'accueil et recherche globale
│   ├── dashboard-simple.html   # Tableau de bord résident (Gamification + Objets)
│   ├── login.html / register.html # Authentification
│   ├── modifier_profil.html    # Gestion des informations personnelles
│   ├── liste_etudiants.html    # Annuaire des résidents
│   ├── reservation_salle.html  # Formulaire de réservation
│   ├── mes_reservations.html   # Suivi et annulation des créneaux
│   └── statistiques.html       # Dashboard énergétique (Niveau Expert)
│
├── Dockerfile                  # Instructions pour l'image Docker Python
├── docker-compose.yml          # Orchestration (Python + MySQL)
├── manage.py                   # Script de commande Django
├── requirements.txt            # Dépendances Python (Django, mysqlclient, etc.)
├── populate_students.py        # # Script de population de test (Etudiants)
├── populate_news.py            # Script de population de test (Actualités)
└── populate_study_rooms.py     # Script de population de test (Salles d'étude)
```

## 📝 Auteurs
Projet réalisé dans le cadre du cursus ING1 CY Tech (2025-2026).
