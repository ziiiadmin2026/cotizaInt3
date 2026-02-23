#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de depuración para verificar datos de usuario en cotizaciones
"""

from database import Database

db = Database()

# Obtener última cotización
cotizaciones = db.obtener_cotizaciones()

if cotizaciones:
    ultima = cotizaciones[0]
    print("\n=== ÚLTIMA COTIZACIÓN ===")
    print(f"ID: {ultima['id']}")
    print(f"Número: {ultima['numero_cotizacion']}")
    print(f"creado_por (user_id): {ultima.get('creado_por', 'NULL')}")
    print(f"creado_por_nombre: {ultima.get('creado_por_nombre', 'NULL')}")
    print(f"creado_por_username: {ultima.get('creado_por_username', 'NULL')}")
    print(f"\nCliente: {ultima['cliente_nombre']}")
    print(f"Total: ${ultima['total']:.2f}")
    
    print("\n=== PROBANDO obtener_cotizacion() ===")
    cot_completa = db.obtener_cotizacion(ultima['id'])
    if cot_completa:
        print(f"creado_por (user_id): {cot_completa.get('creado_por', 'NULL')}")
        print(f"creado_por_nombre: {cot_completa.get('creado_por_nombre', 'NULL')}")
        print(f"creado_por_username: {cot_completa.get('creado_por_username', 'NULL')}")
else:
    print("No hay cotizaciones en el sistema")

# Ver estructura de la tabla
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(cotizaciones)")
cols = cursor.fetchall()

print("\n=== COLUMNAS DE LA TABLA cotizaciones ===")
for col in cols:
    if 'creado' in col[1].lower():
        print(f"  {col[1]}: {col[2]} (NOT NULL: {col[3]})")

# Ver valor real de creado_por en la última cotización
if cotizaciones:
    cursor.execute("SELECT id, numero_cotizacion, creado_por FROM cotizaciones ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    print(f"\n=== VALOR DIRECTO EN BD ===")
    print(f"ID: {row[0]}, Número: {row[1]}, creado_por: {row[2]}")

conn.close()
