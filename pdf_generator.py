import os
import re
import urllib.request
from io import BytesIO
from datetime import datetime
import pytz
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Flowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from xml.sax.saxutils import escape
from config import Config


class FixedSizeImage(Flowable):
    """Flowable de imagen con tamaño fijo para uso seguro dentro de tablas."""

    def __init__(self, image_source, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.image_reader = ImageReader(image_source)
        self.drawWidth = width
        self.drawHeight = height

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.drawImage(
            self.image_reader,
            0,
            0,
            width=self.width,
            height=self.height,
            preserveAspectRatio=True,
            mask='auto'
        )

class PDFGenerator:
    """Generador de PDFs para cotizaciones"""
    
    def __init__(self):
        self.config = Config()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Crear directorio de PDFs si no existe
        if not os.path.exists(Config.PDF_FOLDER):
            os.makedirs(Config.PDF_FOLDER)
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='ProductCell',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            wordWrap='CJK',
        ))

    def _split_long_token(self, text, chunk_size=24):
        """Inserta espacios en tokens muy largos para permitir saltos de línea."""
        if len(text) <= chunk_size:
            return text
        return ' '.join(text[i:i + chunk_size] for i in range(0, len(text), chunk_size))

    def _format_product_text(self, product_name, description, max_description_chars=220):
        """Genera texto seguro y acotado para la celda de producto."""
        safe_name = escape((product_name or 'N/A').strip())

        raw_description = re.sub(r'\s+', ' ', (description or '').strip())
        if len(raw_description) > max_description_chars:
            raw_description = raw_description[:max_description_chars - 3].rstrip() + '...'

        safe_description = escape(raw_description)
        safe_description = ' '.join(self._split_long_token(token) for token in safe_description.split(' '))

        if safe_description:
            return f"<b>{safe_name}</b><br/><font size=7>{safe_description}</font>"
        return f"<b>{safe_name}</b>"
    
    def _load_and_resize_image(self, image_source, max_width=0.6*inch, max_height=0.6*inch):
        """
        Carga y redimensiona una imagen manteniendo el aspect ratio
        
        Args:
            image_source: Ruta local, URL o BytesIO
            max_width: Ancho máximo en puntos
            max_height: Alto máximo en puntos
            
        Returns:
            Objeto Image de ReportLab o None si falla
        """
        try:
            # Cargar imagen con PIL
            if isinstance(image_source, str):
                if image_source.startswith('http://') or image_source.startswith('https://'):
                    # URL web
                    img_data = BytesIO(urllib.request.urlopen(image_source).read())
                    pil_img = PILImage.open(img_data)
                else:
                    # Ruta local
                    pil_img = PILImage.open(image_source)
            elif isinstance(image_source, BytesIO):
                pil_img = PILImage.open(image_source)
            else:
                return None
            
            # Convertir a RGB si es necesario (para PNG con transparencia)
            if pil_img.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                if pil_img.mode == 'P':
                    pil_img = pil_img.convert('RGBA')
                background.paste(pil_img, mask=pil_img.split()[-1] if pil_img.mode in ('RGBA', 'LA') else None)
                pil_img = background
            
            # Obtener dimensiones originales en píxeles
            orig_width_px, orig_height_px = pil_img.size
            aspect_ratio = orig_width_px / orig_height_px
            
            # Calcular dimensiones finales en puntos (para ReportLab)
            if aspect_ratio > 1:
                # Imagen horizontal: limitar por ancho
                final_width_pt = max_width
                final_height_pt = max_width / aspect_ratio
                if final_height_pt > max_height:
                    final_height_pt = max_height
                    final_width_pt = max_height * aspect_ratio
            else:
                # Imagen vertical: limitar por alto
                final_height_pt = max_height
                final_width_pt = max_height * aspect_ratio
                if final_width_pt > max_width:
                    final_width_pt = max_width
                    final_height_pt = max_width / aspect_ratio
            
            # Redimensionar imagen PIL a tamaño razonable en píxeles
            # Usar 2x el tamaño final para buena calidad (aproximadamente 144 DPI)
            target_width_px = int(final_width_pt * 2)
            target_height_px = int(final_height_pt * 2)
            
            # Solo redimensionar si la imagen es más grande que el objetivo
            if orig_width_px > target_width_px or orig_height_px > target_height_px:
                pil_img = pil_img.resize((target_width_px, target_height_px), PILImage.Resampling.LANCZOS)
            
            # Guardar en BytesIO
            img_buffer = BytesIO()
            pil_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Usar un flowable de tamaño fijo evita que ReportLab reinterprete
            # las dimensiones originales al partir la tabla entre páginas.
            return FixedSizeImage(img_buffer, final_width_pt, final_height_pt)
            
        except Exception as e:
            print(f"Error al cargar y redimensionar imagen: {e}")
            return None
    
    def generar_cotizacion_pdf(self, cotizacion_data, filename=None):
        """
        Generar PDF de cotización con formato Integrational3
        
        Args:
            cotizacion_data: Diccionario con los datos de la cotización
            filename: Nombre del archivo (opcional)
        
        Returns:
            Ruta del archivo PDF generado
        """
        if not filename:
            filename = f"{cotizacion_data['numero_cotizacion']}.pdf"
        
        filepath = os.path.join(Config.PDF_FOLDER, filename)
        
        # Crear documento con márgenes personalizados (aumentar bottomMargin para el footer)
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=30,
            bottomMargin=60  # Aumentado para el footer con información del usuario
        )
        
        # Contenedor para los elementos del PDF
        story = []
        width, height = letter
        
        # ============================================
        # HEADER AZUL CON LOGO DE LA EMPRESA
        # ============================================
        
        # Cargar el logo local
        logo_path = os.path.join('static', 'images', 'logo_integrational3.png')
        
        # Crear tabla con logo y fondo azul
        if os.path.exists(logo_path):
            try:
                # Cargar logo con tamaño apropiado
                logo_img = Image(logo_path, width=3.5*inch, height=0.7*inch)
                logo_img.hAlign = 'LEFT'
                
                header_data = [[logo_img]]
                
            except Exception as e:
                print(f"Error al cargar logo: {e}")
                # Fallback: usar texto
                header_data = [[
                    Paragraph(f'<font size=22><b>{Config.EMPRESA_NOMBRE.upper()}</b></font>', 
                             ParagraphStyle('header', alignment=TA_LEFT, textColor=colors.white))
                ]]
        else:
            # Si no existe el logo, usar texto
            header_data = [[
                Paragraph(f'<font size=22><b>{Config.EMPRESA_NOMBRE.upper()}</b></font>', 
                         ParagraphStyle('header', alignment=TA_LEFT, textColor=colors.white))
            ]]
        
        header_table = Table(header_data, colWidths=[width - 80])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0066CC')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(header_table)
        
        # Información de contacto en el header
        contacto_style = ParagraphStyle('contacto', fontSize=9, textColor=colors.white, alignment=TA_LEFT)
        contacto_data = [[
            Paragraph(f'{Config.EMPRESA_EMAIL}<br/>Tel: {Config.EMPRESA_TELEFONO}', contacto_style)
        ]]
        
        contacto_table = Table(contacto_data, colWidths=[width - 80])
        contacto_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0066CC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(contacto_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ============================================
        # SECCIÓN DE DATOS DEL CLIENTE Y COTIZACIÓN
        # ============================================
        
        # Estilo para títulos de sección
        titulo_seccion = ParagraphStyle(
            'TituloSeccion',
            fontSize=12,
            textColor=colors.HexColor('#0066CC'),
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        
        # Crear dos columnas: Datos del cliente y Cotización
        cliente_content = [
            [Paragraph('<b>DATOS DEL CLIENTE</b>', titulo_seccion)],
            [Paragraph(f'<b>{cotizacion_data["nombre"]}</b>', self.styles['Normal'])],
            [Paragraph(cotizacion_data.get('direccion', ''), self.styles['Normal'])],
            [Paragraph(f'Email: {cotizacion_data["email"]}', self.styles['Normal'])],
            [Paragraph(f'Teléfono: {cotizacion_data.get("telefono", "N/A")}', self.styles['Normal'])],
        ]
        
        cliente_table = Table(cliente_content, colWidths=[3.5*inch])
        cliente_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        
        # Formatear el número de cotización
        num_cotizacion = cotizacion_data['numero_cotizacion'].replace('COT-', 'INT-')
        tz_mexico = pytz.timezone('America/Mexico_City')
        fecha_cot = datetime.now(tz_mexico).strftime('%d/%m/%Y')
        
        cotizacion_content = [
            [Paragraph('<b>COTIZACIÓN</b>', titulo_seccion)],
            [Paragraph(f'<font size=16><b>{num_cotizacion}</b></font>', self.styles['Normal'])],
            [Paragraph(f'Fecha: {fecha_cot}', self.styles['Normal'])],
        ]
        
        cotizacion_table = Table(cotizacion_content, colWidths=[2.5*inch])
        cotizacion_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0F0F0')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        
        # Combinar ambas tablas en una fila
        seccion_superior = Table([[cliente_table, cotizacion_table]], colWidths=[3.5*inch, 2.5*inch])
        seccion_superior.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(seccion_superior)
        story.append(Spacer(1, 0.4*inch))
        
        # ============================================
        # TABLA DE PRODUCTOS
        # ============================================
        
        # Encabezados de la tabla
        table_data = [['Imagen', 'Código', 'Producto', 'Cant.', 'Precio Unit.', 'Total']]
        
        # Items con código, imagen y descripción
        for item in cotizacion_data['items']:
            # Obtener código del producto
            codigo = item.get('producto_codigo', '')
            if not codigo:
                # Fallback: extraer del concepto si tiene formato "CODIGO - Nombre"
                concepto = item.get('concepto', 'N/A')
                if ' - ' in concepto:
                    partes = concepto.split(' - ', 1)
                    codigo = partes[0].strip()
            
            # Nombre del producto
            concepto = item.get('concepto', 'N/A')
            producto_nombre = concepto
            if ' - ' in concepto:
                producto_nombre = concepto.split(' - ', 1)[1].strip()
            
            # Descripción del producto
            descripcion = item.get('descripcion', '')
            
            producto_text = self._format_product_text(producto_nombre, descripcion)
            
            # Imagen del producto (thumbnail)
            imagen_cell = ''
            imagen_url = item.get('producto_imagen')
            if imagen_url:
                try:
                    img = None
                    # Si es URL web
                    if imagen_url.startswith('http://') or imagen_url.startswith('https://'):
                        img = self._load_and_resize_image(imagen_url)
                    # Si es ruta relativa /uploads/...
                    elif imagen_url.startswith('/uploads/'):
                        ruta_local = imagen_url.lstrip('/').replace('/', os.sep)
                        if os.path.exists(ruta_local):
                            img = self._load_and_resize_image(ruta_local)
                    # Si es ruta local directa
                    elif os.path.exists(imagen_url):
                        img = self._load_and_resize_image(imagen_url)
                    
                    # Usar la imagen si se cargó correctamente, sino usar texto
                    if img:
                        imagen_cell = img
                    else:
                        imagen_cell = Paragraph('<font size=6>Sin img</font>', self.styles['Normal'])
                except Exception as e:
                    print(f"Error al cargar imagen: {e}")
                    imagen_cell = Paragraph('<font size=6>N/A</font>', self.styles['Normal'])
            else:
                imagen_cell = Paragraph('<font size=6>-</font>', self.styles['Normal'])
            
            table_data.append([
                imagen_cell,
                Paragraph(f'<font size=9><b>{codigo}</b></font>', self.styles['Normal']),
                Paragraph(producto_text, self.styles['ProductCell']),
                str(item['cantidad']),
                f"${item['precio_unitario']:,.2f}",
                f"${item['subtotal']:,.2f}"
            ])
        
        # Crear tabla de productos
        items_table = Table(table_data, colWidths=[0.7*inch, 0.7*inch, 2.3*inch, 0.6*inch, 1.2*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            
            # Body
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # ============================================
        # TOTALES
        # ============================================
        
        # Tabla de totales alineada a la derecha
        totales_data = [
            ['Subtotal:', f"${cotizacion_data['subtotal']:,.2f}"],
            ['IVA (16%):', f"${cotizacion_data['iva']:,.2f}"],
        ]
        
        totales_table = Table(totales_data, colWidths=[1.5*inch, 1.5*inch])
        totales_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        # Total en caja azul
        total_data = [[
            Paragraph('<b>TOTAL:</b>', ParagraphStyle('total', alignment=TA_RIGHT, textColor=colors.white)),
            Paragraph(f'<b>${cotizacion_data["total"]:,.2f}</b>', 
                     ParagraphStyle('total_num', alignment=TA_RIGHT, textColor=colors.white))
        ]]
        
        total_table = Table(total_data, colWidths=[1.5*inch, 1.5*inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0066CC')),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        # Combinar subtotales y total
        seccion_totales = Table(
            [[totales_table], [total_table]], 
            colWidths=[3*inch]
        )
        seccion_totales.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ]))
        
        # Alinear a la derecha
        totales_container = Table([[seccion_totales]], colWidths=[width - 80])
        totales_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ]))
        
        story.append(totales_container)
        
        # Notas si existen
        if cotizacion_data.get('notas'):
            story.append(Spacer(1, 0.3*inch))
            notas_style = ParagraphStyle('notas', fontSize=9, textColor=colors.HexColor('#666666'))
            story.append(Paragraph(f"<b>Notas:</b> {cotizacion_data['notas']}", notas_style))
        
        # ============================================
        # PÁGINA FINAL: DATOS BANCARIOS Y CONDICIONES
        # ============================================
        story.append(PageBreak())
        
        # Header azul: DATOS BANCARIOS
        header_bancario = Table(
            [[Paragraph('<b>DATOS BANCARIOS</b>', 
                       ParagraphStyle('header_banco', fontSize=20, textColor=colors.white, alignment=TA_LEFT))]], 
            colWidths=[width - 80]
        )
        header_bancario.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0066CC')),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(header_bancario)
        story.append(Spacer(1, 0.5*inch))
        
        # Información bancaria
        info_bancaria_style = ParagraphStyle('info_banco', fontSize=11, textColor=colors.HexColor('#0066CC'), 
                                             spaceAfter=10, fontName='Helvetica-Bold')
        
        story.append(Paragraph('<b>Información para transferencias:</b>', info_bancaria_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Tabla de datos bancarios
        datos_bancarios = [
            ['Banco:', 'BBVA'],
            ['Titular:', 'EDGAR ARTURO GUERRA ZERMEÑO'],
            ['Cuenta:', '274 864 8042'],
            ['CLABE:', '012 010 02748648042 5']
        ]
        
        tabla_bancaria = Table(datos_bancarios, colWidths=[1.2*inch, 4*inch])
        tabla_bancaria.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#555555')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        
        # Contenedor con borde
        container_bancario = Table([[tabla_bancaria]], colWidths=[5.5*inch])
        container_bancario.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        story.append(container_bancario)
        story.append(Spacer(1, 0.4*inch))
        
        # Condiciones Comerciales (si existen)
        condiciones_texto = cotizacion_data.get('condiciones_comerciales', '')
        if condiciones_texto and condiciones_texto.strip():
            story.append(Paragraph('<b>Condiciones Comerciales:</b>', info_bancaria_style))
            story.append(Spacer(1, 0.1*inch))
            
            condiciones_style = ParagraphStyle('condiciones', fontSize=9, textColor=colors.HexColor('#555555'), 
                                              leftIndent=10, spaceAfter=6)
            
            # Dividir por líneas y agregar cada una
            for linea in condiciones_texto.split('\n'):
                if linea.strip():
                    story.append(Paragraph(linea, condiciones_style))
            
            story.append(Spacer(1, 0.3*inch))
        
        # Políticas Comerciales
        story.append(Paragraph('<b>Políticas Comerciales:</b>', info_bancaria_style))
        story.append(Spacer(1, 0.1*inch))
        
        politicas = [
            '1. Los tiempos de entrega e inicio de servicio corren a partir de la comprobación del pago del anticipo o su totalidad dentro de las 24 a 48 horas.',
            '2. Enviar por favor el comprobante de pago a administracion@integrational3.com.mx.',
            '3. Para facturar, enviar Constancia de Situación Fiscal y comprobante el mismo día.',
            '4. No se aceptan cancelaciones ni devoluciones en servicios, licencias o pedidos especiales.',
            '5. Precios sujetos a cambio sin previo aviso hasta confirmar el pago, debido a variaciones en tipo de cambio.'
        ]
        
        politicas_style = ParagraphStyle('politicas', fontSize=8, textColor=colors.HexColor('#555555'), 
                                        leftIndent=5, spaceAfter=5, alignment=TA_JUSTIFY)
        
        for politica in politicas:
            story.append(Paragraph(politica, politicas_style))
        
        story.append(Spacer(1, 0.4*inch))
        
        # Mensaje final
        mensaje_final = '<i>Gracias por su preferencia. Para cualquier duda o aclaración, no dude en contactarnos.</i>'
        mensaje_style = ParagraphStyle('mensaje', fontSize=9, textColor=colors.HexColor('#999999'), 
                                       alignment=TA_CENTER)
        story.append(Paragraph(mensaje_final, mensaje_style))
        
        # Función para el pie de página
        def footer(canvas_obj, doc_obj):
            canvas_obj.saveState()
            
            # Configuración de zona horaria México
            tz_mexico = pytz.timezone('America/Mexico_City')
            fecha_generacion = datetime.now(tz_mexico).strftime('%d/%m/%Y %H:%M')
            
            # Información del usuario que generó la cotización
            usuario_nombre = cotizacion_data.get('creado_por_nombre') or 'Usuario no registrado'
            
            # Línea separadora
            canvas_obj.setStrokeColor(colors.HexColor('#CCCCCC'))
            canvas_obj.setLineWidth(0.5)
            canvas_obj.line(40, 40, letter[0] - 40, 40)
            
            # Texto del pie de página - Izquierda: Usuario y fecha
            canvas_obj.setFont('Helvetica', 7)
            canvas_obj.setFillColor(colors.HexColor('#666666'))
            canvas_obj.drawString(40, 28, f'Generado por: {usuario_nombre}')
            canvas_obj.drawString(40, 18, f'Fecha de generación: {fecha_generacion}')
            
            # Texto del pie de página - Derecha: Número de página
            canvas_obj.setFont('Helvetica', 7)
            page_num = canvas_obj.getPageNumber()
            canvas_obj.drawRightString(letter[0] - 40, 28, f'Página {page_num}')
            canvas_obj.drawRightString(letter[0] - 40, 18, f'{cotizacion_data["numero_cotizacion"]}')
            
            canvas_obj.restoreState()
        
        # Construir PDF con footer
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        
        return filepath
