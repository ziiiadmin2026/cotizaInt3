#!/bin/bash
# Script de instalación rápida en servidor Debian virgen
# Sistema de Cotización - Integrational3
# Ejecutar como root

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}Sistema de Cotización - Integrational3${NC}"
echo -e "${CYAN}Instalación Rápida en Debian${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Verificar que somos root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Por favor ejecuta como root o con sudo${NC}"
    exit 1
fi

echo -e "${GREEN}1. Actualizando sistema...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}2. Instalando herramientas básicas...${NC}"
apt install -y curl wget git nano sudo ca-certificates gnupg apt-transport-https lsb-release unzip

echo -e "${GREEN}3. Instalando Docker...${NC}"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker
systemctl start docker

echo -e "${GREEN}4. Verificando instalación de Docker...${NC}"
docker --version
docker compose version

echo -e "${GREEN}5. Creando estructura de directorios...${NC}"
mkdir -p /opt/cotizador
cd /opt/cotizador

echo -e "${GREEN}6. Instalando Python (para scripts de utilidad)...${NC}"
apt install -y python3 python3-pip

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}✅ Servidor preparado exitosamente!${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo ""
echo "1. Transferir proyecto desde Windows:"
echo "   PowerShell> cd D:\Proyecto5Init(CotizadorLocal)"
echo "   PowerShell> .\transfer_to_server.ps1"
echo ""
echo "2. Configurar variables de entorno:"
echo "   cd /opt/cotizador"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "3. Desplegar:"
echo "   chmod +x deploy.sh"
echo "   ./deploy.sh"
echo ""
echo -e "${CYAN}============================================${NC}"
echo ""
