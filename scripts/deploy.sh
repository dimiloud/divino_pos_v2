#!/bin/bash

# Variables d'environnement
EXPORT $(cat .env | xargs)

# Mise à jour du code
echo "Pulling latest changes..."
git pull origin main

# Installation des dépendances
echo "Installing dependencies..."
pip install -r requirements.txt

# Migrations de la base de données
echo "Running migrations..."
python manage.py migrate

# Collecte des fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Redémarrage des services
echo "Restarting services..."
docker-compose up -d --build

echo "Deployment complete!"