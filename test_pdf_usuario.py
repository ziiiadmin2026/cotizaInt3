#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de generación de PDF con información de usuario
"""

from database import Database
from pdf_generator import PDFGenerator
import os

db = Database()
pdf_gen = PDFGenerator()

# Obtener última cotización
cotizaciones = db.obtener_cotizaciones()

if cotizaciones:
    ultima = cotizaciones[0]
    print(f"\n=== GENERANDO PDF DE PRUEBA ===")
    print(f"Cotización: {ultima['numero_cotizacion']}")
    print(f"Creado por: {ultima.get('creado_por_nombre', 'N/A')}")
    
    # Obtener cotización completa
    cot_completa = db.obtener_cotizacion(ultima['id'])
    
    if cot_completa:
        print(f"\nDatos enviados al generador PDF:")
        print(f"  - creado_por_nombre: {cot_completa.get('creado_por_nombre', 'NULL')}")
        print(f"  - creado_por_username: {cot_completa.get('creado_por_username', 'NULL')}")
        
        # Generar PDF de prueba
        try:
            pdf_path = pdf_gen.generar_cotizacion_pdf(cot_completa, filename=f"TEST_{ultima['numero_cotizacion']}.pdf")
            print(f"\n✅ PDF generado exitosamente:")
            print(f"   {pdf_path}")
            print(f"\n📄 Revisa el pie de página del PDF para verificar:")
            print(f"   - Generado por: {cot_completa.get('creado_por_nombre', 'Usuario no registrado')}")
        except Exception as e:
            print(f"\n❌ Error al generar PDF: {e}")
else:
    print("No hay cotizaciones para probar")
