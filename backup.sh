#!/bin/bash
# Script de Backup
# Sistema de Cotización - Integrational3

# Configuración
BACKUP_DIR="/backups/cotizador"
APP_DIR="/opt/cotizador"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "Sistema de Cotización - Backup"
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"
echo ""

# Crear directorio de backup si no existe
mkdir -p $BACKUP_DIR

# Backup de base de datos
echo -e "${GREEN}Respaldando base de datos...${NC}"
if [ -f "$APP_DIR/data/cotizaciones.db" ]; then
    cp "$APP_DIR/data/cotizaciones.db" "$BACKUP_DIR/db_$DATE.db"
    echo "✓ Base de datos respaldada: db_$DATE.db"
else
    echo -e "${YELLOW}⚠ Base de datos no encontrada${NC}"
fi

# Backup de uploads
echo -e "${GREEN}Respaldando archivos subidos...${NC}"
if [ -d "$APP_DIR/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$APP_DIR" uploads/
    echo "✓ Uploads respaldados: uploads_$DATE.tar.gz"
fi

# Backup de PDFs
echo -e "${GREEN}Respaldando PDFs...${NC}"
if [ -d "$APP_DIR/pdfs" ]; then
    tar -czf "$BACKUP_DIR/pdfs_$DATE.tar.gz" -C "$APP_DIR" pdfs/
    echo "✓ PDFs respaldados: pdfs_$DATE.tar.gz"
fi

# Backup de configuración
echo -e "${GREEN}Respaldando configuración...${NC}"
if [ -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env" "$BACKUP_DIR/env_$DATE.txt"
    echo "✓ Configuración respaldada: env_$DATE.txt"
fi

# Limpiar backups antiguos
echo ""
echo -e "${GREEN}Limpiando backups antiguos (>$RETENTION_DAYS días)...${NC}"
find "$BACKUP_DIR" -name "*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.txt" -mtime +$RETENTION_DAYS -delete
echo "✓ Limpieza completada"

# Resumen
echo ""
echo "============================================"
echo "Backup completado exitosamente"
echo "Ubicación: $BACKUP_DIR"
echo "============================================"
echo ""

# Mostrar tamaño del backup
echo "Tamaño de backups:"
du -sh $BACKUP_DIR
echo ""
