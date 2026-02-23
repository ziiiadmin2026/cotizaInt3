import sqlite3
from datetime import datetime
import pytz
from config import Config
import hashlib
import secrets

class Database:
    """Manejo de la base de datos SQLite"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializar la base de datos con las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                telefono TEXT,
                direccion TEXT,
                rfc TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de cotizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_cotizacion TEXT UNIQUE NOT NULL,
                cliente_id INTEGER NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_validez DATE,
                subtotal REAL NOT NULL,
                iva REAL DEFAULT 0,
                total REAL NOT NULL,
                notas TEXT,
                condiciones_comerciales TEXT,
                estado TEXT DEFAULT 'pendiente',
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')
        
        # Agregar columna condiciones_comerciales si no existe (para bases de datos existentes)
        try:
            cursor.execute('ALTER TABLE cotizaciones ADD COLUMN condiciones_comerciales TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            pass  # La columna ya existe
        
        # Agregar columnas de aprobación si no existen
        columnas_aprobacion = [
            ('token_aprobacion', 'TEXT UNIQUE'),
            ('estado_aprobacion', "TEXT DEFAULT 'pendiente'"),
            ('fecha_aprobacion', 'TIMESTAMP'),
            ('comentarios_cliente', 'TEXT'),
            ('creado_por', 'INTEGER')  # ID del usuario que creó la cotización
        ]
        
        for columna, tipo in columnas_aprobacion:
            try:
                cursor.execute(f'ALTER TABLE cotizaciones ADD COLUMN {columna} {tipo}')
                conn.commit()
            except sqlite3.OperationalError:
                pass  # La columna ya existe
        
        # Tabla de items de cotización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizacion_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cotizacion_id INTEGER NOT NULL,
                producto_id INTEGER,
                concepto TEXT NOT NULL,
                descripcion TEXT,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones (id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos (id) ON DELETE SET NULL
            )
        ''')
        
        # Agregar columna producto_id si no existe
        try:
            cursor.execute('ALTER TABLE cotizacion_items ADD COLUMN producto_id INTEGER')
            conn.commit()
        except sqlite3.OperationalError:
            pass

        # Tabla de adjuntos de cotización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizacion_adjuntos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cotizacion_id INTEGER NOT NULL,
                nombre_original TEXT NOT NULL,
                nombre_archivo TEXT NOT NULL,
                ruta_archivo TEXT NOT NULL,
                mime_tipo TEXT,
                tamano_bytes INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cotizacion_id) REFERENCES cotizaciones (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre_completo TEXT NOT NULL,
                email TEXT NOT NULL,
                rol TEXT DEFAULT 'usuario',
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP
            )
        ''')
        
        # Tabla de productos y servicios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                tipo TEXT NOT NULL DEFAULT 'producto',
                precio REAL NOT NULL,
                unidad TEXT DEFAULT 'pza',
                categoria TEXT,
                imagen_url TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Agregar columna imagen_url si no existe
        try:
            cursor.execute('ALTER TABLE productos ADD COLUMN imagen_url TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
        
        # Crear usuario admin por defecto si no existe
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_password = self._hash_password('admin123')
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', admin_password, 'Administrador', 'admin@integrational3.com.mx', 'admin'))
            conn.commit()
        
        conn.close()
    
    def crear_cliente(self, nombre, email, telefono='', direccion='', rfc=''):
        """Crear un nuevo cliente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clientes (nombre, email, telefono, direccion, rfc)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, email, telefono, direccion, rfc))
        
        conn.commit()
        cliente_id = cursor.lastrowid
        conn.close()
        
        return cliente_id
    
    def actualizar_cliente(self, cliente_id, nombre, email, telefono='', direccion='', rfc=''):
        """Actualizar un cliente existente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE clientes 
            SET nombre = ?, email = ?, telefono = ?, direccion = ?, rfc = ?
            WHERE id = ?
        ''', (nombre, email, telefono, direccion, rfc, cliente_id))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def obtener_clientes(self):
        """Obtener todos los clientes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM clientes ORDER BY nombre')
        clientes = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return clientes
    
    def obtener_cliente(self, cliente_id):
        """Obtener un cliente por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
        cliente = cursor.fetchone()
        
        conn.close()
        return dict(cliente) if cliente else None
    
    def crear_cotizacion(self, cliente_id, items, fecha_validez=None, notas='', condiciones_comerciales='', iva_porcentaje=16, creado_por=None):
        """Crear una nueva cotización con sus items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Generar número de cotización con formato INT-
        tz_mexico = pytz.timezone('America/Mexico_City')
        fecha_actual = datetime.now(tz_mexico)
        cursor.execute('SELECT COUNT(*) as total FROM cotizaciones')
        total = cursor.fetchone()['total']
        numero_cotizacion = f"INT-{fecha_actual.strftime('%Y%m%d')}-{total + 1:04d}"
        
        # Generar token único de aprobación
        token_aprobacion = secrets.token_urlsafe(32)
        
        # Calcular totales
        subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in items)
        iva = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva
        
        # Insertar cotización
        cursor.execute('''
            INSERT INTO cotizaciones 
            (numero_cotizacion, cliente_id, fecha_validez, subtotal, iva, total, notas, condiciones_comerciales, token_aprobacion, estado_aprobacion, creado_por)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (numero_cotizacion, cliente_id, fecha_validez, subtotal, iva, total, notas, condiciones_comerciales, token_aprobacion, 'pendiente', creado_por))
        
        cotizacion_id = cursor.lastrowid
        
        # Insertar items
        for item in items:
            item_subtotal = item['cantidad'] * item['precio_unitario']
            cursor.execute('''
                INSERT INTO cotizacion_items 
                (cotizacion_id, producto_id, concepto, descripcion, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cotizacion_id, item.get('producto_id'), item['concepto'], item.get('descripcion', ''), 
                  item['cantidad'], item['precio_unitario'], item_subtotal))
        
        conn.commit()
        conn.close()
        
        return cotizacion_id, numero_cotizacion
    
    def obtener_cotizaciones(self):
        """Obtener todas las cotizaciones con información del cliente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, cl.nombre as cliente_nombre, cl.email as cliente_email,
                   u.nombre_completo as creado_por_nombre, u.username as creado_por_username
            FROM cotizaciones c
            JOIN clientes cl ON c.cliente_id = cl.id
            LEFT JOIN usuarios u ON c.creado_por = u.id
            ORDER BY c.fecha_creacion DESC
        ''')
        
        cotizaciones = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return cotizaciones
    
    def obtener_cotizacion(self, cotizacion_id):
        """Obtener una cotización completa con items y cliente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener cotización
        cursor.execute('''
            SELECT c.*, cl.*,
                   u.nombre_completo as creado_por_nombre, u.username as creado_por_username
            FROM cotizaciones c
            JOIN clientes cl ON c.cliente_id = cl.id
            LEFT JOIN usuarios u ON c.creado_por = u.id
            WHERE c.id = ?
        ''', (cotizacion_id,))
        
        cotizacion = cursor.fetchone()
        if not cotizacion:
            conn.close()
            return None
        
        cotizacion_dict = dict(cotizacion)
        
        # Obtener items con información del producto (JOIN)
        cursor.execute('''
            SELECT ci.*, p.codigo as producto_codigo, p.imagen_url as producto_imagen
            FROM cotizacion_items ci
            LEFT JOIN productos p ON ci.producto_id = p.id
            WHERE ci.cotizacion_id = ?
            ORDER BY ci.id
        ''', (cotizacion_id,))
        
        items = [dict(row) for row in cursor.fetchall()]
        cotizacion_dict['items'] = items

        # Obtener adjuntos
        cursor.execute('''
            SELECT * FROM cotizacion_adjuntos WHERE cotizacion_id = ?
            ORDER BY fecha_creacion ASC
        ''', (cotizacion_id,))

        adjuntos = [dict(row) for row in cursor.fetchall()]
        cotizacion_dict['adjuntos'] = adjuntos
        
        conn.close()
        return cotizacion_dict

    def agregar_adjuntos(self, cotizacion_id, adjuntos):
        """Agregar adjuntos a una cotización"""
        if not adjuntos:
            return 0

        conn = self.get_connection()
        cursor = conn.cursor()

        for adjunto in adjuntos:
            cursor.execute('''
                INSERT INTO cotizacion_adjuntos
                (cotizacion_id, nombre_original, nombre_archivo, ruta_archivo, mime_tipo, tamano_bytes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                cotizacion_id,
                adjunto['nombre_original'],
                adjunto['nombre_archivo'],
                adjunto['ruta_archivo'],
                adjunto.get('mime_tipo'),
                adjunto.get('tamano_bytes')
            ))

        conn.commit()
        count = cursor.rowcount
        conn.close()

        return count

    def obtener_adjuntos(self, cotizacion_id):
        """Obtener adjuntos de una cotización"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM cotizacion_adjuntos WHERE cotizacion_id = ?
            ORDER BY fecha_creacion ASC
        ''', (cotizacion_id,))

        adjuntos = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return adjuntos
    
    def actualizar_cotizacion(self, cotizacion_id, cliente_id, items, fecha_validez=None, notas='', condiciones_comerciales='', iva_porcentaje=16):
        """Actualizar una cotización existente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calcular totales
        subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in items)
        iva = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva
        
        # Actualizar cotización
        cursor.execute('''
            UPDATE cotizaciones 
            SET cliente_id = ?, fecha_validez = ?, subtotal = ?, iva = ?, total = ?, notas = ?, condiciones_comerciales = ?
            WHERE id = ?
        ''', (cliente_id, fecha_validez, subtotal, iva, total, notas, condiciones_comerciales, cotizacion_id))
        
        # Eliminar items anteriores
        cursor.execute('DELETE FROM cotizacion_items WHERE cotizacion_id = ?', (cotizacion_id,))
        
        # Insertar nuevos items
        for item in items:
            item_subtotal = item['cantidad'] * item['precio_unitario']
            cursor.execute('''
                INSERT INTO cotizacion_items 
                (cotizacion_id, producto_id, concepto, descripcion, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cotizacion_id, item.get('producto_id'), item['concepto'], item.get('descripcion', ''), 
                  item['cantidad'], item['precio_unitario'], item_subtotal))
        
        conn.commit()
        conn.close()
        
        return True
    
    # ==========================================
    # FUNCIONES DE AUTENTICACIÓN Y USUARIOS
    # ==========================================
    
    def _hash_password(self, password):
        """Generar hash de contraseña con salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    def _verify_password(self, password, password_hash):
        """Verificar contraseña contra hash almacenado"""
        try:
            salt, stored_hash = password_hash.split('$')
            pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return pwd_hash == stored_hash
        except:
            return False
    
    def autenticar_usuario(self, username, password):
        """Autenticar un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM usuarios WHERE username = ? AND activo = 1
        ''', (username,))
        
        usuario = cursor.fetchone()
        
        if usuario and self._verify_password(password, usuario['password_hash']):
            # Actualizar último acceso
            cursor.execute('''
                UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = ?
            ''', (usuario['id'],))
            conn.commit()
            conn.close()
            
            # Retornar datos del usuario (sin el hash)
            user_dict = dict(usuario)
            user_dict.pop('password_hash')
            return user_dict
        
        conn.close()
        return None
    
    def crear_usuario(self, username, password, nombre_completo, email, rol='usuario'):
        """Crear un nuevo usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return None
        
        password_hash = self._hash_password(password)
        
        cursor.execute('''
            INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, nombre_completo, email, rol))
        
        conn.commit()
        usuario_id = cursor.lastrowid
        conn.close()
        
        return usuario_id
    
    def obtener_usuarios(self):
        """Obtener todos los usuarios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nombre_completo, email, rol, activo, fecha_creacion, ultimo_acceso
            FROM usuarios ORDER BY nombre_completo
        ''')
        usuarios = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return usuarios
    
    def obtener_usuario(self, usuario_id):
        """Obtener un usuario por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, nombre_completo, email, rol, activo, fecha_creacion, ultimo_acceso
            FROM usuarios WHERE id = ?
        ''', (usuario_id,))
        
        usuario = cursor.fetchone()
        conn.close()
        
        return dict(usuario) if usuario else None
    
    def actualizar_usuario(self, usuario_id, nombre_completo=None, email=None, rol=None, activo=None):
        """Actualizar datos de un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if nombre_completo is not None:
            updates.append('nombre_completo = ?')
            params.append(nombre_completo)
        
        if email is not None:
            updates.append('email = ?')
            params.append(email)
        
        if rol is not None:
            updates.append('rol = ?')
            params.append(rol)
        
        if activo is not None:
            updates.append('activo = ?')
            params.append(activo)
        
        if not updates:
            conn.close()
            return False
        
        params.append(usuario_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return True
    
    def cambiar_password(self, usuario_id, nueva_password):
        """Cambiar la contraseña de un usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self._hash_password(nueva_password)
        
        cursor.execute('''
            UPDATE usuarios SET password_hash = ? WHERE id = ?
        ''', (password_hash, usuario_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def eliminar_usuario(self, usuario_id):
        """Eliminar un usuario (realmente lo desactiva)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE usuarios SET activo = 0 WHERE id = ?
        ''', (usuario_id,))
        
        conn.commit()
        conn.close()
        
        return True
        
        # Obtener items
        cursor.execute('''
            SELECT * FROM cotizacion_items
            WHERE cotizacion_id = ?
            ORDER BY id
        ''', (cotizacion_id,))
        
        items = [dict(row) for row in cursor.fetchall()]
        cotizacion_dict['items'] = items
        
        conn.close()
        return cotizacion_dict
    
    def actualizar_estado_cotizacion(self, cotizacion_id, estado):
        """Actualizar el estado de una cotización"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cotizaciones
            SET estado = ?
            WHERE id = ?
        ''', (estado, cotizacion_id))
        
        conn.commit()
        conn.close()
    
    # ==========================================
    # FUNCIONES DE PRODUCTOS Y SERVICIOS
    # ==========================================
    
    def crear_producto(self, codigo, nombre, descripcion, tipo, precio, unidad='pza', categoria='', imagen_url=None):
        """Crear un nuevo producto o servicio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar si el código ya existe
        cursor.execute('SELECT id FROM productos WHERE codigo = ?', (codigo,))
        if cursor.fetchone():
            conn.close()
            return None
        
        cursor.execute('''
            INSERT INTO productos (codigo, nombre, descripcion, tipo, precio, unidad, categoria, imagen_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (codigo, nombre, descripcion, tipo, precio, unidad, categoria, imagen_url))
        
        conn.commit()
        producto_id = cursor.lastrowid
        conn.close()
        
        return producto_id
    
    def obtener_productos(self, incluir_inactivos=False):
        """Obtener todos los productos y servicios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if incluir_inactivos:
            cursor.execute('SELECT * FROM productos ORDER BY nombre')
        else:
            cursor.execute('SELECT * FROM productos WHERE activo = 1 ORDER BY nombre')
        
        productos = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return productos
    
    def obtener_producto(self, producto_id):
        """Obtener un producto por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM productos WHERE id = ?', (producto_id,))
        
        producto = cursor.fetchone()
        conn.close()
        
        return dict(producto) if producto else None
    
    def buscar_producto_por_codigo(self, codigo):
        """Buscar un producto por código"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM productos WHERE codigo = ? AND activo = 1', (codigo,))
        
        producto = cursor.fetchone()
        conn.close()
        
        return dict(producto) if producto else None
    
    def actualizar_producto(self, producto_id, codigo=None, nombre=None, descripcion=None, 
                           tipo=None, precio=None, unidad=None, categoria=None, activo=None, imagen_url=None):
        """Actualizar un producto"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if codigo is not None:
            # Verificar que el código no esté en uso por otro producto
            cursor.execute('SELECT id FROM productos WHERE codigo = ? AND id != ?', (codigo, producto_id))
            if cursor.fetchone():
                conn.close()
                return False
            updates.append('codigo = ?')
            params.append(codigo)
        
        if nombre is not None:
            updates.append('nombre = ?')
            params.append(nombre)
        
        if descripcion is not None:
            updates.append('descripcion = ?')
            params.append(descripcion)
        
        if tipo is not None:
            updates.append('tipo = ?')
            params.append(tipo)
        
        if precio is not None:
            updates.append('precio = ?')
            params.append(precio)
        
        if unidad is not None:
            updates.append('unidad = ?')
            params.append(unidad)
        
        if categoria is not None:
            updates.append('categoria = ?')
            params.append(categoria)
        
        if activo is not None:
            updates.append('activo = ?')
            params.append(activo)
        
        if imagen_url is not None:
            updates.append('imagen_url = ?')
            params.append(imagen_url)
        
        if not updates:
            conn.close()
            return False
        
        params.append(producto_id)
        query = f"UPDATE productos SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return True
    
    def eliminar_producto(self, producto_id):
        """Eliminar un producto (realmente lo desactiva)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE productos SET activo = 0 WHERE id = ?
        ''', (producto_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def obtener_cotizacion_por_token(self, token):
        """Obtener cotización por su token de aprobación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, cl.nombre as cliente_nombre, cl.email as cliente_email,
                   u.nombre_completo as creado_por_nombre, u.username as creado_por_username
            FROM cotizaciones c
            JOIN clientes cl ON c.cliente_id = cl.id
            LEFT JOIN usuarios u ON c.creado_por = u.id
            WHERE c.token_aprobacion = ?
        ''', (token,))
        
        cotizacion = cursor.fetchone()
        
        if cotizacion:
            cotizacion = dict(cotizacion)
            
            # Obtener items
            cursor.execute('''
                SELECT * FROM cotizacion_items WHERE cotizacion_id = ?
            ''', (cotizacion['id'],))
            cotizacion['items'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return cotizacion
    
    def actualizar_estado_aprobacion(self, token, estado, comentarios=None):
        """Actualizar el estado de aprobación de una cotización"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if comentarios:
            cursor.execute('''
                UPDATE cotizaciones 
                SET estado_aprobacion = ?, fecha_aprobacion = CURRENT_TIMESTAMP, comentarios_cliente = ?
                WHERE token_aprobacion = ?
            ''', (estado, comentarios, token))
        else:
            cursor.execute('''
                UPDATE cotizaciones 
                SET estado_aprobacion = ?, fecha_aprobacion = CURRENT_TIMESTAMP
                WHERE token_aprobacion = ?
            ''', (estado, token))
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def actualizar_emails_destino(self, cotizacion_id, emails):
        """Actualizar los emails destino de una cotización"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE cotizaciones 
            SET emails_destino = ?
            WHERE id = ?
        ''', (emails, cotizacion_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def obtener_categorias(self):
        """Obtener lista única de categorías de productos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT categoria 
            FROM productos 
            WHERE categoria IS NOT NULL AND categoria != '' AND activo = 1
            ORDER BY categoria
        ''')
        
        categorias = [row['categoria'] for row in cursor.fetchall()]
        
        conn.close()
        return categorias
