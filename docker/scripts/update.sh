#!/bin/bash
# PediAssist Update Script

echo "Updating PediAssist..."

# Pull latest code
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "PediAssist updated successfully!"
