#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/divino_pos"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="divino_pos_db_1"

# Créer le répertoire de backup s'il n'existe pas
mkdir -p $BACKUP_DIR

# Backup de la base de données
echo "Backing up database..."
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Backup des fichiers media
echo "Backing up media files..."
tar -zcf $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz media/

# Suppression des vieux backups (plus de 7 jours)
find $BACKUP_DIR -name "*backup_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*backup_*.tar.gz" -mtime +7 -delete

echo "Backup complete!"
echo "Files saved in $BACKUP_DIR"