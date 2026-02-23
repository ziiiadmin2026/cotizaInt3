#!/usr/bin/env python3
"""
Script de verificación pre-despliegue
Verifica que todo esté configurado correctamente antes de desplegar
"""
import os
import sys

def check_env_file():
    """Verificar archivo .env"""
    if not os.path.exists('.env'):
        print("❌ Archivo .env no encontrado")
        print("   Ejecuta: cp .env.example .env")
        return False
    
    # Leer y verificar variables críticas
    with open('.env', 'r') as f:
        content = f.read()
        
    required_vars = [
        'SECRET_KEY',
        'SMTP_EMAIL',
        'SMTP_PASSWORD',
        'BASE_URL'
    ]
    
    missing = []
    for var in required_vars:
        if var not in content or f'{var}=' not in content:
            missing.append(var)
        elif 'tu_contraseña' in content or 'cambiar-por' in content or 'tu-clave' in content:
            if var in content.split('=')[0]:
                missing.append(var)
    
    if missing:
        print(f"❌ Variables de entorno no configuradas: {', '.join(missing)}")
        print("   Edita el archivo .env con tus credenciales reales")
        return False
    
    print("✅ Archivo .env configurado")
    return True

def check_docker():
    """Verificar que Docker esté instalado"""
    if os.system('docker --version > /dev/null 2>&1') != 0:
        print("❌ Docker no está instalado")
        return False
    
    if os.system('docker compose version > /dev/null 2>&1') != 0:
        print("❌ Docker Compose no está instalado")
        return False
    
    print("✅ Docker y Docker Compose instalados")
    return True

def check_directories():
    """Verificar y crear directorios necesarios"""
    dirs = ['data', 'logs', 'pdfs', 'uploads/productos', 'static/images']
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    print("✅ Directorios creados")
    return True

def check_files():
    """Verificar archivos necesarios"""
    required_files = [
        'app.py',
        'database.py',
        'config.py',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'gunicorn_config.py'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Archivos faltantes: {', '.join(missing)}")
        return False
    
    print("✅ Todos los archivos necesarios presentes")
    return True

def main():
    print("=" * 60)
    print("Verificación Pre-Despliegue")
    print("Sistema de Cotización - Integrational3")
    print("=" * 60)
    print()
    
    checks = [
        ("Archivos del proyecto", check_files),
        ("Docker instalado", check_docker),
        ("Archivo .env", check_env_file),
        ("Directorios", check_directories),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\nVerificando {name}...")
        if not check_func():
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✅ Todas las verificaciones pasaron")
        print()
        print("Listo para desplegar! Ejecuta:")
        print("  ./deploy.sh           (Linux/Mac)")
        print("  .\\deploy.ps1 -Build   (Windows)")
        print("  docker compose up -d  (Manual)")
    else:
        print("❌ Hay problemas que deben resolverse antes de desplegar")
        sys.exit(1)
    print("=" * 60)

if __name__ == '__main__':
    main()
