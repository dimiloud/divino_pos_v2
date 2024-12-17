#!/bin/bash

# Demander confirmation
echo "Warning: This will overwrite your current database and media files."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Restauration de la base de données
echo "Restoring database..."
cat $1 | docker exec -i $DB_CONTAINER psql -U $DB_USER $DB_NAME

# Restauration des fichiers media
echo "Restoring media files..."
tar -xzf $2 -C .

echo "Restore complete!"
