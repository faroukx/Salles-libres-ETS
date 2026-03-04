# Salles libres ÉTS
API permettant de trouver automatiquement les salles de classe disponibles à l’ÉTS à partir d’un PDF d’horaire officiel.

![display](https://github.com/user-attachments/assets/82e4365f-f8db-45ba-8191-3bb39ae73e3c)

## Table des matières
- [Source des données](#-source-des-données)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Structure](#structure)
- [Installation (Première fois)](#installation-première-fois)
- [Utilisation quotidienne](#utilisation-quotidienne)
- [Gestion des horaires (PDF)](#gestion-des-horaires-pdf)
- [Nouvelle Session (Nettoyage & Sync)](#-nouvelle-session-nettoyage--sync)

---

## Source des données
L'application peut désormais récupérer automatiquement les horaires officiels depuis le site de l'ÉTS :
👉 **[Horaire des cours — ÉTS Montréal](https://www.etsmtl.ca/etudier-a-lets/inscription-aux-cours/horaire-cours)**

---

## Fonctionnalités
L'application extrait automatiquement les informations des PDF d'horaires (numéro de salle, jour, plages horaires). Elle permet de rechercher rapidement les salles disponibles à une date et une heure précises. Pour chaque salle trouvée, elle calcule et affiche combien de temps celle-ci restera libre. Un script de rechargement automatique met à jour régulièrement la base de données à partir des nouveaux PDF publiés. Le tout repose sur une architecture propre et modulaire, construite avec FastAPI et SQLAlchemy.

En résumé :
* **Synchronisation automatique** : Télécharge tous les horaires PDF depuis le site de l'ÉTS en un clic.
* **Parsing automatique** : Extrait les données de n'importe quel PDF d'horaire ÉTS.
* **Recherche Intelligente** : Trouve les salles libres par date/heure ou par code de cours.
* **Interface Masterpiece** : Dark Mode, Vue Grille/Liste, Timeline de 3h, et indicateurs de densité.
* **API REST** : Documentation Swagger complète.

## Architecture 
* **FastAPI** → API REST
* **SQLAlchemy** → ORM
* **SQLite** → Base de données (ets_rooms.db)
* **Pydantic** → Validation des données

## Structure
```
ets_room_finder/
├── app/
│   ├── api/          # Routes REST
│   ├── core/         # Configuration et sécurité
│   ├── db/           # Session et base de données
│   ├── models/       # Modèles SQLAlchemy
│   ├── schemas/      # Modèles Pydantic (validation)
│   ├── services/     # Logique métier (Parsing PDF, RoomService)
│   └── main.py       # Point d'entrée FastAPI
├── data/             
│   └── uploads/      # Dossier pour déposer vos horaires PDF localement
├── scripts/          
│   ├── fetch_schedules.py # Script de téléchargement automatique
│   ├── clear_session.py   # Script de nettoyage complet
│   └── sync_session.py    # Script de synchronisation complète
├── requirements.txt  # Dépendances Python
├── setup.bat         # Script d'installation automatique (Windows)
├── setup.sh          # Script d'installation automatique (Mac/Linux)
├── run.bat           # Script de lancement rapide (Windows)
├── run.sh            # Script de lancement rapide (Mac/Linux)
└── .env              # Variables d'environnement
```

# Installation (Première fois)

#### 1. Cloner et entrer dans le projet
```bash
cd ets_room_finder
```

#### 2. Lancer l'installation automatique
##### Windows
Double-cliquez sur le fichier **`setup.bat`**. 
##### Mac / Linux
Ouvrez votre terminal dans le dossier et tapez :
```bash
chmod +x setup.sh && ./setup.sh
```

---

# Utilisation Quotidienne

### 🚀 Lancement Rapide (Recommandé)
##### Windows
Double-cliquez simplement sur le fichier **`run.bat`**.
##### Mac / Linux
Ouvrez votre terminal dans le dossier et tapez :
```bash
chmod +x run.sh && ./run.sh
```

---

# Gestion des horaires (PDF)

### Synchronisation Automatique 
Plus besoin de télécharger les PDFs manuellement ! 
1. Allez sur l'interface : [http://localhost:8000](http://localhost:8000)
2. Utilisez le bouton **"SYNCHRONISER L'HORAIRE ÉTS"** en haut de la page.
3. L'application va télécharger tous les horaires du site de l'ÉTS et remplir la base de données automatiquement.

> **⚠️ NOTE IMPORTANTE (DÉPANNAGE)** : 
> Si vous rencontrez l’erreur `No module named 'requests'` lors de la synchronisation, ouvrez un terminal dans le dossier du projet et suivez ces étapes :
>
> ```powershell
> .\venv\Scripts\activate
> pip install requests beautifulsoup4
> python -m uvicorn app.main:app --reload
> ```

<img width="2305" height="490" alt="image" src="https://github.com/user-attachments/assets/4ac4fda5-823d-4226-a977-96bd256a1897" />

---

# 🔄 Nouvelle Session (Nettoyage & Sync)

Pour préparer l'application à une nouvelle session (ex: passage de l'Automne à l'Hiver), tout est automatisé directement dans l'interface web :

### 1. Vider les anciennes données
*   **Via l'Interface** : Cliquez sur le bouton **"NETTOYER LA SESSION"** en haut de la page. Cela supprimera tous les anciens horaires et locaux.
*   **Manuellement** : Supprimez le fichier `ets_rooms.db` et videz le dossier `data/uploads/`.

### 2. Synchroniser les nouveaux horaires
*   **Via l'Interface** : Cliquez sur le bouton **"SYNCHRONISER L'HORAIRE ÉTS"**. L'application s'occupe de tout : téléchargement, analyse et importation.

### 3. Vérification
*   L'application affichera alors uniquement les locaux basés sur les nouveaux fichiers téléchargés.
