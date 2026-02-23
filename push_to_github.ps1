# Script PowerShell para hacer push inicial al repositorio
# https://github.com/ziiiadmin2026/cotizaInt3

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Push Inicial a GitHub" -ForegroundColor Cyan
Write-Host "Repositorio: ziiiadmin2026/cotizaInt3" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "app.py")) {
    Write-Host "Error: No estás en el directorio del proyecto" -ForegroundColor Red
    exit 1
}

# Verificar si git está instalado
try {
    git --version | Out-Null
} catch {
    Write-Host "Error: Git no está instalado" -ForegroundColor Red
    Write-Host "Descarga e instala Git desde: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "Preparando archivos para GitHub..." -ForegroundColor Green

# Inicializar git si no existe
if (-not (Test-Path ".git")) {
    Write-Host "Inicializando repositorio Git..." -ForegroundColor Yellow
    git init
    git branch -M main
}

# Configurar remote
Write-Host "Configurando remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/ziiiadmin2026/cotizaInt3.git

# Verificar .gitignore existe
if (-not (Test-Path ".gitignore")) {
    Write-Host "Error: .gitignore no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "`nArchivos a subir:" -ForegroundColor Cyan
Write-Host "  ✓ Código fuente (app.py, config.py, database.py, etc.)" -ForegroundColor Gray
Write-Host "  ✓ Configuración Docker (Dockerfile, docker-compose.yml)" -ForegroundColor Gray
Write-Host "  ✓ Scripts de despliegue (deploy.sh, backup.sh)" -ForegroundColor Gray
Write-Host "  ✓ Frontend (static/, templates/)" -ForegroundColor Gray
Write-Host "  ✓ Documentación (README.md, DEPLOYMENT.md, etc.)" -ForegroundColor Gray
Write-Host "`n  ✗ Base de datos (excluida - se transfiere aparte)" -ForegroundColor Red
Write-Host "  ✗ Archivos locales (venv/, __pycache__, .env)" -ForegroundColor Red
Write-Host ""

# Agregar archivos
Write-Host "Agregando archivos al repositorio..." -ForegroundColor Green
git add .

# Mostrar status
Write-Host "`nArchivos que se subirán:" -ForegroundColor Yellow
git status --short

Write-Host "`n¿Continuar con el commit y push? (S/N): " -ForegroundColor Yellow -NoNewline
$confirmation = Read-Host

if ($confirmation -ne 'S' -and $confirmation -ne 's') {
    Write-Host "Operación cancelada" -ForegroundColor Yellow
    exit 0
}

# Commit
Write-Host "`nCreando commit..." -ForegroundColor Green
git commit -m "Initial commit - Sistema de Cotización Integrational3

- Backend Flask con Python
- Sistema de cotizaciones con PDF
- Envío de emails SMTP
- Frontend HTML/CSS/JS
- Docker con Gunicorn para producción
- Configuración para Debian/Ubuntu
- Documentación completa de despliegue
"

# Push
Write-Host "Subiendo a GitHub..." -ForegroundColor Green
Write-Host "(Se te pedirá tu usuario y token de GitHub)`n" -ForegroundColor Yellow

try {
    git push -u origin main
    
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "✅ Código subido exitosamente a GitHub!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "`nRepositorio: https://github.com/ziiiadmin2026/cotizaInt3" -ForegroundColor White
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. Desplegar en el servidor Debian" -ForegroundColor White
    Write-Host "   Ver: DEPLOY_FROM_GITHUB.md" -ForegroundColor Gray
    Write-Host "`n2. Transferir base de datos:" -ForegroundColor White
    Write-Host "   scp cotizaciones.db root@10.10.1.211:/opt/cotizador/data/" -ForegroundColor Gray
    Write-Host "============================================`n" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error al hacer push: $_" -ForegroundColor Red
    Write-Host "`nSi el error es de autenticación:" -ForegroundColor Yellow
    Write-Host "1. Ve a GitHub Settings > Developer settings > Personal access tokens" -ForegroundColor White
    Write-Host "2. Genera un token con permisos 'repo'" -ForegroundColor White
    Write-Host "3. Usa el token como contraseña al hacer push" -ForegroundColor White
    exit 1
}
