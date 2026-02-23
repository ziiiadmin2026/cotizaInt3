# 🚀 Despliegue desde GitHub
## Sistema de Cotización - Servidor Debian 10.10.1.211

**Repositorio:** https://github.com/ziiiadmin2026/cotizaInt3

---

## ✅ PRE-REQUISITO: Docker ya instalado

```bash
docker --version
docker compose version
```

---

## 🎯 DESPLIEGUE RÁPIDO (Método GitHub)

### Paso 1: En el Servidor Debian

```bash
# Conectar al servidor
ssh root@10.10.1.211

# Instalar git si no está
apt install -y git python3 nano

# Clonar repositorio
cd /opt
git clone https://github.com/ziiiadmin2026/cotizaInt3.git cotizador
cd cotizador
```

### Paso 2: Transferir Base de Datos Actual

**Desde Windows PowerShell:**

```powershell
cd D:\Proyecto5Init(CotizadorLocal)

# Crear directorio data en el servidor
ssh root@10.10.1.211 "mkdir -p /opt/cotizador/data"

# Transferir base de datos
scp cotizaciones.db root@10.10.1.211:/opt/cotizador/data/cotizaciones.db

# Transferir uploads y pdfs (si existen)
scp -r uploads root@10.10.1.211:/opt/cotizador/
scp -r pdfs root@10.10.1.211:/opt/cotizador/
```

### Paso 3: Configurar en el Servidor

```bash
# En el servidor
cd /opt/cotizador

# Crear estructura de directorios
mkdir -p data logs pdfs uploads/productos static/images

# Asignar permisos
chmod -R 755 data logs pdfs uploads static

# Configurar variables de entorno
cp .env.example .env
nano .env
```

**Configurar en .env:**

```env
SECRET_KEY=<generar_con_comando_abajo>
SMTP_EMAIL=contacto@integracional3.com.mx
SMTP_PASSWORD=tu_contraseña_smtp_real
BASE_URL=http://10.10.1.211:5000
FLASK_ENV=production
DATABASE_PATH=data/cotizaciones.db
```

**Generar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Paso 4: Desplegar

```bash
# Dar permisos a scripts
chmod +x deploy.sh backup.sh

# Desplegar
./deploy.sh

# O manualmente:
docker compose build
docker compose up -d
```

### Paso 5: Verificar

```bash
# Ver estado
docker compose ps

# Ver logs
docker compose logs -f web

# Health check
curl http://localhost:5000/api/clientes
```

**Acceder desde navegador:** http://10.10.1.211:5000

---

## 🔄 ACTUALIZAR DESDE GITHUB

Cuando hagas cambios en el repositorio:

```bash
cd /opt/cotizador

# Backup de base de datos
cp data/cotizaciones.db data/cotizaciones.db.backup

# Actualizar código
git pull

# Reconstruir y reiniciar
docker compose down
docker compose build
docker compose up -d

# Ver logs
docker compose logs -f web
```

---

## 📦 MÉTODO ALTERNATIVO: Transferencia Completa desde Windows

Si prefieres copiar todo desde tu PC en lugar de clonar de GitHub:

```powershell
cd D:\Proyecto5Init(CotizadorLocal)

# Script automatizado que incluye BD
.\transfer_to_server.ps1

# O manual (incluye base de datos)
scp -r docker-compose.yml Dockerfile gunicorn_config.py nginx.conf app.py config.py database.py email_sender.py pdf_generator.py requirements.txt .env.example deploy.sh backup.sh static templates cotizaciones.db uploads pdfs root@10.10.1.211:/opt/cotizador/
```

Luego en el servidor:
```bash
cd /opt/cotizador
mkdir -p data
mv cotizaciones.db data/
cp .env.example .env
nano .env
chmod +x deploy.sh
./deploy.sh
```

---

## 🔐 BACKUP DE PRODUCCIÓN

Configurar backups automáticos:

```bash
# Probar backup
cd /opt/cotizador
./backup.sh

# Configurar cron (backup diario a las 2 AM)
crontab -e

# Agregar:
0 2 * * * /opt/cotizador/backup.sh >> /var/log/cotizador_backup.log 2>&1
```

---

## 📊 Comandos de Gestión

```bash
# Ver logs
docker compose logs -f web

# Reiniciar
docker compose restart

# Detener
docker compose down

# Iniciar
docker compose up -d

# Estado
docker compose ps

# Reconstruir
docker compose build --no-cache
```

---

## 🔒 Seguridad Básica

```bash
# Firewall
apt install -y ufw
ufw allow 22/tcp
ufw allow 5000/tcp
ufw enable
```

---

## ✅ Checklist Final

- [ ] Docker instalado y funcionando
- [ ] Repositorio clonado en /opt/cotizador
- [ ] Base de datos transferida a data/cotizaciones.db
- [ ] Uploads y PDFs transferidos
- [ ] Archivo .env configurado
- [ ] ./deploy.sh ejecutado
- [ ] Aplicación accesible en http://10.10.1.211:5000
- [ ] Backups configurados

---

## 🆘 Solución de Problemas

### Base de datos no encontrada
```bash
ls -la /opt/cotizador/data/
# Debe mostrar cotizaciones.db
```

### Error de permisos
```bash
chown -R 1000:1000 /opt/cotizador/data
chmod -R 755 /opt/cotizador
```

### Ver logs detallados
```bash
docker compose logs --tail=200 web
tail -f logs/error.log
```

---

## 📞 Contacto

**Integrational3**  
Email: contacto@integracional3.com.mx  
Tel: 449 356 6356

---

**¡Sistema listo para producción!** 🎉
