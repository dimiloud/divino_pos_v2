# Guide de déploiement

## Configuration du serveur

1. Installer Docker et Docker Compose
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose
```

2. Configurer Nginx et SSL
```bash
# Installer Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d votre-domaine.com
```

## Déploiement

1. Cloner le projet
```bash
git clone https://github.com/dimiloud/divino_pos_v2.git
cd divino_pos_v2
```

2. Configurer les variables d'environnement
```bash
cp .env.example .env
vim .env
```

3. Démarrer l'application
```bash
docker-compose up -d
```

4. Appliquer les migrations
```bash
docker-compose exec web python manage.py migrate
```

5. Créer un superutilisateur
```bash
docker-compose exec web python manage.py createsuperuser
```

## Maintenance

### Backup
```bash
./scripts/backup.sh
```

### Restauration
```bash
./scripts/restore.sh backup_file.sql media_backup.tar.gz
```

### Mise à jour
```bash
./scripts/deploy.sh
```