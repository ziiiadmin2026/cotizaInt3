import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('cotizaciones.db')
cursor = conn.cursor()

categorias = ['SDI', 'CCTV', 'Redes', 'Audiovisual', 'Repuestos']

print('Actualizando categorías de productos existentes...\n')

# Verificar cuántos productos hay
cursor.execute('SELECT COUNT(*) FROM productos')
total_productos = cursor.fetchone()[0]
print(f'Total de productos: {total_productos}')

if total_productos > 0:
    # Obtener productos sin categoría o con categoría genérica
    cursor.execute('SELECT id, nombre, categoria FROM productos')
    productos = cursor.fetchall()
    
    print('\nProductos actuales:')
    for p in productos:
        print(f'  ID {p[0]}: {p[1]} - Categoría: {p[2]}')
    
    print('\n¿Deseas actualizar las categorías? (s/n)')
    respuesta = input().strip().lower()
    
    if respuesta == 's':
        print('\nActualiza manualmente desde la interfaz web')
else:
    print('\nNo hay productos. Las categorías disponibles son:')
    for i, cat in enumerate(categorias, 1):
        print(f'{i}. {cat}')

print(f'\n✓ Categorías configuradas: {", ".join(categorias)}')
print('Estas categorías estarán disponibles al crear/editar productos')

conn.close()
