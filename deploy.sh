#!/bin/bash
# Script de despliegue del Sistema de Cotización
# Integrational3 - Production Deployment

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "Sistema de Cotización - Integrational3"
echo "Script de Despliegue Docker"
echo "============================================"
echo ""

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker no está instalado${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose no está instalado${NC}"
    exit 1
fi

# Verificar archivo .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}Advertencia: No se encontró archivo .env${NC}"
    echo -e "${YELLOW}Copiando .env.example a .env...${NC}"
    cp .env.example .env
    echo -e "${RED}IMPORTANTE: Edita el archivo .env con tus credenciales antes de continuar${NC}"
    echo -e "${YELLOW}Ejecuta: nano .env o vim .env${NC}"
    exit 1
fi

# Crear directorios necesarios
echo -e "${GREEN}Creando directorios necesarios...${NC}"
mkdir -p data logs pdfs uploads/productos static/images

# Asignar permisos
echo -e "${GREEN}Asignando permisos...${NC}"
chmod -R 755 data logs pdfs uploads static

# Construir imagen
echo -e "${GREEN}Construyendo imagen Docker...${NC}"
docker-compose build --no-cache

# Detener contenedores existentes
echo -e "${GREEN}Deteniendo contenedores existentes...${NC}"
docker-compose down

# Iniciar servicios
echo -e "${GREEN}Iniciando servicios...${NC}"
docker-compose up -d

# Esperar a que el servicio esté listo
echo -e "${GREEN}Esperando a que el servicio esté listo...${NC}"
sleep 5

# Verificar estado
echo -e "${GREEN}Verificando estado de los contenedores...${NC}"
docker-compose ps

# Health check
echo ""
echo -e "${GREEN}Verificando salud del servicio...${NC}"
sleep 3
if curl -f http://localhost:5000/api/clientes &> /dev/null; then
    echo -e "${GREEN}✓ Servicio funcionando correctamente${NC}"
else
    echo -e "${YELLOW}⚠ El servicio puede estar iniciando aún. Verifica los logs:${NC}"
    echo -e "${YELLOW}  docker-compose logs -f web${NC}"
fi

echo ""
echo "============================================"
echo -e "${GREEN}Despliegue completado!${NC}"
echo "============================================"
echo ""
echo "Accesos:"
echo "  - Aplicación: http://localhost:5000"
echo "  - Nginx (si habilitado): http://localhost"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f web"
echo "  - Reiniciar: docker-compose restart"
echo "  - Detener: docker-compose down"
echo "  - Ver estado: docker-compose ps"
echo ""
