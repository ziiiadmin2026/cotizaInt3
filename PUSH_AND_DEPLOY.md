# 🚀 PASOS COMPLETOS: Push a GitHub y Deploy

## 📤 PASO 1: Subir Código a GitHub

### En Windows PowerShell:

```powershell
cd D:\Proyecto5Init(CotizadorLocal)

# Ejecutar script de push
.\push_to_github.ps1
```

**O manualmente:**

```powershell
# Inicializar git (si no existe)
git init
git branch -M main

# Configurar remote
git remote add origin https://github.com/ziiiadmin2026/cotizaInt3.git

# Agregar archivos
git add .

# Commit
git commit -m "Initial commit - Sistema de Cotización Integrational3"

# Push (te pedirá usuario y token)
git push -u origin main
```

### ⚠️ Autenticación en GitHub

Si te pide usuario/contraseña:
- **Usuario**: ziiiadmin2026
- **Contraseña**: Usar un Personal Access Token (no la contraseña normal)

**Crear token:**
1. Ve a: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Selecciona: `repo` (full control)
4. Genera y copia el token
5. Úsalo como contraseña

---

## 🐳 PASO 2: Desplegar en Servidor Debian

### A. Conectar al Servidor

```bash
ssh root@10.10.1.211
```

### B. Clonar Repositorio

```bash
# Instalar git
apt install -y git python3 nano

# Clonar
cd /opt
git clone https://github.com/ziiiadmin2026/cotizaInt3.git cotizador
cd cotizador

# Crear directorios
mkdir -p data logs pdfs uploads/productos static/images
chmod -R 755 data logs pdfs uploads static
```

### C. Transferir Base de Datos (desde Windows)

```powershell
cd D:\Proyecto5Init(CotizadorLocal)

# Transferir BD
scp cotizaciones.db root@10.10.1.211:/opt/cotizador/data/

# Transferir uploads (si existen)
scp -r uploads root@10.10.1.211:/opt/cotizador/

# Transferir PDFs (si existen)
scp -r pdfs root@10.10.1.211:/opt/cotizador/
```

### D. Configurar Variables de Entorno (en servidor)

```bash
cd /opt/cotizador

# Copiar plantilla
cp .env.example .env

# Generar SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"

# Editar .env
nano .env
```

**Configurar estos valores:**
```env
SECRET_KEY=<pegar_resultado_del_comando_anterior>
SMTP_EMAIL=contacto@integracional3.com.mx
SMTP_PASSWORD=tu_contraseña_smtp_real
BASE_URL=http://10.10.1.211:5000
FLASK_ENV=production
DATABASE_PATH=data/cotizaciones.db
```

Guardar: `Ctrl+O`, `Enter`, `Ctrl+X`

### E. Verificar Base de Datos

```bash
# Verificar que la BD está en el lugar correcto
ls -la /opt/cotizador/data/cotizaciones.db

# Debe mostrar el archivo
```

### F. Desplegar Docker

```bash
# Dar permisos
chmod +x deploy.sh backup.sh

# Desplegar
./deploy.sh
```

**O manualmente:**
```bash
docker compose build
docker compose up -d
```

### G. Verificar

```bash
# Ver estado
docker compose ps

# Ver logs
docker compose logs -f web

# Health check
curl http://localhost:5000/api/clientes
```

---

## 🌐 PASO 3: Acceder a la Aplicación

Abrir navegador: **http://10.10.1.211:5000**

---

## 🔄 Actualizar en el Futuro

Cuando hagas cambios:

**1. Desde Windows, subir cambios:**
```powershell
cd D:\Proyecto5Init(CotizadorLocal)
git add .
git commit -m "Descripción de cambios"
git push
```

**2. En el servidor, actualizar:**
```bash
cd /opt/cotizador
git pull
docker compose down
docker compose build
docker compose up -d
```

---

## 📋 Checklist Completo

- [ ] Código subido a GitHub
- [ ] Servidor conectado vía SSH
- [ ] Docker instalado en servidor
- [ ] Repositorio clonado en /opt/cotizador
- [ ] Base de datos transferida a data/cotizaciones.db
- [ ] Archivo .env configurado con credenciales reales
- [ ] ./deploy.sh ejecutado exitosamente
- [ ] docker compose ps muestra contenedores corriendo
- [ ] curl http://localhost:5000/api/clientes responde OK
- [ ] Navegador abre http://10.10.1.211:5000

---

## 🆘 Solución de Problemas

### Error al hacer push a GitHub
```powershell
# Verificar remote
git remote -v

# Verificar branch
git branch

# Ver status
git status
```

### Base de datos no encontrada en servidor
```bash
# Verificar ubicación
find /opt/cotizador -name "cotizaciones.db"

# Transferir de nuevo si es necesario
# (desde Windows)
scp cotizaciones.db root@10.10.1.211:/opt/cotizador/data/
```

### Error de permisos
```bash
chown -R 1000:1000 /opt/cotizador/data
chmod 644 /opt/cotizador/data/cotizaciones.db
```

### Ver logs detallados
```bash
docker compose logs --tail=200 web
tail -f /opt/cotizador/logs/error.log
```

---

## 📞 Contacto

**Integrational3**  
Email: contacto@integracional3.com.mx  
Tel: 449 356 6356

---

**¡Todo listo para producción!** 🎉
