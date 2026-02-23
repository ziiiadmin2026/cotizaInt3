# Guía de Despliegue en Producción
## Sistema de Cotización - Integrational3

---

## 📋 Requisitos Previos

### Servidor
- **Sistema Operativo**: Debian 11/12, Ubuntu 20.04+, o Alpine Linux
- **CPU**: Mínimo 2 cores (recomendado 4+)
- **RAM**: Mínimo 2GB (recomendado 4GB+)
- **Disco**: Mínimo 10GB libres (recomendado 20GB+)

### Software Necesario
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (para clonar el repositorio)

---

## 🚀 Instalación de Docker en Debian/Ubuntu

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar clave GPG de Docker
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar repositorio de Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalación
docker --version
docker compose version

# Agregar usuario al grupo docker (opcional)
sudo usermod -aG docker $USER
```

---

## 📥 Despliegue Inicial

### 1. Clonar o Copiar el Proyecto

```bash
# Si usas Git
git clone <url-repositorio> /opt/cotizador
cd /opt/cotizador

# O copiar archivos manualmente
scp -r proyecto_local usuario@servidor:/opt/cotizador
ssh usuario@servidor
cd /opt/cotizador
```

### 2. Configurar Variables de Entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar configuración
nano .env  # o vim .env
```

**Variables críticas a configurar:**
```env
FLASK_ENV=production
SECRET_KEY=generar-clave-segura-aleatoria-32-caracteres-minimo
BASE_URL=https://tu-dominio.com
SMTP_EMAIL=contacto@integracional3.com.mx
SMTP_PASSWORD=tu_contraseña_smtp_real
```

**Generar SECRET_KEY segura:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Crear Directorios y Permisos

```bash
# Crear directorios
mkdir -p data logs pdfs uploads/productos static/images

# Asignar permisos
chmod -R 755 data logs pdfs uploads static
```

### 4. Construir e Iniciar

#### Opción A: Usando script de despliegue (recomendado)
```bash
# Dar permisos de ejecución
chmod +x deploy.sh

# Ejecutar despliegue
./deploy.sh
```

#### Opción B: Manual con Docker Compose
```bash
# Construir imagen
docker compose build

# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f web
```

---

## 🔧 Configuración sin Nginx (Solo Flask)

Si NO quieres usar Nginx como proxy reverso:

1. **Editar docker-compose.yml** - Comentar o eliminar el servicio nginx:
```yaml
  # nginx:
  #   image: nginx:alpine
  #   ...
```

2. **Acceder directamente al puerto 5000:**
```
http://tu-servidor:5000
```

---

## 🔒 Configuración con Nginx (Recomendado para Producción)

### 1. Preparar Nginx

El archivo `nginx.conf` ya está incluido y configurado. Solo necesitas:

```bash
# Editar nginx.conf si necesitas cambiar el dominio
nano nginx.conf

# Buscar y cambiar:
server_name cotizador.integracional3.com.mx;
```

### 2. Agregar Certificado SSL (Opcional pero recomendado)

#### Opción A: Let's Encrypt con Certbot
```bash
# En el servidor, fuera de Docker
sudo apt install certbot

# Obtener certificado
sudo certbot certonly --standalone -d tu-dominio.com

# Copiar certificados al proyecto
mkdir -p ssl
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/
```

#### Opción B: Certificado propio
```bash
# Copiar tus certificados
mkdir -p ssl
cp tu-certificado.pem ssl/cert.pem
cp tu-llave-privada.pem ssl/key.pem
chmod 600 ssl/*.pem
```

### 3. Habilitar SSL en nginx.conf

Descomentar estas líneas en `nginx.conf`:
```nginx
listen 443 ssl http2;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

### 4. Reiniciar servicios
```bash
docker compose restart nginx
```

---

## 📊 Comandos de Gestión

### Ver Estado
```bash
docker compose ps
```

### Ver Logs
```bash
# Todos los servicios
docker compose logs -f

# Solo web
docker compose logs -f web

# Solo nginx
docker compose logs -f nginx

# Últimas 100 líneas
docker compose logs --tail=100 web
```

### Reiniciar Servicios
```bash
# Reiniciar todo
docker compose restart

# Reiniciar solo web
docker compose restart web
```

### Detener Servicios
```bash
docker compose down
```

### Actualizar Código
```bash
# 1. Hacer pull o copiar nuevos archivos
git pull  # o copiar archivos

# 2. Reconstruir imagen
docker compose build

# 3. Reiniciar servicios
docker compose down
docker compose up -d
```

### Acceder al Contenedor
```bash
docker compose exec web bash
```

### Ver Uso de Recursos
```bash
docker stats
```

---

## 🔍 Resolución de Problemas

### El servicio no inicia
```bash
# Ver logs detallados
docker compose logs web

# Ver errores de build
docker compose build --no-cache

# Verificar configuración
docker compose config
```

### Error de permisos
```bash
# Asignar permisos correctos
sudo chown -R 1000:1000 data/ logs/ pdfs/ uploads/
chmod -R 755 data/ logs/ pdfs/ uploads/
```

### Base de datos no se crea
```bash
# Verificar directorio data
ls -la data/

# Crear manualmente si es necesario
docker compose exec web python3 -c "from database import Database; Database()"
```

### Problemas con SMTP
```bash
# Verificar configuración
docker compose exec web python3 -c "import os; print(os.getenv('SMTP_EMAIL'))"

# Probar conexión SMTP
docker compose exec web python3 test_email_interactive.py
```

### Puerto 5000 ya en uso
```bash
# Opción 1: Cambiar puerto en docker-compose.yml
ports:
  - "8080:5000"

# Opción 2: Detener servicio que usa el puerto
sudo lsof -i :5000
sudo kill -9 <PID>
```

---

## 🔐 Seguridad en Producción

### 1. Firewall
```bash
# Permitir solo puertos necesarios
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw status
```

### 2. Actualizar Sistema Regularmente
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Backups Automáticos

Crear script de backup:
```bash
#!/bin/bash
# /opt/scripts/backup_cotizador.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/cotizador"

mkdir -p $BACKUP_DIR

# Backup de base de datos
cp /opt/cotizador/data/cotizaciones.db $BACKUP_DIR/db_$DATE.db

# Backup de uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/cotizador/uploads

# Backup de PDFs
tar -czf $BACKUP_DIR/pdfs_$DATE.tar.gz /opt/cotizador/pdfs

# Limpiar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Agregar a crontab:
```bash
# Editar crontab
crontab -e

# Agregar línea (backup diario a las 2 AM)
0 2 * * * /opt/scripts/backup_cotizador.sh
```

---

## 📈 Monitoreo

### Health Check Manual
```bash
curl http://localhost:5000/api/clientes
```

### Monitoreo de Logs en Tiempo Real
```bash
tail -f logs/access.log
tail -f logs/error.log
```

### Ver Recursos del Sistema
```bash
# CPU, RAM, Disco
htop
df -h
free -h
```

---

## 🔄 Actualización de Producción

```bash
# 1. Hacer backup
./backup.sh  # Si tienes script de backup

# 2. Descargar nueva versión
git pull

# 3. Detener servicios
docker compose down

# 4. Reconstruir
docker compose build --no-cache

# 5. Iniciar
docker compose up -d

# 6. Verificar
docker compose logs -f web
curl http://localhost:5000/api/clientes
```

---

## 📞 Soporte

Para soporte técnico, contactar:
- **Email**: contacto@integracional3.com.mx
- **Teléfono**: 449 356 6356

---

## 📝 Notas Adicionales

### Zona Horaria
El sistema está configurado en `America/Mexico_City` (UTC-6).

### Límites de Archivos
- Máximo 5 adjuntos por cotización
- Máximo 15MB por archivo
- Máximo 20MB total de adjuntos

### Usuarios por Defecto
Después del primer inicio, crear usuarios admin desde la interfaz web.

---

**Última actualización**: Febrero 2026  
**Versión**: 1.0.0  
**Integrational3** - Soluciones Tecnológicas Integrales
