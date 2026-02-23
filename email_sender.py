import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from config import Config

class EmailSender:
    """Manejador de envío de correos electrónicos"""
    
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email = Config.SMTP_EMAIL
        self.password = Config.SMTP_PASSWORD
    
    def enviar_cotizacion_email(self, destinatario, cotizacion_data, pdf_path=None, adjuntos=None):
        """
        Enviar cotización por correo electrónico
        
        Args:
            destinatario: Email del destinatario
            cotizacion_data: Datos de la cotización
            pdf_path: Ruta del PDF adjunto (opcional)
            adjuntos: Lista de adjuntos extra (opcional)
        
        Returns:
            True si el envío fue exitoso, False en caso contrario
        """
        try:
            print(f"[EMAIL] Iniciando envío a {destinatario}")
            print(f"[EMAIL] Servidor: {self.smtp_server}:{self.smtp_port}")
            print(f"[EMAIL] Usuario: {self.email}")
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = formataddr(("Cotización Integrational3", self.email))
            msg['To'] = destinatario
            msg['Subject'] = f"Cotización {cotizacion_data['numero_cotizacion']} - {Config.EMPRESA_NOMBRE}"
            
            print(f"[EMAIL] Generando cuerpo HTML...")
            # Cuerpo del correo en HTML
            html_body = self._generar_html_cotizacion(cotizacion_data)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Adjuntar PDF si existe
            if pdf_path and os.path.exists(pdf_path):
                print(f"[EMAIL] Adjuntando PDF: {pdf_path}")
                with open(pdf_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition', 
                        'attachment', 
                        filename=os.path.basename(pdf_path)
                    )
                    msg.attach(pdf_attachment)

            # Adjuntar archivos adicionales si existen
            if adjuntos:
                for adjunto in adjuntos:
                    ruta = adjunto.get('ruta_archivo')
                    nombre = adjunto.get('nombre_original') or os.path.basename(ruta or '')
                    if not ruta or not os.path.exists(ruta):
                        continue
                    print(f"[EMAIL] Adjuntando archivo: {ruta}")
                    with open(ruta, 'rb') as f:
                        extra_attachment = MIMEApplication(f.read())
                        extra_attachment.add_header(
                            'Content-Disposition',
                            'attachment',
                            filename=nombre
                        )
                        msg.attach(extra_attachment)
            
            # Enviar correo
            print(f"[EMAIL] Conectando al servidor SMTP...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.set_debuglevel(1)  # Activar debug
                print(f"[EMAIL] Iniciando TLS...")
                server.starttls()
                print(f"[EMAIL] Autenticando...")
                server.login(self.email, self.password)
                print(f"[EMAIL] Enviando mensaje...")
                server.send_message(msg)
            
            print(f"[EMAIL] ✓ Email enviado exitosamente")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Error de autenticación SMTP: {str(e)}"
            print(f"[EMAIL ERROR] {error_msg}")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP: {str(e)}"
            print(f"[EMAIL ERROR] {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Error al enviar correo: {str(e)}"
            print(f"[EMAIL ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg
    
    def _generar_html_cotizacion(self, cotizacion_data):
        """Generar HTML para el correo electrónico"""
        
        # Generar filas de items
        items_html = ""
        for item in cotizacion_data['items']:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{item['concepto']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{item.get('descripcion', '')}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{item['cantidad']}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">${item['precio_unitario']:,.2f}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">${item['subtotal']:,.2f}</td>
            </tr>
            """
        
        # Generar botones de aprobación si existe token
        botones_aprobacion = ""
        # TEMPORALMENTE DESHABILITADO - Descomentar para producción
        """
        if cotizacion_data.get('token_aprobacion'):
            base_url = Config.BASE_URL if hasattr(Config, 'BASE_URL') else 'http://localhost:5000'
            aprobar_url = f"{base_url}/aprobar/{cotizacion_data['token_aprobacion']}"
            rechazar_url = f"{base_url}/rechazar/{cotizacion_data['token_aprobacion']}"
            
            botones_aprobacion = f\"\"\"
                <div style="text-align: center; margin: 30px 0; padding: 20px; background: #f0f8ff; border-radius: 10px;">
                    <h3 style="color: #1a5490; margin-bottom: 15px;">¿Desea aprobar esta cotización?</h3>
                    <p style="color: #666; margin-bottom: 20px;">Haga clic en una de las opciones:</p>
                    <a href="{aprobar_url}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #28a745, #20c997); color: white; text-decoration: none; border-radius: 10px; font-weight: bold; margin: 10px; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);">✅ APROBAR COTIZACIÓN</a>
                    <a href="{rechazar_url}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #dc3545, #c82333); color: white; text-decoration: none; border-radius: 10px; font-weight: bold; margin: 10px; box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);">❌ RECHAZAR COTIZACIÓN</a>
                </div>
            \"\"\"
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #1a5490 0%, #2980b9 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .logo {{
                    max-width: 250px;
                    height: auto;
                    margin-bottom: 15px;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .info-box {{
                    background-color: white;
                    padding: 15px;
                    margin: 15px 0;
                    border-left: 4px solid #3498db;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background-color: white;
                }}
                th {{
                    background-color: #1a5490;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }}
                .totales {{
                    text-align: right;
                    margin: 20px 0;
                    font-size: 16px;
                }}
                .total-final {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #e74c3c;
                    margin-top: 10px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #ddd;
                    color: #777;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="{Config.EMPRESA_LOGO_URL}" alt="{Config.EMPRESA_NOMBRE}" class="logo">
                <h2 style="margin: 10px 0;">{Config.EMPRESA_SLOGAN}</h2>
                <p style="margin: 5px 0;">{Config.EMPRESA_DIRECCION}</p>
                <p style="margin: 5px 0;">Tel: {Config.EMPRESA_TELEFONO} | Email: {Config.EMPRESA_EMAIL}</p>
            </div>
            
            <div class="content">
                <h2>Cotización {cotizacion_data['numero_cotizacion']}</h2>
                
                <div class="info-box">
                    <p><strong>Estimado(a) {cotizacion_data['nombre']},</strong></p>
                    <p>Le presentamos nuestra cotización con los siguientes detalles:</p>
                </div>
                
                <div class="info-box">
                    <p><strong>Fecha:</strong> {cotizacion_data.get('fecha_creacion', 'N/A')}</p>
                    <p><strong>Válida hasta:</strong> {cotizacion_data.get('fecha_validez', 'N/A')}</p>
                </div>
                
                <h3>Conceptos:</h3>
                <table>
                    <thead>
                        <tr style="background-color: #1a5490;">
                            <th style="color: white; padding: 12px;">Concepto</th>
                            <th style="color: white; padding: 12px;">Descripción</th>
                            <th style="color: white; padding: 12px; text-align: center;">Cantidad</th>
                            <th style="color: white; padding: 12px; text-align: right;">Precio Unit.</th>
                            <th style="color: white; padding: 12px; text-align: right;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div class="totales">
                    <p><strong>Subtotal:</strong> ${cotizacion_data['subtotal']:,.2f}</p>
                    <p><strong>IVA (16%):</strong> ${cotizacion_data['iva']:,.2f}</p>
                    <p class="total-final">TOTAL: ${cotizacion_data['total']:,.2f}</p>
                </div>
                
                {"<div class='info-box'><h4>Notas:</h4><p>" + cotizacion_data.get('notas', '') + "</p></div>" if cotizacion_data.get('notas') else ""}
                
                {botones_aprobacion}
                
                <div class="info-box">
                    <p>Para cualquier duda o aclaración, no dude en contactarnos.</p>
                    <p>Quedamos a sus órdenes.</p>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>{Config.EMPRESA_NOMBRE}</strong></p>
                <p style="color: #1a5490; font-weight: 600;">{Config.EMPRESA_SLOGAN}</p>
                <p>{Config.EMPRESA_SITIO_WEB}</p>
                <p><em>Soluciones tecnológicas integrales para tu negocio</em></p>
                <p style="margin-top: 15px; font-size: 12px; color: #999;">Este correo fue generado automáticamente por nuestro sistema de cotizaciones</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def enviar_confirmacion_aprobacion(self, destinatario, cotizacion_data, estado, comentarios=''):
        """
        Enviar email de confirmación de aprobación/rechazo al cliente
        
        Args:
            destinatario: Email del cliente
            cotizacion_data: Datos de la cotización
            estado: 'aprobado' o 'rechazado'
            comentarios: Comentarios del cliente (opcional)
        """
        try:
            print(f"[EMAIL] Enviando confirmación de {estado} a {destinatario}")
            
            # Validar destinatario
            if not destinatario or '@' not in destinatario:
                print(f"[EMAIL] ✗ Email inválido: {destinatario}")
                return False
            
            # Usar alternative para incluir texto plano y HTML
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr(("Cotización Integrational3", self.email))
            msg['To'] = destinatario
            
            if estado == 'aprobado':
                msg['Subject'] = f"Confirmacion: Cotizacion {cotizacion_data['numero_cotizacion']} Aprobada"
                titulo = "Cotizacion Aprobada"
                mensaje = "Gracias por aprobar nuestra cotizacion"
                color = "#27ae60"
            else:
                msg['Subject'] = f"Confirmacion: Cotizacion {cotizacion_data['numero_cotizacion']} Rechazada"
                titulo = "Cotizacion Rechazada"
                mensaje = "Hemos recibido su respuesta sobre la cotizacion"
                color = "#e74c3c"
            
            # Crear versión texto plano (importante para evitar spam)
            texto_plano = f"""
{Config.EMPRESA_NOMBRE}
{Config.EMPRESA_SLOGAN}

{titulo}

{mensaje}

Detalles de la cotizacion:
- Numero de cotizacion: {cotizacion_data['numero_cotizacion']}
- Cliente: {cotizacion_data.get('cliente_nombre', cotizacion_data.get('nombre', 'N/A'))}
- Total: ${cotizacion_data['total']:,.2f}
- Estado: {estado.upper()}

{f'Sus comentarios: {comentarios}' if comentarios else ''}

Esta confirmacion ha sido enviada a: {destinatario}
Nuestro equipo se pondra en contacto con usted a la brevedad.

Si tiene alguna pregunta, no dude en contactarnos:
Tel: {Config.EMPRESA_TELEFONO}
Email: {Config.EMPRESA_EMAIL}
Web: {Config.EMPRESA_SITIO_WEB}

---
{Config.EMPRESA_NOMBRE}
Soluciones tecnologicas integrales para tu negocio
"""
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #1a5490 0%, #2980b9 100%);
                        color: white;
                        padding: 30px 20px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border: 1px solid #ddd;
                    }}
                    .estado-box {{
                        background-color: {color};
                        color: white;
                        padding: 20px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 20px 0;
                        font-size: 24px;
                    }}
                    .info-box {{
                        background-color: #f9f9f9;
                        padding: 15px;
                        margin: 15px 0;
                        border-left: 4px solid #3498db;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 2px solid #ddd;
                        color: #777;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{titulo}</h1>
                </div>
                
                <div class="content">
                    <div class="estado-box">
                        {mensaje}
                    </div>
                    
                    <div class="info-box">
                        <p><strong>Cotizacion:</strong> {cotizacion_data['numero_cotizacion']}</p>
                        <p><strong>Cliente:</strong> {cotizacion_data.get('cliente_nombre', cotizacion_data.get('nombre', 'N/A'))}</p>
                        <p><strong>Total:</strong> ${cotizacion_data['total']:,.2f}</p>
                        <p><strong>Estado:</strong> {estado.upper()}</p>
                    </div>
                    
                    {f'<div class="info-box"><p><strong>Sus comentarios:</strong></p><p>{comentarios}</p></div>' if comentarios else ''}
                    
                    <p>Esta confirmacion ha sido enviada a: <strong>{destinatario}</strong></p>
                    <p>Nuestro equipo se pondra en contacto con usted a la brevedad.</p>
                    
                    <p style="margin-top: 30px;">Si tiene alguna pregunta, no dude en contactarnos:</p>
                    <p>
                        Tel: {Config.EMPRESA_TELEFONO}<br>
                        Email: {Config.EMPRESA_EMAIL}<br>
                        Web: {Config.EMPRESA_SITIO_WEB}
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>{Config.EMPRESA_NOMBRE}</strong></p>
                    <p style="color: #1a5490; font-weight: 600;">{Config.EMPRESA_SLOGAN}</p>
                    <p><em>Soluciones tecnológicas integrales para tu negocio</em></p>
                </div>
            </body>
            </html>
            """
            
            # Adjuntar ambas versiones (texto plano primero, HTML después)
            parte_texto = MIMEText(texto_plano, 'plain', 'utf-8')
            parte_html = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(parte_texto)
            msg.attach(parte_html)
            
            # Conectar y enviar
            print(f"[EMAIL] Conectando al servidor SMTP...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            print(f"[EMAIL] Iniciando TLS...")
            server.starttls()
            print(f"[EMAIL] Autenticando...")
            server.login(self.email, self.password)
            print(f"[EMAIL] Enviando mensaje de confirmación...")
            server.send_message(msg)
            server.quit()
            
            print(f"[EMAIL] ✓ Confirmación de {estado} enviada exitosamente a {destinatario}")
            return True
            
        except Exception as e:
            print(f"[EMAIL] ✗ Error al enviar confirmación: {str(e)}")
            return False

    def verificar_configuracion(self):
        """Verificar si la configuración de email es válida"""
        if not self.email or not self.password:
            return False, "Configuración de email incompleta. Configure SMTP_EMAIL y SMTP_PASSWORD en el archivo .env"
        return True, "Configuración de email correcta"
