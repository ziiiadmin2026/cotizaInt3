from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime
from uuid import uuid4
from werkzeug.utils import secure_filename
from database import Database
from pdf_generator import PDFGenerator
from email_sender import EmailSender
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-integrational3-2025')
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
CORS(app)

# Inicializar servicios
db = Database()
pdf_gen = PDFGenerator()
email_sender = EmailSender()

# Asegurar directorios
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(Config.UPLOAD_FOLDER, 'productos'), exist_ok=True)

def _allowed_attachment(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_ATTACHMENT_EXTENSIONS

def _allowed_image(filename):
    """Verificar si es una imagen permitida"""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        if session.get('rol') != 'admin':
            return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Rutas de autenticación

@app.route('/')
def index():
    """Página principal - redirige al login si no está autenticado"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')

@app.route('/login')
def login_page():
    """Página de login"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/usuarios')
@login_required
def usuarios_page():
    """Página de gestión de usuarios (solo admin)"""
    if session.get('rol') != 'admin':
        return redirect(url_for('index'))
    return render_template('usuarios.html')

@app.route('/nueva-cotizacion')
@login_required
def nueva_cotizacion_page():
    """Página dedicada para crear nueva cotización"""
    return render_template('nueva_cotizacion.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Autenticar usuario"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Usuario y contraseña requeridos'
        }), 400
    
    usuario = db.autenticar_usuario(username, password)
    
    if usuario:
        # Guardar en sesión
        session['user_id'] = usuario['id']
        session['username'] = usuario['username']
        session['nombre_completo'] = usuario['nombre_completo']
        session['rol'] = usuario['rol']
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'usuario': {
                'id': usuario['id'],
                'username': usuario['username'],
                'nombre_completo': usuario['nombre_completo'],
                'rol': usuario['rol']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Usuario o contraseña incorrectos'
        }), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Sesión cerrada'
    })

@app.route('/api/session', methods=['GET'])
def get_session():
    """Obtener información de la sesión actual"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'usuario': {
                'id': session['user_id'],
                'username': session['username'],
                'nombre_completo': session['nombre_completo'],
                'rol': session['rol']
            }
        })
    else:
        return jsonify({'authenticated': False})

@app.route('/api/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    """Gestión de clientes"""
    if request.method == 'GET':
        # Obtener todos los clientes
        clientes_list = db.obtener_clientes()
        return jsonify(clientes_list)
    
    elif request.method == 'POST':
        # Crear nuevo cliente
        data = request.get_json()
        
        try:
            cliente_id = db.crear_cliente(
                nombre=data['nombre'],
                email=data['email'],
                telefono=data.get('telefono', ''),
                direccion=data.get('direccion', ''),
                rfc=data.get('rfc', '')
            )
            
            return jsonify({
                'success': True,
                'cliente_id': cliente_id,
                'message': 'Cliente creado exitosamente'
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al crear cliente: {str(e)}'
            }), 400

@app.route('/api/clientes/<int:cliente_id>', methods=['GET', 'PUT'])
def obtener_cliente(cliente_id):
    """Obtener o actualizar un cliente específico"""
    if request.method == 'GET':
        cliente = db.obtener_cliente(cliente_id)
        
        if cliente:
            return jsonify(cliente)
        else:
            return jsonify({'error': 'Cliente no encontrado'}), 404
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            resultado = db.actualizar_cliente(
                cliente_id,
                nombre=data.get('nombre'),
                email=data.get('email'),
                telefono=data.get('telefono'),
                direccion=data.get('direccion'),
                rfc=data.get('rfc')
            )
            
            if resultado:
                return jsonify({
                    'success': True,
                    'message': 'Cliente actualizado correctamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No se pudo actualizar el cliente'
                }), 400
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 400

@app.route('/api/cotizaciones', methods=['GET', 'POST'])
@login_required
def cotizaciones():
    """Gestión de cotizaciones"""
    if request.method == 'GET':
        # Obtener todas las cotizaciones
        cotizaciones_list = db.obtener_cotizaciones()
        return jsonify(cotizaciones_list)
    
    elif request.method == 'POST':
        # Crear nueva cotización
        data = request.get_json()
        
        try:
            cotizacion_id, numero_cotizacion = db.crear_cotizacion(
                cliente_id=data['cliente_id'],
                items=data['items'],
                fecha_validez=data.get('fecha_validez'),
                notas=data.get('notas', ''),
                condiciones_comerciales=data.get('condiciones_comerciales', ''),
                iva_porcentaje=data.get('iva_porcentaje', 16),
                creado_por=session.get('user_id')  # Agregar usuario que crea la cotización
            )
            
            return jsonify({
                'success': True,
                'cotizacion_id': cotizacion_id,
                'numero_cotizacion': numero_cotizacion,
                'message': 'Cotización creada exitosamente'
            }), 201
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al crear cotización: {str(e)}'
            }), 400

@app.route('/api/cotizaciones/<int:cotizacion_id>', methods=['GET', 'PUT'])
@login_required
def obtener_cotizacion(cotizacion_id):
    """Obtener o actualizar una cotización específica"""
    if request.method == 'GET':
        cotizacion = db.obtener_cotizacion(cotizacion_id)
        
        if cotizacion:
            return jsonify(cotizacion)
        else:
            return jsonify({'error': 'Cotización no encontrada'}), 404
    
    elif request.method == 'PUT':
        # Actualizar cotización
        data = request.get_json()
        
        try:
            db.actualizar_cotizacion(
                cotizacion_id=cotizacion_id,
                cliente_id=data['cliente_id'],
                items=data['items'],
                fecha_validez=data.get('fecha_validez'),
                notas=data.get('notas', ''),
                condiciones_comerciales=data.get('condiciones_comerciales', ''),
                iva_porcentaje=data.get('iva_porcentaje', 16)
            )
            
            return jsonify({
                'success': True,
                'message': 'Cotización actualizada exitosamente'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al actualizar cotización: {str(e)}'
            }), 400

@app.route('/api/cotizaciones/<int:cotizacion_id>/adjuntos', methods=['POST'])
@login_required
def subir_adjuntos(cotizacion_id):
    """Subir adjuntos para una cotización"""
    cotizacion = db.obtener_cotizacion(cotizacion_id)
    if not cotizacion:
        return jsonify({'success': False, 'message': 'Cotización no encontrada'}), 404

    archivos = request.files.getlist('archivos')
    if not archivos:
        return jsonify({'success': False, 'message': 'No se recibieron archivos'}), 400

    archivos_validos = [a for a in archivos if a and a.filename]
    if not archivos_validos:
        return jsonify({'success': False, 'message': 'No se recibieron archivos válidos'}), 400

    if len(archivos_validos) > Config.MAX_ATTACHMENTS:
        return jsonify({
            'success': False,
            'message': f'Se permiten máximo {Config.MAX_ATTACHMENTS} archivos por cotización'
        }), 400

    cotizacion_dir = os.path.join(Config.UPLOAD_FOLDER, f"cotizacion_{cotizacion_id}")
    os.makedirs(cotizacion_dir, exist_ok=True)

    adjuntos_data = []
    saved_paths = []
    total_bytes = 0

    try:
        for archivo in archivos_validos:
            if not _allowed_attachment(archivo.filename):
                raise ValueError('Tipo de archivo no permitido')

            safe_name = secure_filename(archivo.filename)
            stored_name = f"{uuid4().hex}_{safe_name}"
            file_path = os.path.join(cotizacion_dir, stored_name)

            archivo.save(file_path)
            saved_paths.append(file_path)

            size = os.path.getsize(file_path)
            total_bytes += size

            if size > Config.MAX_ATTACHMENT_MB * 1024 * 1024:
                raise ValueError('Archivo excede el tamaño permitido')

            if total_bytes > Config.MAX_TOTAL_ATTACH_MB * 1024 * 1024:
                raise ValueError('Tamaño total de adjuntos excedido')

            adjuntos_data.append({
                'nombre_original': archivo.filename,
                'nombre_archivo': stored_name,
                'ruta_archivo': file_path,
                'mime_tipo': archivo.mimetype,
                'tamano_bytes': size
            })

        db.agregar_adjuntos(cotizacion_id, adjuntos_data)

        return jsonify({
            'success': True,
            'message': f'Adjuntos guardados: {len(adjuntos_data)}'
        }), 201

    except ValueError as e:
        for path in saved_paths:
            try:
                os.remove(path)
            except OSError:
                pass
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        for path in saved_paths:
            try:
                os.remove(path)
            except OSError:
                pass
        return jsonify({
            'success': False,
            'message': f'Error al subir adjuntos: {str(e)}'
        }), 500

@app.route('/api/cotizaciones/<int:cotizacion_id>/pdf', methods=['GET'])
@login_required
def generar_pdf(cotizacion_id):
    """Generar PDF de una cotización"""
    try:
        cotizacion = db.obtener_cotizacion(cotizacion_id)
        
        if not cotizacion:
            return jsonify({'error': 'Cotización no encontrada'}), 404
        
        # Generar PDF
        pdf_path = pdf_gen.generar_cotizacion_pdf(cotizacion)
        
        # Enviar archivo
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{cotizacion['numero_cotizacion']}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar PDF: {str(e)}'
        }), 500

@app.route('/api/cotizaciones/<int:cotizacion_id>/email', methods=['POST'])
@login_required
def enviar_email(cotizacion_id):
    """Enviar cotización por email"""
    try:
        print(f"\n[API] Solicitud de envío de email para cotización {cotizacion_id}")
        data = request.get_json()
        cotizacion = db.obtener_cotizacion(cotizacion_id)
        
        if not cotizacion:
            return jsonify({'error': 'Cotización no encontrada'}), 404
        
        # Verificar configuración de email
        es_valida, mensaje = email_sender.verificar_configuracion()
        if not es_valida:
            print(f"[API] Configuración inválida: {mensaje}")
            return jsonify({
                'success': False,
                'message': mensaje
            }), 400
        
        print(f"[API] Generando PDF...")
        # Generar PDF
        pdf_path = pdf_gen.generar_cotizacion_pdf(cotizacion)
        print(f"[API] PDF generado: {pdf_path}")

        adjuntos = db.obtener_adjuntos(cotizacion_id)
        
        # Obtener emails de destinatarios (puede ser uno o varios)
        emails = data.get('emails', [])
        if not emails:
            # Fallback al formato antiguo
            email = data.get('email', cotizacion['email'])
            emails = [email] if email else []
        
        # Filtrar y validar emails
        emails = [e.strip() for e in emails if e and e.strip()]
        
        if not emails:
            return jsonify({
                'success': False,
                'message': 'No se especificaron destinatarios válidos'
            }), 400
        
        print(f"[API] Destinatarios ({len(emails)}): {', '.join(emails)}")
        
        # Enviar email a cada destinatario
        exitosos = 0
        fallidos = 0
        
        for destinatario in emails:
            resultado = email_sender.enviar_cotizacion_email(
                destinatario,
                cotizacion,
                pdf_path,
                adjuntos=adjuntos
            )
            if isinstance(resultado, tuple):
                success, _ = resultado
                if success:
                    exitosos += 1
                else:
                    fallidos += 1
            elif resultado:
                exitosos += 1
            else:
                fallidos += 1
                # Guardar emails destino en la cotización
        if exitosos > 0:
            emails_str = ','.join(emails)
            db.actualizar_emails_destino(cotizacion_id, emails_str)
            print(f"[API] Emails destino guardados: {emails_str}")
                # Construir mensaje de resultado
        if exitosos > 0 and fallidos == 0:
            mensaje = f'Cotización enviada exitosamente a {exitosos} destinatario(s)'
            return jsonify({
                'success': True,
                'message': mensaje
            })
        elif exitosos > 0 and fallidos > 0:
            mensaje = f'Enviado a {exitosos} destinatario(s), {fallidos} fallaron'
            return jsonify({
                'success': True,
                'message': mensaje
            })
        else:
            return jsonify({
                'success': False,
                'message': f'No se pudo enviar a ninguno de los {len(emails)} destinatarios'
            }), 500
            
    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/cotizaciones/<int:cotizacion_id>/estado', methods=['PUT'])
@login_required
def actualizar_estado(cotizacion_id):
    """Actualizar estado de una cotización"""
    try:
        data = request.get_json()
        estado = data.get('estado')
        
        if not estado:
            return jsonify({'error': 'Estado no proporcionado'}), 400
        
        db.actualizar_estado_cotizacion(cotizacion_id, estado)
        
        return jsonify({
            'success': True,
            'message': 'Estado actualizado exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

# Rutas de gestión de usuarios

@app.route('/api/usuarios', methods=['GET', 'POST'])
@admin_required
def api_usuarios():
    """Gestión de usuarios (solo admin)"""
    if request.method == 'GET':
        # Obtener todos los usuarios
        usuarios_list = db.obtener_usuarios()
        return jsonify(usuarios_list)
    
    elif request.method == 'POST':
        # Crear nuevo usuario
        data = request.get_json()
        
        try:
            usuario_id = db.crear_usuario(
                username=data['username'],
                password=data['password'],
                nombre_completo=data['nombre_completo'],
                email=data['email'],
                rol=data.get('rol', 'usuario')
            )
            
            if usuario_id:
                return jsonify({
                    'success': True,
                    'usuario_id': usuario_id,
                    'message': 'Usuario creado exitosamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'El usuario ya existe'
                }), 400
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al crear usuario: {str(e)}'
            }), 500

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def api_usuario(usuario_id):
    """Gestión de usuario individual"""
    if request.method == 'GET':
        usuario = db.obtener_usuario(usuario_id)
        if usuario:
            return jsonify(usuario)
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        try:
            db.actualizar_usuario(
                usuario_id,
                nombre_completo=data.get('nombre_completo'),
                email=data.get('email'),
                rol=data.get('rol'),
                activo=data.get('activo')
            )
            
            return jsonify({
                'success': True,
                'message': 'Usuario actualizado exitosamente'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
    
    elif request.method == 'DELETE':
        try:
            # No permitir eliminar al usuario actual
            if usuario_id == session['user_id']:
                return jsonify({
                    'success': False,
                    'message': 'No puedes eliminar tu propio usuario'
                }), 400
            
            db.eliminar_usuario(usuario_id)
            
            return jsonify({
                'success': True,
                'message': 'Usuario eliminado exitosamente'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500

@app.route('/api/usuarios/<int:usuario_id>/password', methods=['PUT'])
@admin_required
def cambiar_password_usuario(usuario_id):
    """Cambiar contraseña de un usuario"""
    data = request.get_json()
    
    try:
        nueva_password = data.get('nueva_password')
        
        if not nueva_password:
            return jsonify({
                'success': False,
                'message': 'Nueva contraseña requerida'
            }), 400
        
        db.cambiar_password(usuario_id, nueva_password)
        
        return jsonify({
            'success': True,
            'message': 'Contraseña actualizada exitosamente'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

# Rutas de gestión de productos

@app.route('/productos')
@login_required
def productos_page():
    """Página de gestión de productos"""
    return render_template('productos.html')

@app.route('/test-upload')
@login_required
def test_upload_page():
    """Página de prueba para subida de imágenes"""
    return render_template('test_upload.html')

@app.route('/api/productos/upload-imagen', methods=['POST'])
@login_required
def upload_imagen_producto():
    """Subir imagen de producto"""
    if 'imagen' not in request.files:
        return jsonify({'success': False, 'message': 'No se recibió archivo'}), 400
    
    archivo = request.files['imagen']
    if not archivo or not archivo.filename:
        return jsonify({'success': False, 'message': 'Archivo inválido'}), 400
    
    if not _allowed_image(archivo.filename):
        return jsonify({'success': False, 'message': 'Tipo de archivo no permitido. Use PNG, JPG, JPEG, GIF o WEBP'}), 400
    
    try:
        # Generar nombre único
        safe_name = secure_filename(archivo.filename)
        ext = safe_name.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid4().hex}.{ext}"
        
        # Guardar en directorio de productos
        productos_dir = os.path.join(Config.UPLOAD_FOLDER, 'productos')
        file_path = os.path.join(productos_dir, unique_name)
        archivo.save(file_path)
        
        # Retornar ruta relativa para guardar en BD
        relative_path = f"/uploads/productos/{unique_name}"
        
        return jsonify({
            'success': True,
            'url': relative_path,
            'filename': unique_name
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al subir imagen: {str(e)}'
        }), 500

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Servir archivos subidos"""
    return send_file(os.path.join(Config.UPLOAD_FOLDER, filename))

@app.route('/api/productos', methods=['GET', 'POST'])
@login_required
def api_productos():
    """Gestión de productos"""
    if request.method == 'GET':
        # Obtener todos los productos
        incluir_inactivos = request.args.get('incluir_inactivos', 'false').lower() == 'true'
        productos = db.obtener_productos(incluir_inactivos)
        return jsonify(productos)
    
    elif request.method == 'POST':
        # Crear nuevo producto
        data = request.get_json()
        
        try:
            producto_id = db.crear_producto(
                codigo=data['codigo'],
                nombre=data['nombre'],
                descripcion=data.get('descripcion', ''),
                tipo=data['tipo'],
                precio=float(data['precio']),
                unidad=data.get('unidad', 'pza'),
                categoria=data.get('categoria', ''),
                imagen_url=data.get('imagen_url')
            )
            
            if producto_id:
                return jsonify({
                    'success': True,
                    'producto_id': producto_id,
                    'message': 'Producto creado exitosamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'El código del producto ya existe'
                }), 400
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al crear producto: {str(e)}'
            }), 500

@app.route('/api/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_producto(producto_id):
    """Gestión de producto individual"""
    if request.method == 'GET':
        producto = db.obtener_producto(producto_id)
        if producto:
            return jsonify(producto)
        return jsonify({'error': 'Producto no encontrado'}), 404
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        try:
            resultado = db.actualizar_producto(
                producto_id,
                codigo=data.get('codigo'),
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion'),
                tipo=data.get('tipo'),
                precio=float(data['precio']) if 'precio' in data else None,
                unidad=data.get('unidad'),
                categoria=data.get('categoria'),
                activo=data.get('activo'),
                imagen_url=data.get('imagen_url')
            )
            
            if resultado:
                return jsonify({
                    'success': True,
                    'message': 'Producto actualizado exitosamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'El código del producto ya existe'
                }), 400
        
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500
    
    elif request.method == 'DELETE':
        try:
            db.eliminar_producto(producto_id)
            
            return jsonify({
                'success': True,
                'message': 'Producto eliminado exitosamente'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error: {str(e)}'
            }), 500

@app.route('/api/productos/buscar/<codigo>', methods=['GET'])
@login_required
def buscar_producto_por_codigo(codigo):
    """Buscar producto por código"""
    producto = db.buscar_producto_por_codigo(codigo)
    if producto:
        return jsonify(producto)
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/api/categorias', methods=['GET'])
@login_required
def api_categorias():
    """Obtener lista de categorías"""
    categorias = db.obtener_categorias()
    return jsonify(categorias)

@app.route('/api/config', methods=['GET'])
def obtener_config():
    """Obtener configuración de la empresa"""
    return jsonify({
        'empresa_nombre': Config.EMPRESA_NOMBRE,
        'empresa_direccion': Config.EMPRESA_DIRECCION,
        'empresa_telefono': Config.EMPRESA_TELEFONO,
        'empresa_email': Config.EMPRESA_EMAIL,
        'empresa_sitio_web': Config.EMPRESA_SITIO_WEB
    })

# Rutas públicas de aprobación de cotizaciones

@app.route('/aprobar/<token>', methods=['GET', 'POST'])
def aprobar_cotizacion(token):
    """Página pública para aprobar cotización"""
    try:
        cotizacion = db.obtener_cotizacion_por_token(token)
        
        if not cotizacion:
            return render_template('aprobacion_resultado.html', 
                                 error='Token inválido o cotización no encontrada'), 404
        
        if cotizacion['estado_aprobacion'] != 'pendiente':
            return render_template('aprobacion_resultado.html',
                                 estado=cotizacion['estado_aprobacion'],
                                 fecha=cotizacion['fecha_aprobacion'],
                                 ya_procesado=True)
        
        if request.method == 'POST':
            comentarios = request.form.get('comentarios', '')
            if db.actualizar_estado_aprobacion(token, 'aprobado', comentarios):
                # Enviar email de confirmación a los destinatarios originales
                emails_destino = cotizacion.get('emails_destino', '')
                destinatarios = [e.strip() for e in emails_destino.split(',') if e.strip()] if emails_destino else []
                
                # Fallback al email del cliente si no hay destinos guardados
                if not destinatarios:
                    cliente_email = cotizacion.get('cliente_email', '')
                    if cliente_email:
                        destinatarios = [cliente_email]
                
                print(f"[DEBUG] Enviando confirmación a: {destinatarios}")
                print(f"[DEBUG] Cotización: {cotizacion.get('numero_cotizacion')}")
                
                # Enviar a cada destinatario
                for email_dest in destinatarios:
                    try:
                        resultado = email_sender.enviar_confirmacion_aprobacion(
                            email_dest,
                            cotizacion,
                            'aprobado',
                            comentarios
                        )
                        print(f"[DEBUG] Resultado envío a {email_dest}: {resultado}")
                    except Exception as e:
                        print(f"[ERROR] Error al enviar confirmación a {email_dest}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                return render_template('aprobacion_resultado.html',
                                     estado='aprobado',
                                     cotizacion=cotizacion,
                                     comentarios=comentarios)
            else:
                return render_template('aprobacion_resultado.html',
                                     error='Error al procesar aprobación'), 500
        
        return render_template('aprobacion_form.html', 
                             cotizacion=cotizacion, 
                             accion='aprobar')
    
    except Exception as e:
        return render_template('aprobacion_resultado.html',
                             error=f'Error: {str(e)}'), 500

@app.route('/rechazar/<token>', methods=['GET', 'POST'])
def rechazar_cotizacion(token):
    """Página pública para rechazar cotización"""
    try:
        cotizacion = db.obtener_cotizacion_por_token(token)
        
        if not cotizacion:
            return render_template('aprobacion_resultado.html',
                                 error='Token inválido o cotización no encontrada'), 404
        
        if cotizacion['estado_aprobacion'] != 'pendiente':
            return render_template('aprobacion_resultado.html',
                                 estado=cotizacion['estado_aprobacion'],
                                 fecha=cotizacion['fecha_aprobacion'],
                                 ya_procesado=True)
        
        if request.method == 'POST':
            comentarios = request.form.get('comentarios', '')
            if db.actualizar_estado_aprobacion(token, 'rechazado', comentarios):
                # Enviar email de confirmación al cliente
                email_sender.enviar_confirmacion_aprobacion(
                    cotizacion.get('cliente_email', ''),
                    cotizacion,
                    'rechazado',
                    comentarios
                )
                return render_template('aprobacion_resultado.html',
                                     estado='rechazado',
                                     cotizacion=cotizacion,
                                     comentarios=comentarios)
            else:
                return render_template('aprobacion_resultado.html',
                                     error='Error al procesar rechazo'), 500
        
        return render_template('aprobacion_form.html',
                             cotizacion=cotizacion,
                             accion='rechazar')
    
    except Exception as e:
        return render_template('aprobacion_resultado.html',
                             error=f'Error: {str(e)}'), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
