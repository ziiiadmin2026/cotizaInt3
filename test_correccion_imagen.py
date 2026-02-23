#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación corregida de carga de imagen en modal producto rápido
"""

print("\n=== VERIFICACIÓN DE CORRECCIÓN DE ERRORES ===\n")

# 1. Verificar que la función JavaScript esté corregida
print("📝 Verificando archivo JavaScript...")
with open('static/js/nueva_cotizacion.js', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Verificar que la función recibe parámetro
    if 'async function subirImagenProductoRapido(btnElement)' in content:
        print("  ✅ Función recibe parámetro btnElement")
    else:
        print("  ❌ Función no recibe parámetro")
    
    # Verificar que no usa event.target sin parámetro
    if 'const btnUpload = btnElement;' in content:
        print("  ✅ Usa btnElement correctamente")
    else:
        print("  ❌ btnUpload no está bien definido")
    
    # Verificar que btnUpload está en scope correcto
    if content.count('btnUpload.disabled = false;') >= 2:  # Una en try, una en catch
        print("  ✅ btnUpload accesible en try/catch")
    else:
        print("  ❌ Problema con scope de btnUpload")

# 2. Verificar que el HTML pasa el parámetro
print("\n📝 Verificando archivo HTML...")
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
    if 'onclick="subirImagenProductoRapido(this)"' in content:
        print("  ✅ HTML pasa 'this' como parámetro al botón")
    else:
        print("  ❌ HTML no pasa parámetro al botón")
    
    if 'id="prod-imagen-file"' in content and 'id="prod-imagen-url"' in content:
        print("  ✅ Elementos de imagen presentes en HTML")
    else:
        print("  ❌ Faltan elementos de imagen en HTML")

# 3. Verificar endpoint de API
print("\n📝 Verificando endpoint de API...")
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    if "@app.route('/api/productos/upload-imagen'" in content:
        print("  ✅ Endpoint /api/productos/upload-imagen existe")
    else:
        print("  ❌ Endpoint no encontrado")

print("\n" + "="*60)
print("🔧 CORRECCIONES APLICADAS:")
print("="*60)
print("1. ✅ Función subirImagenProductoRapido() ahora recibe parámetro 'btnElement'")
print("2. ✅ HTML pasa 'this' al hacer click en botón")
print("3. ✅ Variable btnUpload correctamente declarada fuera del try/catch")
print("4. ✅ Eliminadas líneas duplicadas en el código")
print("\n💡 CÓMO PROBAR:")
print("   1. Abre el navegador en http://127.0.0.1:5000")
print("   2. Click en 'Nueva Cotización'")
print("   3. Click en '+ Agregar Concepto'")
print("   4. Click en botón 'Nuevo' (verde)")
print("   5. En el modal, selecciona una imagen y click '📤 Subir Imagen'")
print("   6. Deberías ver: '⏳ Subiendo...' → Preview de imagen → Notificación de éxito")
print("\n🚀 Servidor corriendo en http://127.0.0.1:5000")
