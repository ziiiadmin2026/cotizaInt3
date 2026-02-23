# PowerShell Script para Despliegue en Windows
# Sistema de Cotización - Integrational3

param(
    [switch]$Build,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Logs,
    [switch]$Status
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Sistema de Cotización - Integrational3" -ForegroundColor Cyan
Write-Host "Script de Despliegue Docker" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Verificar Docker
try {
    docker --version | Out-Null
    docker-compose --version | Out-Null
} catch {
    Write-Host "Error: Docker o Docker Compose no están instalados" -ForegroundColor Red
    exit 1
}

# Verificar archivo .env
if (-not (Test-Path .env)) {
    Write-Host "Advertencia: No se encontró archivo .env" -ForegroundColor Yellow
    Write-Host "Copiando .env.example a .env..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "IMPORTANTE: Edita el archivo .env con tus credenciales" -ForegroundColor Red
    exit 1
}

# Crear directorios necesarios
Write-Host "Creando directorios necesarios..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path data, logs, pdfs, "uploads\productos", "static\images" | Out-Null

# Función para construir
function Build-Docker {
    Write-Host "Construyendo imagen Docker..." -ForegroundColor Green
    docker-compose build --no-cache
}

# Función para iniciar
function Start-Docker {
    Write-Host "Iniciando servicios..." -ForegroundColor Green
    docker-compose up -d
    Start-Sleep -Seconds 5
    docker-compose ps
    
    Write-Host "`nVerificando salud del servicio..." -ForegroundColor Green
    Start-Sleep -Seconds 3
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/clientes" -UseBasicParsing -TimeoutSec 5
        Write-Host "✓ Servicio funcionando correctamente" -ForegroundColor Green
    } catch {
        Write-Host "⚠ El servicio puede estar iniciando. Verifica los logs:" -ForegroundColor Yellow
        Write-Host "  docker-compose logs -f web" -ForegroundColor Yellow
    }
}

# Función para detener
function Stop-Docker {
    Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
    docker-compose down
}

# Función para reiniciar
function Restart-Docker {
    Stop-Docker
    Start-Docker
}

# Función para ver logs
function Show-Logs {
    docker-compose logs -f web
}

# Función para ver estado
function Show-Status {
    docker-compose ps
}

# Ejecutar según parámetros
if ($Build) {
    Build-Docker
    Start-Docker
} elseif ($Start) {
    Start-Docker
} elseif ($Stop) {
    Stop-Docker
} elseif ($Restart) {
    Restart-Docker
} elseif ($Logs) {
    Show-Logs
} elseif ($Status) {
    Show-Status
} else {
    Write-Host "Uso del script:" -ForegroundColor Cyan
    Write-Host "  .\deploy.ps1 -Build     # Construir e iniciar" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Start     # Iniciar servicios" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Stop      # Detener servicios" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Restart   # Reiniciar servicios" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Logs      # Ver logs" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Status    # Ver estado" -ForegroundColor White
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Comandos útiles:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f web  # Ver logs en tiempo real" -ForegroundColor White
Write-Host "  docker-compose ps           # Ver estado de contenedores" -ForegroundColor White
Write-Host "  docker-compose restart      # Reiniciar servicios" -ForegroundColor White
Write-Host "============================================`n" -ForegroundColor Cyan
