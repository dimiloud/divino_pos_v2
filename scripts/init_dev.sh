#!/bin/bash

# Script d'initialisation pour l'environnement de développement

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installé."
    exit 1
}

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement
cp .env.example .env

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Charger les données de test
python manage.py loaddata fixtures/demo_data.json

echo "Installation terminée !"
