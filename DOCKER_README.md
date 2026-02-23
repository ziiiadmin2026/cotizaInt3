# 🐳 Docker Quick Start

Sistema de Cotización - Integrational3

## Inicio Rápido

### 1. Configurar Variables de Entorno
```bash
cp .env.example .env
nano .env  # Editar con tus credenciales
```

### 2. Desplegar

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```powershell
.\deploy.ps1 -Build
```

**Manual:**
```bash
docker compose up -d
```

## Acceso
- **Aplicación**: http://localhost:5000
- **Nginx** (opcional): http://localhost

## Comandos Útiles

```bash
# Ver logs
docker compose logs -f web

# Reiniciar
docker compose restart

# Detener
docker compose down

# Ver estado
docker compose ps

# Reconstruir
docker compose build --no-cache
```

## Documentación Completa
Ver [DEPLOYMENT.md](DEPLOYMENT.md) para guía completa de despliegue en producción.

## Estructura de Volúmenes

- `./data` - Base de datos SQLite
- `./pdfs` - PDFs generados
- `./uploads` - Archivos subidos
- `./logs` - Logs de la aplicación

## Soporte
**Email**: contacto@integracional3.com.mx  
**Tel**: 449 356 6356
