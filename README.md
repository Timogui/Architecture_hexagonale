# FestiPlan — Architecture Hexagonale & Domain-Driven Design (DDD)

API de gestion du festival metal fictif **Hellforge Open Air**. Ce projet a été refactorisé d'une architecture monolithique legacy vers une **Architecture Hexagonale (Ports & Adaptateurs)** respectant les principes du **Domain-Driven Design (DDD)**.

---

## 🏛️ Architecture du Projet

L'application respecte strictement le principe d'inversion des dépendances : le cœur métier est 100% indépendant de tout framework technique (ni FastAPI, ni SQLAlchemy dans le domaine).

```
app/
├── domain/                      # Cœur Métier (Python pur : zéro framework)
│   ├── entities/                # Festival, Concert, Stage, Artist, Incident
│   ├── value_objects/           # TimeSlot, DateRange, EquipmentSet
│   ├── exceptions.py            # Exceptions métier (DomainError, ConcertConflictError...)
│   └── events.py                # Événements de domaine (ConcertRescheduled...)
│
├── application/                 # Orchestration Applicative
│   ├── ports/                   # Contrats abstraits (Repositories, Notification, UnitOfWork)
│   ├── use_cases/               # Cas d'utilisation (RescheduleConcert, PublishFestival...)
│   └── dtos.py                  # Objets de transfert et commandes
│
├── adapters/                    # Connecteurs vers les technologies
│   ├── inbound/api/             # Contrôleurs HTTP FastAPI (Primary Adapters)
│   └── outbound/                # Adaptateurs secondaires (Driven Adapters)
│       ├── persistence/         # Repositories SQLAlchemy & UnitOfWork
│       └── notifications/       # Adaptateur de notification email
│
├── dependencies.py              # Composition Root & Injection de dépendances
├── database.py                  # Configuration SQLite & SQLAlchemy
├── models.py                    # Schémas de tables SQLAlchemy
├── schemas.py                   # Schémas de validation Pydantic
└── main.py                      # Point d'entrée de l'application FastAPI
```

Pour le détail des choix de conception, des invariants métier (R1 à R10) et les diagrammes UML (Composants et Séquence), consultez la [Note d'Architecture (NOTE_D_ARCHITECTURE.md)](NOTE_D_ARCHITECTURE.md).

---

## ⚙️ Installation & Lancement

### 1. Prérequis
- Python 3.11 ou supérieur
- PowerShell (Windows) ou Bash (Linux/macOS)

### 2. Création et activation de l'environnement virtuel
```powershell
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Sur Windows (PowerShell) :
.venv\Scripts\Activate.ps1
# Sur macOS / Linux :
source .venv/bin/activate
```

### 3. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 4. Initialisation de la base de données de démonstration
```bash
python -m app.seed
```

### 5. Démarrage de l'API
```bash
uvicorn app.main:app --reload
```
L'API est accessible sur `http://127.0.0.1:8000`.
La documentation interactive Swagger est disponible sur **`http://127.0.0.1:8000/docs`**.

---

## 🧪 Exécution des Tests

Le projet dispose d'une suite de **46 tests automatisés** couvrant le domaine, les cas d'utilisation, les adaptateurs et la non-régression des 3 défauts initiaux :

```bash
# Lancer l'ensemble des tests
pytest -v

# Lancer uniquement les tests unitaires du Domaine (Python pur, ultra rapides)
pytest tests/domain/ -v

# Lancer les tests des Cas d'Utilisation (avec doubles en mémoire)
pytest tests/application/ -v

# Lancer les tests de non-régression des 3 défauts initiaux
pytest tests/test_non_regression_defauts.py -v
```

---