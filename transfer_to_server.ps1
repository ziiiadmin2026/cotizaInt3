# Script PowerShell para transferir proyecto al servidor Debian
# Sistema de Cotización - Integrational3

param(
    [string]$ServerIP = "10.10.1.211",
    [string]$User = "root",
    [string]$DestPath = "/opt/cotizador"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Transfer to Debian Server" -ForegroundColor Cyan
Write-Host "Destination: $User@$ServerIP:$DestPath" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "app.py")) {
    Write-Host "Error: No estás en el directorio del proyecto" -ForegroundColor Red
    Write-Host "Ejecuta desde: D:\Proyecto5Init(CotizadorLocal)" -ForegroundColor Yellow
    exit 1
}

# Archivos y directorios a transferir
$includeItems = @(
    ".dockerignore",
    ".env.example",
    ".gitignore",
    "app.py",
    "backup.sh",
    "config.py",
    "database.py",
    "deploy.sh",
    "docker-compose.yml",
    "Dockerfile",
    "email_sender.py",
    "gunicorn_config.py",
    "nginx.conf",
    "pdf_generator.py",
    "requirements.txt",
    "verify_deployment.py",
    "migrate_to_docker.py",
    "static",
    "templates",
    "uploads",
    "pdfs",
    "cotizaciones.db",
    "DEPLOYMENT.md",
    "DOCKER_README.md",
    "DOCKER_SETUP.md",
    "INSTALL_DEBIAN.md",
    "README.md"
)

Write-Host "Preparando archivos para transferir..." -ForegroundColor Green

# Crear directorio temporal
$tempDir = "temp_transfer"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copiar archivos seleccionados
foreach ($item in $includeItems) {
    if (Test-Path $item) {
        $destItem = Join-Path $tempDir $item
        $destItemDir = Split-Path -Parent $destItem
        
        if ($destItemDir -and -not (Test-Path $destItemDir)) {
            New-Item -ItemType Directory -Path $destItemDir -Force | Out-Null
        }
        
        if (Test-Path $item -PathType Container) {
            Copy-Item -Path $item -Destination $destItem -Recurse -Force
        } else {
            Copy-Item -Path $item -Destination $destItem -Force
        }
        Write-Host "  ✓ $item" -ForegroundColor Gray
    }
}

Write-Host "`nTransfiriendo archivos al servidor..." -ForegroundColor Green
Write-Host "(Se te pedirá la contraseña del servidor)`n" -ForegroundColor Yellow

# Transferir usando SCP
try {
    # Crear directorio en el servidor si no existe
    Write-Host "Creando directorio en el servidor..." -ForegroundColor Gray
    ssh "$User@$ServerIP" "mkdir -p $DestPath"
    
    # Transferir archivos
    Write-Host "Copiando archivos..." -ForegroundColor Gray
    scp -r "$tempDir/*" "$User@$ServerIP`:$DestPath/"
    
    Write-Host "`n✅ Transferencia completada exitosamente!" -ForegroundColor Green
    
    # Limpiar
    Remove-Item -Recurse -Force $tempDir
    
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "Próximos pasos en el servidor:" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "ssh $User@$ServerIP" -ForegroundColor White
    Write-Host "cd $DestPath" -ForegroundColor White
    Write-Host "cp .env.example .env" -ForegroundColor White
    Write-Host "nano .env  # Configurar variables" -ForegroundColor White
    Write-Host "chmod +x deploy.sh" -ForegroundColor White
    Write-Host "./deploy.sh" -ForegroundColor White
    Write-Host "`nO ver: INSTALL_DEBIAN.md para guía completa" -ForegroundColor Yellow
    Write-Host "============================================`n" -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ Error durante la transferencia: $_" -ForegroundColor Red
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    exit 1
}
