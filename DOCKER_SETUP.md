# 🎯 Resumen de Archivos para Producción Docker

## ✅ Archivos Creados

### Configuración Docker
- `Dockerfile` - Imagen Docker optimizada para producción (Debian)
- `docker-compose.yml` - Orquestación de servicios (Web + Nginx)
- `.dockerignore` - Optimización de build
- `gunicorn_config.py` - Configuración de servidor WSGI para producción

### Scripts de Despliegue
- `deploy.sh` - Script de despliegue automatizado (Linux/Mac)
- `deploy.ps1` - Script de despliegue automatizado (Windows)
- `verify_deployment.py` - Verificación pre-despliegue

### Configuración y Documentación
- `.env.example` - Plantilla actualizada de variables de entorno
- `nginx.conf` - Configuración de proxy reverso (opcional)
- `DEPLOYMENT.md` - Guía completa de despliegue en producción
- `DOCKER_README.md` - Guía rápida de Docker
- `README.md` - Actualizado con sección de Docker

## 📋 Pasos para Desplegar

### 1️⃣ En Windows (Desarrollo/Pruebas)
```powershell
# Copiar configuración
cp .env.example .env

# Editar variables
notepad .env

# Verificar
python verify_deployment.py

# Desplegar
.\deploy.ps1 -Build
```

### 2️⃣ En Servidor Linux (Producción)

```bash
# 1. Instalar Docker (si no está instalado)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Copiar proyecto al servidor
scp -r proyecto/ usuario@servidor:/opt/cotizador/

# 3. En el servidor
cd /opt/cotizador
cp .env.example .env
nano .env  # Configurar variables

# 4. Verificar
python3 verify_deployment.py

# 5. Desplegar
chmod +x deploy.sh
./deploy.sh
```

## 🔑 Variables Críticas a Configurar

En el archivo `.env`:

```env
# ⚠️ IMPORTANTE - Cambiar estos valores
SECRET_KEY=generar-clave-aleatoria-segura-32-chars
SMTP_EMAIL=contacto@integrational3.com.mx
SMTP_PASSWORD=contraseña-real-smtp
BASE_URL=http://tu-dominio.com

# Opcional
GUNICORN_WORKERS=4
DATABASE_PATH=data/cotizaciones.db
```

## 🔒 Generar SECRET_KEY Segura

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 🌐 Configuración de Dominio

### Sin Nginx (Directo)
- Acceder directamente al puerto 5000
- `http://servidor:5000`

### Con Nginx (Recomendado)
- Editar `server_name` en `nginx.conf`
- Configurar DNS apuntando al servidor
- Opcional: SSL con Let's Encrypt
- Acceder en puerto 80/443

## 📊 Comandos Útiles

```bash
# Ver logs
docker compose logs -f web

# Reiniciar
docker compose restart

# Detener
docker compose down

# Reconstruir
docker compose build --no-cache

# Estado
docker compose ps

# Recursos
docker stats
```

## 🔍 Verificar Funcionamiento

```bash
# Health check
curl http://localhost:5000/api/clientes

# Ver logs
tail -f logs/access.log
tail -f logs/error.log

# Estado de contenedores
docker compose ps
```

## 📦 Estructura de Volúmenes Persistentes

```
/opt/cotizador/
├── data/              # Base de datos SQLite
├── pdfs/              # PDFs generados
├── uploads/           # Archivos subidos
│   └── productos/     # Imágenes de productos
└── logs/              # Logs de aplicación
    ├── access.log
    └── error.log
```

## 🔐 Backups Recomendados

```bash
# Backup manual
tar -czf backup_$(date +%Y%m%d).tar.gz data/ pdfs/ uploads/

# Backup automático (crontab)
0 2 * * * /opt/cotizador/backup.sh
```

## ⚡ Características de Producción

✅ **Gunicorn** - Servidor WSGI robusto  
✅ **Workers múltiples** - Manejo de concurrencia  
✅ **Health checks** - Monitoreo automático  
✅ **Logs estructurados** - Access y error logs  
✅ **Volúmenes persistentes** - Datos seguros  
✅ **Restart automático** - Alta disponibilidad  
✅ **Nginx opcional** - Proxy reverso + SSL  
✅ **Zona horaria** - America/Mexico_City configurada  

## 📞 Soporte

**Integrational3**  
Email: contacto@integrational3.com.mx  
Tel: 449 356 6356  
Web: www.integrational3.com.mx

---

**Nota**: Todos los archivos están configurados y listos para desplegar. Solo necesitas configurar las variables de entorno en `.env` antes de iniciar.
