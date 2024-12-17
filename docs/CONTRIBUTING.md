# Guide de contribution

## Prérequis

- Python 3.10+
- PostgreSQL 13+
- Git

## Installation de l'environnement de développement

1. Forker le projet
2. Cloner votre fork
```bash
git clone https://github.com/votre-username/divino_pos_v2.git
```

3. Configurer l'environnement
```bash
./scripts/init_dev.sh
```

## Processus de contribution

1. Créer une branche
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

2. Développer et tester
```bash
python manage.py test
flake8
black .
```

3. Commiter les changements
```bash
git add .
git commit -m "Description claire des changements"
```

4. Pousser et créer une Pull Request

## Standards de code

- Suivre PEP 8
- Utiliser Black pour le formatage
- Écrire des tests unitaires
- Documenter le code
- Commenter en français

## Tests

```bash
# Tests unitaires
python manage.py test

# Couverture de code
coverage run manage.py test
coverage report
```