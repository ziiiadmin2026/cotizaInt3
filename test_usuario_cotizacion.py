#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el campo creado_por se agregó correctamente
"""

import sqlite3
from database import Database

def test_estructura_cotizaciones():
    """Verificar que la tabla cotizaciones tiene la columna creado_por"""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Obtener información de la tabla cotizaciones
    cursor.execute("PRAGMA table_info(cotizaciones)")
    columnas = cursor.fetchall()
    
    print("\n=== ESTRUCTURA DE LA TABLA COTIZACIONES ===")
    for col in columnas:
        print(f"  {col[1]}: {col[2]}")
    
    # Verificar que existe la columna creado_por
    nombres_columnas = [col[1] for col in columnas]
    if 'creado_por' in nombres_columnas:
        print("\n✅ La columna 'creado_por' existe en la tabla cotizaciones")
    else:
        print("\n❌ La columna 'creado_por' NO existe en la tabla cotizaciones")
    
    conn.close()

def test_obtener_usuarios():
    """Verificar que podemos obtener usuarios"""
    db = Database()
    usuarios = db.obtener_usuarios()
    
    print("\n=== USUARIOS EN EL SISTEMA ===")
    if usuarios:
        for usuario in usuarios:
            print(f"  ID: {usuario['id']}, Usuario: {usuario['username']}, Nombre: {usuario['nombre_completo']}")
    else:
        print("  No hay usuarios en el sistema")

if __name__ == '__main__':
    print("Iniciando pruebas...\n")
    test_estructura_cotizaciones()
    test_obtener_usuarios()
    print("\n✅ Pruebas completadas")
