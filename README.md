# Projet PostgreSQL + Python : Gestion académique

Ce projet charge les fichiers CSV fournis dans une base PostgreSQL normalisée.

## 1) Structure fonctionnelle
Tables :
- `type_matiere`
- `type_evaluation`
- `enseignant`
- `etudiant`
- `matiere`
- `note`

Relations :
- une `matiere` appartient à un `type_matiere`
- une `matiere` est enseignée par un `enseignant`
- une `note` référence un `etudiant`, une `matiere`, et un `type_evaluation`

## 2) Pré-requis
- Docker et Docker Compose
- Python 3.11+
- Les fichiers CSV dans le dossier `data/`

## 3) Lancer en local avec Docker
```bash
docker compose up -d --build
```

Cela démarre :
- PostgreSQL
- pgAdmin
- un conteneur Python qui initialise la base puis charge les données

## 4) Accès
PostgreSQL :
- host: localhost
- port: 5432
- database: school_db
- user: postgres
- password: postgres

pgAdmin :
- http://localhost:8080
- email: admin@example.com
- password: admin

## 5) Exécuter sans Docker
Créer un environnement :
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Définir les variables :
```bash
# Windows PowerShell
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="school_db"
$env:DB_USER="postgres"
$env:DB_PASSWORD="postgres"
```

Puis lancer :
```bash
python scripts/load_data.py
```

## 6) Vérifications SQL
```sql
SELECT COUNT(*) FROM scolarite.enseignant;
SELECT COUNT(*) FROM scolarite.etudiant;
SELECT COUNT(*) FROM scolarite.matiere;
SELECT COUNT(*) FROM scolarite.note;
```

## 7) Requêtes utiles
Moyenne par étudiant :
```sql
SELECT
    e.id_etudiant,
    e.nom_etudiant,
    e.pren_etudiant,
    ROUND(AVG(n.nb_note), 2) AS moyenne
FROM scolarite.note n
JOIN scolarite.etudiant e ON e.id_etudiant = n.id_etudiant
GROUP BY 1,2,3
ORDER BY moyenne DESC;
```

Moyenne pondérée par coefficient :
```sql
SELECT
    e.id_etudiant,
    e.nom_etudiant,
    e.pren_etudiant,
    ROUND(SUM(n.nb_note * m.nb_coef)::numeric / NULLIF(SUM(m.nb_coef), 0), 2) AS moyenne_ponderee
FROM scolarite.note n
JOIN scolarite.etudiant e ON e.id_etudiant = n.id_etudiant
JOIN scolarite.matiere m ON m.cd_matiere = n.cd_matiere
GROUP BY 1,2,3
ORDER BY moyenne_ponderee DESC;
```

## 8) Déploiement
Deux options simples :

### Option A — Base PostgreSQL managée
Déployer la base sur un service PostgreSQL managé, puis définir les variables d'environnement :
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

Ensuite lancer :
```bash
python scripts/load_data.py
```

### Option B — Serveur VPS
Installer Docker sur le serveur puis :
```bash
docker compose up -d --build
```

## 9) Points techniques importants
- Les CSV utilisent le séparateur `|`
- La date `DT_NOTE` est convertie en type `DATE`
- La table `note` utilise une clé primaire composite
- Les contraintes de clés étrangères protègent l'intégrité référentielle