# 🚀 Instalación en Debian 13 (Servidor 10.10.1.211)
## Sistema de Cotización - Integrational3

---

## 📋 PASO 1: Preparar el Servidor Debian

Conectado como root al servidor:

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar herramientas básicas
apt install -y curl wget git nano sudo ca-certificates gnupg

# Crear usuario para la aplicación (opcional pero recomendado)
useradd -m -s /bin/bash cotizador
usermod -aG sudo cotizador
passwd cotizador  # Establecer contraseña
```

---

## 📦 PASO 2: Instalar Docker en Debian 13

```bash
# Instalar dependencias
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Agregar repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Actualizar lista de paquetes
apt update

# Instalar Docker y Docker Compose
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verificar instalación
docker --version
docker compose version

# Habilitar Docker al inicio
systemctl enable docker
systemctl start docker

# Agregar usuario al grupo docker (si creaste usuario cotizador)
usermod -aG docker cotizador
```

---

## 📂 PASO 3: Transferir Proyecto desde Windows

**En tu PC Windows** (PowerShell):

```powershell
# Navegar al proyecto
cd D:\Proyecto5Init(CotizadorLocal)

# Crear archivo comprimido (excluyendo archivos innecesarios)
$exclude = @('venv', '__pycache__', '*.db', 'pdfs', 'uploads', 'logs', '.git')
Compress-Archive -Path * -DestinationPath cotizador.zip -Force

# Transferir al servidor (reemplaza la contraseña cuando te la pida)
scp cotizador.zip root@10.10.1.211:/home/cotizador/
```

**Alternativa con WinSCP o FileZilla:**
- Conectar a: 10.10.1.211
- Usuario: root (o cotizador)
- Subir todo el proyecto a: `/home/cotizador/`

---

## 🔧 PASO 4: Configurar en el Servidor

**En el servidor Debian:**

```bash
# Cambiar a usuario cotizador (si lo creaste)
su - cotizador
# O quedarte como root

# Crear directorio del proyecto
mkdir -p /opt/cotizador
cd /opt/cotizador

# Si subiste el ZIP
apt install -y unzip  # Si no está instalado
unzip /home/cotizador/cotizador.zip -d /opt/cotizador/

# O si copiaste los archivos directamente
# cp -r /home/cotizador/proyecto/* /opt/cotizador/

# Dar permisos
chmod -R 755 /opt/cotizador
cd /opt/cotizador
```

---

## ⚙️ PASO 5: Configurar Variables de Entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar configuración
nano .env
```

**Configurar estos valores:**

```env
# Generar SECRET_KEY segura
SECRET_KEY=<pegar_clave_generada_abajo>

# SMTP
SMTP_SERVER=smtp.titan.email
SMTP_PORT=587
SMTP_EMAIL=contacto@integracional3.com.mx
SMTP_PASSWORD=tu_contraseña_smtp_real

# URL del servidor
BASE_URL=http://10.10.1.211:5000
# O si tienes dominio: BASE_URL=http://cotizador.integracional3.com.mx

# Base de datos
DATABASE_PATH=data/cotizaciones.db

# Producción
FLASK_ENV=production

# Workers (ajustar según CPU del servidor)
GUNICORN_WORKERS=4

# Zona horaria
TZ=America/Mexico_City
```

**Generar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copiar la salida y pegarla en `SECRET_KEY` dentro del `.env`.

Guardar archivo: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🏗️ PASO 6: Crear Estructura de Directorios

```bash
# Crear directorios necesarios
mkdir -p data logs pdfs uploads/productos static/images

# Asignar permisos
chmod -R 755 data logs pdfs uploads static

# Crear archivos .gitkeep
touch data/.gitkeep logs/.gitkeep
```

---

## 🐳 PASO 7: Construir e Iniciar Docker

```bash
# Dar permisos al script de despliegue
chmod +x deploy.sh

# Construir e iniciar
./deploy.sh
```

**O manualmente:**

```bash
# Construir imagen
docker compose build

# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f web
```

---

## 🔍 PASO 8: Verificar Funcionamiento

```bash
# Ver estado de contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f web

# Health check
curl http://localhost:5000/api/clientes

# O desde tu PC Windows
curl http://10.10.1.211:5000/api/clientes
```

**Acceder desde navegador:**
- Abrir: http://10.10.1.211:5000

---

## 🔥 PASO 9: Configurar Firewall (Opcional pero Recomendado)

```bash
# Instalar ufw si no está
apt install -y ufw

# Configurar reglas
ufw allow 22/tcp    # SSH
ufw allow 5000/tcp  # Aplicación (o 80/443 si usas nginx)

# Habilitar firewall
ufw enable

# Ver estado
ufw status
```

---

## 🌐 PASO 10: Configurar Nginx con Dominio (Opcional)

Si quieres usar un dominio y SSL:

### Opción A: Sin SSL (HTTP simple)

**1. Editar nginx.conf:**
```bash
nano nginx.conf
```

Cambiar:
```nginx
server_name 10.10.1.211;
```

**2. Iniciar nginx:**
```bash
# Descomentar servicio nginx en docker-compose.yml
nano docker-compose.yml

# Reiniciar
docker compose down
docker compose up -d
```

**3. Abrir puerto:**
```bash
ufw allow 80/tcp
```

**4. Acceder:**
- http://10.10.1.211

### Opción B: Con SSL (HTTPS - Recomendado)

**1. Instalar Certbot:**
```bash
apt install -y certbot

# Obtener certificado (reemplaza el dominio)
certbot certonly --standalone -d cotizador.integracional3.com.mx
```

**2. Copiar certificados:**
```bash
mkdir -p /opt/cotizador/ssl
cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem /opt/cotizador/ssl/cert.pem
cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem /opt/cotizador/ssl/key.pem
chmod 600 /opt/cotizador/ssl/*.pem
```

**3. Editar nginx.conf:**
```bash
cd /opt/cotizador
nano nginx.conf
```

Descomentar líneas SSL:
```nginx
listen 443 ssl http2;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

**4. Reiniciar:**
```bash
docker compose restart nginx
```

**5. Abrir puertos:**
```bash
ufw allow 80/tcp
ufw allow 443/tcp
```

---

## 🔄 PASO 11: Configurar Backups Automáticos

```bash
# Crear directorio de backups
mkdir -p /backups/cotizador

# Dar permisos al script
chmod +x backup.sh

# Editar rutas en backup.sh
nano backup.sh

# Cambiar:
# BACKUP_DIR="/backups/cotizador"
# APP_DIR="/opt/cotizador"

# Probar backup manual
./backup.sh

# Configurar cron para backup automático
crontab -e

# Agregar línea (backup diario a las 2 AM)
0 2 * * * /opt/cotizador/backup.sh >> /var/log/cotizador_backup.log 2>&1
```

---

## 📊 Comandos de Gestión Diaria

```bash
# Ver logs
docker compose logs -f web
docker compose logs --tail=100 web

# Ver estado
docker compose ps
docker stats

# Reiniciar
docker compose restart
docker compose restart web

# Detener
docker compose down

# Iniciar
docker compose up -d

# Actualizar código (después de subir nuevos archivos)
docker compose down
docker compose build --no-cache
docker compose up -d

# Ver recursos del sistema
htop
df -h
free -h

# Acceder al contenedor
docker compose exec web bash
```

---

## 🔍 Resolución de Problemas

### Error: Puerto 5000 en uso
```bash
# Ver qué está usando el puerto
lsof -i :5000
netstat -tulpn | grep 5000

# Matar proceso
kill -9 <PID>
```

### Error: Permisos
```bash
chown -R 1000:1000 /opt/cotizador/data
chmod -R 755 /opt/cotizador
```

### Ver logs detallados
```bash
docker compose logs --tail=200 web
tail -f /opt/cotizador/logs/error.log
```

### Reconstruir completamente
```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## 📱 Acceso desde Otros Dispositivos

Una vez en funcionamiento, puedes acceder desde:

- **Red local:** http://10.10.1.211:5000
- **Con dominio:** http://tu-dominio.com
- **Con SSL:** https://tu-dominio.com

---

## 🎯 Checklist Final

- [ ] Docker instalado y funcionando
- [ ] Proyecto transferido a /opt/cotizador
- [ ] Archivo .env configurado con credenciales reales
- [ ] Directorios creados (data, logs, pdfs, uploads)
- [ ] Docker compose funcionando
- [ ] Aplicación accesible desde navegador
- [ ] Firewall configurado
- [ ] Backups automáticos configurados
- [ ] (Opcional) Nginx con SSL configurado

---

## 🆘 Soporte

Si encuentras problemas:

1. **Ver logs:**
   ```bash
   docker compose logs -f web
   ```

2. **Verificar configuración:**
   ```bash
   cat .env
   docker compose config
   ```

3. **Contacto:**
   - Email: contacto@integracional3.com.mx
   - Tel: 449 356 6356

---

**¡Listo! Tu sistema de cotización debería estar funcionando en producción.**

Accede a: **http://10.10.1.211:5000**
