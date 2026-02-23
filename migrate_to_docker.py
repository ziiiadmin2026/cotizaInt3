#!/usr/bin/env python3
"""
Script de migración a Docker
Prepara la instalación existente para usar con Docker
"""
import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Crear estructura de directorios para Docker"""
    print("📁 Creando estructura de directorios...")
    
    directories = [
        'data',
        'logs',
        'pdfs',
        'uploads',
        'uploads/productos',
        'static/images',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print("✅ Estructura de directorios creada\n")

def migrate_database():
    """Migrar base de datos al directorio data/"""
    print("🗃️  Migrando base de datos...")
    
    old_db = 'cotizaciones.db'
    new_db = 'data/cotizaciones.db'
    
    if os.path.exists(old_db) and not os.path.exists(new_db):
        # Crear backup
        backup_db = f'{old_db}.backup'
        shutil.copy2(old_db, backup_db)
        print(f"  ✓ Backup creado: {backup_db}")
        
        # Copiar a nueva ubicación
        shutil.copy2(old_db, new_db)
        print(f"  ✓ Base de datos copiada a: {new_db}")
        print(f"  ℹ️  La base de datos original quedó en: {old_db}")
    elif os.path.exists(new_db):
        print(f"  ℹ️  Base de datos ya existe en: {new_db}")
    else:
        print(f"  ⚠️  No se encontró base de datos para migrar")
    
    print("✅ Migración de base de datos completada\n")

def check_env_file():
    """Verificar y actualizar archivo .env"""
    print("⚙️  Verificando archivo .env...")
    
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("  ✓ Archivo .env creado desde .env.example")
            print("  ⚠️  IMPORTANTE: Edita .env con tus credenciales")
        else:
            print("  ❌ No se encontró .env.example")
            return False
    else:
        # Verificar si tiene DATABASE_PATH correcto
        with open('.env', 'r') as f:
            content = f.read()
        
        if 'DATABASE_PATH=cotizaciones.db' in content:
            content = content.replace(
                'DATABASE_PATH=cotizaciones.db',
                'DATABASE_PATH=data/cotizaciones.db'
            )
            with open('.env', 'w') as f:
                f.write(content)
            print("  ✓ DATABASE_PATH actualizado en .env")
        else:
            print("  ✓ Archivo .env existe y está configurado")
    
    print("✅ Verificación de .env completada\n")
    return True

def create_gitkeep_files():
    """Crear archivos .gitkeep en directorios vacíos"""
    print("📝 Creando archivos .gitkeep...")
    
    directories = ['data', 'logs']
    for directory in directories:
        gitkeep = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep):
            Path(gitkeep).touch()
            print(f"  ✓ {gitkeep}")
    
    print("✅ Archivos .gitkeep creados\n")

def show_summary():
    """Mostrar resumen de la migración"""
    print("=" * 60)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 60)
    print("""
Tu proyecto está listo para Docker! 🐳

PRÓXIMOS PASOS:

1. Editar archivo .env con tus credenciales:
   - SECRET_KEY (generar una nueva)
   - SMTP_EMAIL y SMTP_PASSWORD
   - BASE_URL del servidor de producción

2. Verificar configuración:
   python verify_deployment.py

3. Desplegar:
   Linux/Mac:  ./deploy.sh
   Windows:    .\\deploy.ps1 -Build
   Manual:     docker compose up -d

DOCUMENTACIÓN:
- Guía rápida:    DOCKER_SETUP.md
- Guía completa:  DEPLOYMENT.md
- README:         README.md

ESTRUCTURA DE DATOS:
- Base de datos:  data/cotizaciones.db
- PDFs:           pdfs/
- Uploads:        uploads/
- Logs:           logs/

La base de datos original (cotizaciones.db) quedó como backup.
""")
    print("=" * 60)

def main():
    print("=" * 60)
    print("MIGRACIÓN A DOCKER")
    print("Sistema de Cotización - Integrational3")
    print("=" * 60)
    print()
    
    try:
        create_directory_structure()
        migrate_database()
        
        if check_env_file():
            create_gitkeep_files()
            show_summary()
        else:
            print("\n❌ Error en la configuración del archivo .env")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
