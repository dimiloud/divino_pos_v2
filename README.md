# Divino POS v2

Système de Point de Vente moderne développé avec Django

## Installation

```bash
# Cloner le projet
git clone https://github.com/dimiloud/divino_pos_v2.git
cd divino_pos_v2

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

1. Copier le fichier .env.example vers .env
2. Configurer les variables d'environnement
3. Exécuter les migrations
4. Créer un superuser

## Développement

```bash
python manage.py runserver
```

## Tests

```bash
python manage.py test
```