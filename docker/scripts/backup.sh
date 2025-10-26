#!/bin/bash
# PediAssist Backup Script

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating backup in $BACKUP_DIR..."

# Backup database
echo "Backing up database..."
docker-compose exec postgres pg_dump -U pediassist pediassist > "$BACKUP_DIR/database.sql"

# Backup application data
echo "Backing up application data..."
docker run --rm -v pediassist_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/data.tar.gz -C /data .

# Backup configuration
echo "Backing up configuration..."
cp -r docker "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"
cp Dockerfile "$BACKUP_DIR/"

# Backup environment files
cp .env.* "$BACKUP_DIR/" 2>/dev/null || true

echo "Backup completed successfully!"
echo "Backup location: $BACKUP_DIR"
