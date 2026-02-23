# Script para subir base de datos a GitHub temporalmente
# Luego la descargarás en el servidor

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Subir Base de Datos a GitHub" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

if (-not (Test-Path "cotizaciones.db")) {
    Write-Host "Error: cotizaciones.db no encontrada" -ForegroundColor Red
    exit 1
}

Write-Host "Preparando para subir base de datos..." -ForegroundColor Green

# Crear rama temporal para la BD
Write-Host "Creando rama temporal..." -ForegroundColor Yellow
git checkout -b database-transfer

# Modificar .gitignore temporalmente para permitir .db
Write-Host "Permitiendo archivos .db temporalmente..." -ForegroundColor Yellow
(Get-Content .gitignore) -replace '^\*\.db$', '#*.db' | Set-Content .gitignore
(Get-Content .gitignore) -replace '^\*\.sqlite$', '#*.sqlite' | Set-Content .gitignore

# Agregar base de datos
Write-Host "Agregando base de datos..." -ForegroundColor Green
git add cotizaciones.db
git add .gitignore

# Commit
git commit -m "Temporary: Add database for transfer"

# Push
Write-Host "Subiendo a GitHub..." -ForegroundColor Green
git push -u origin database-transfer

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✅ Base de datos subida a GitHub!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nEn el servidor ejecuta:" -ForegroundColor Yellow
Write-Host "cd /opt/cotizador" -ForegroundColor White
Write-Host "git fetch origin" -ForegroundColor White
Write-Host "git checkout database-transfer" -ForegroundColor White
Write-Host "cp cotizaciones.db data/" -ForegroundColor White
Write-Host "git checkout main" -ForegroundColor White
Write-Host "`nLuego continúa con el deploy" -ForegroundColor Yellow
Write-Host "============================================`n" -ForegroundColor Cyan

# Volver a main
Write-Host "Volviendo a rama main..." -ForegroundColor Yellow
git checkout main

Write-Host "`nNOTA: La rama 'database-transfer' quedó en GitHub." -ForegroundColor Yellow
Write-Host "Puedes eliminarla después con:" -ForegroundColor Gray
Write-Host "git push origin --delete database-transfer" -ForegroundColor Gray
