#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para actualizar cotizaciones antiguas y asignar un usuario por defecto
"""

from database import Database

def actualizar_cotizaciones_sin_usuario():
    """Asignar cotizaciones sin usuario al administrador (ID=1)"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Verificar cuántas cotizaciones tienen creado_por NULL
    cursor.execute("SELECT COUNT(*) FROM cotizaciones WHERE creado_por IS NULL")
    total_sin_usuario = cursor.fetchone()[0]
    
    print(f"\n=== COTIZACIONES SIN USUARIO ===")
    print(f"Total: {total_sin_usuario}")
    
    if total_sin_usuario > 0:
        # Obtener el primer usuario (normalmente admin)
        cursor.execute("SELECT id, username, nombre_completo FROM usuarios ORDER BY id LIMIT 1")
        usuario = cursor.fetchone()
        
        if usuario:
            usuario_id, username, nombre = usuario
            print(f"\nAsignando cotizaciones al usuario: {nombre} ({username})")
            
            respuesta = input(f"\n¿Deseas asignar las {total_sin_usuario} cotizaciones antiguas a '{nombre}'? (s/n): ")
            
            if respuesta.lower() == 's':
                cursor.execute("""
                    UPDATE cotizaciones 
                    SET creado_por = ? 
                    WHERE creado_por IS NULL
                """, (usuario_id,))
                
                conn.commit()
                print(f"✅ Se actualizaron {total_sin_usuario} cotizaciones")
            else:
                print("❌ Operación cancelada")
        else:
            print("❌ No hay usuarios en el sistema")
    else:
        print("✅ Todas las cotizaciones tienen un usuario asignado")
    
    conn.close()

if __name__ == '__main__':
    actualizar_cotizaciones_sin_usuario()
