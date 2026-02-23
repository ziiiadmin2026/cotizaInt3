# 🚀 GUÍA DE INSTALACIÓN SUPER RÁPIDA
## Servidor Debian 10.10.1.211

---

## ⚡ OPCIÓN 1: Instalación Automatizada (RECOMENDADA)

### Paso 1: En el Servidor Debian (SSH como root)

```bash
# Descargar y ejecutar script de setup
curl -fsSL https://raw.githubusercontent.com/tu-repo/setup_debian.sh -o setup_debian.sh
chmod +x setup_debian.sh
./setup_debian.sh
```

**O copiar manualmente `setup_debian.sh` y ejecutarlo:**

```bash
# En tu PC, copiar el archivo
scp setup_debian.sh root@10.10.1.211:/root/

# En el servidor
ssh root@10.10.1.211
chmod +x setup_debian.sh
./setup_debian.sh
```

### Paso 2: En Windows (PowerShell)

```powershell
cd D:\Proyecto5Init(CotizadorLocal)
.\transfer_to_server.ps1
```

### Paso 3: En el Servidor (Configurar y Desplegar)

```bash
ssh root@10.10.1.211
cd /opt/cotizador

# Configurar variables
cp .env.example .env
nano .env

# Generar SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copiar el resultado y pegarlo en SECRET_KEY dentro de .env

# Configurar SMTP_PASSWORD con tu contraseña real

# Desplegar
chmod +x deploy.sh
./deploy.sh
```

### Paso 4: Acceder

Abrir navegador: **http://10.10.1.211:5000**

---

## ⚡ OPCIÓN 2: Instalación Manual (Paso a Paso)

### A. Preparar Servidor Debian

```bash
ssh root@10.10.1.211

# Actualizar
apt update && apt upgrade -y

# Herramientas básicas
apt install -y curl git nano

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verificar
docker --version
docker compose version
```

### B. Transferir Proyecto

**En Windows PowerShell:**

```powershell
cd D:\Proyecto5Init(CotizadorLocal)

# Transferir archivos importantes
scp -r docker-compose.yml Dockerfile gunicorn_config.py app.py config.py database.py email_sender.py pdf_generator.py requirements.txt .env.example static templates root@10.10.1.211:/opt/cotizador/
```

### C. Configurar en Servidor

```bash
ssh root@10.10.1.211
cd /opt/cotizador

# Crear directorios
mkdir -p data logs pdfs uploads/productos

# Configurar variables
cp .env.example .env
nano .env
```

**Editar estos valores en .env:**
- `SECRET_KEY=` (generar con: `python3 -c "import secrets; print(secrets.token_hex(32))"`)
- `SMTP_PASSWORD=` (tu contraseña real)
- `BASE_URL=http://10.10.1.211:5000`

### D. Desplegar

```bash
# Construir
docker compose build

# Iniciar
docker compose up -d

# Ver logs
docker compose logs -f web
```

### E. Verificar

```bash
# Health check
curl http://localhost:5000/api/clientes

# Ver contenedores
docker compose ps
```

**Abrir navegador:** http://10.10.1.211:5000

---

## 🔧 Comandos Esenciales

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
```

---

## ❓ Problemas Comunes

### No puedo conectar por SSH
```bash
# Verificar que SSH está corriendo en el servidor
systemctl status sshd
```

### Puerto 5000 bloqueado
```bash
# Abrir puerto en firewall
ufw allow 5000/tcp
```

### Error de permisos
```bash
chmod -R 755 /opt/cotizador
```

---

## 📞 Siguiente Nivel: Nginx + SSL

Una vez funcionando, puedes configurar:
- Nginx como proxy reverso
- Certificado SSL gratis con Let's Encrypt
- Dominio personalizado

Ver: `INSTALL_DEBIAN.md` sección "Paso 10"

---

## ✅ Checklist Rápido

- [ ] SSH al servidor funcionando
- [ ] Docker instalado
- [ ] Proyecto transferido a /opt/cotizador
- [ ] Archivo .env configurado
- [ ] docker compose up -d ejecutado
- [ ] http://10.10.1.211:5000 abre en navegador

---

## 📚 Documentación Completa

- **Guía detallada:** `INSTALL_DEBIAN.md`
- **Comandos rápidos:** `comandos_rapidos.txt`
- **Setup completo:** `DEPLOYMENT.md`

---

**¡Listo en 5 minutos!** 🎉
