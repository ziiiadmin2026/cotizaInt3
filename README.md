# 📋 Sistema de Cotización - Integrational3

Sistema profesional de gestión de cotizaciones con generación de PDFs y envío automático de correos electrónicos para **Integrational3 - Soluciones Tecnológicas Integrales**, desarrollado con Python Flask.

![Integrational3](https://integrational3.com.mx/logorigen/integrational_std2.png)

## 🌟 Características

- ✅ **Gestión de Clientes**: Registro y administración de clientes
- 📋 **Creación de Cotizaciones**: Interfaz intuitiva para crear cotizaciones detalladas
- 📄 **Generación de PDFs**: Cotizaciones profesionales en formato PDF
- ✉️ **Envío de Emails**: Envío automático de cotizaciones por correo electrónico
- 💾 **Base de Datos Local**: Almacenamiento SQLite sin necesidad de servidor
- 🎨 **Interfaz Moderna**: Diseño responsive y fácil de usar
- 📊 **Cálculo Automático**: IVA y totales calculados automáticamente

## 🛠️ Tecnologías

- **Backend**: Python 3.x con Flask
- **Base de Datos**: SQLite
- **Generación PDF**: ReportLab
- **Envío de Emails**: SMTP (smtplib)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## � Despliegue con Docker (Recomendado para Producción)

### Inicio Rápido con Docker

1. **Configurar variables de entorno**:
```bash
cp .env.example .env
nano .env  # Editar con tus credenciales
```

2. **Verificar configuración**:
```bash
python verify_deployment.py
```

3. **Desplegar**:
```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
.\deploy.ps1 -Build

# Manual
docker compose up -d
```

4. **Acceder**: http://localhost:5000

📖 **Documentación completa**: Ver [DEPLOYMENT.md](DEPLOYMENT.md) para guía detallada de producción.

---

## 📦 Instalación Tradicional (Desarrollo)

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
```

3. **Activar el entorno virtual**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

5. **Configurar variables de entorno**:
   - Copiar `.env.example` a `.env`:
     ```bash
     copy .env.example .env
     ```
   - Editar `.env` con tus configuraciones:
     ```
     SMTP_SERVER=smtp.gmail.com
     SMTP_PORT=587
     SMTP_EMAIL=tu_email@gmail.com
     SMTP_PASSWORD=tu_contraseña_de_aplicacion
     ```

   **Nota para Gmail**: 
   - Ve a tu cuenta de Google
   - Habilita la verificación en 2 pasos
   - Genera una contraseña de aplicación en [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Usa esa contraseña en `SMTP_PASSWORD`

## 🚀 Uso

### Iniciar el Servidor

```bash
python app.py
```

El servidor se iniciará en `http://localhost:5000`

### Usar la Aplicación

1. **Registrar Clientes**:
   - Ve a la pestaña "👥 Clientes"
   - Haz clic en "➕ Nuevo Cliente"
   - Completa el formulario con los datos del cliente

2. **Crear Cotización**:
   - Ve a la pestaña "➕ Nueva Cotización"
   - Selecciona un cliente
   - Agrega los conceptos/productos
   - Los totales se calculan automáticamente
   - Haz clic en "💾 Crear Cotización"

3. **Gestionar Cotizaciones**:
   - Ve a la pestaña "📋 Cotizaciones"
   - Opciones disponibles:
     - **👁️ Ver**: Ver detalles completos
     - **📄 PDF**: Descargar en formato PDF
     - **✉️ Email**: Enviar por correo electrónico

## 📁 Estructura del Proyecto

```
Proyecto5Init(CotizadorLocal)/
│
├── .github/
│   └── copilot-instructions.md
│
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── pdfs/                    # PDFs generados (se crea automáticamente)
│
├── app.py                   # Aplicación Flask principal
├── config.py                # Configuración
├── database.py              # Gestión de base de datos
├── pdf_generator.py         # Generador de PDFs
├── email_sender.py          # Envío de emails
├── requirements.txt         # Dependencias
├── .env.example            # Plantilla de configuración
├── .gitignore
└── README.md
```

## 🔧 Configuración Avanzada

### Personalización de la Empresa

El sistema está configurado para **Integrational3**. Si necesitas cambiar los datos, edita el archivo `config.py`:

```python
EMPRESA_NOMBRE = 'Integrational3'
EMPRESA_SLOGAN = 'Soluciones Tecnológicas Integrales'
EMPRESA_DIRECCION = 'Aguascalientes, México'
EMPRESA_TELEFONO = '449 356 6356'
EMPRESA_EMAIL = 'proyectos@integrational3.com.mx'
EMPRESA_SITIO_WEB = 'www.integrational3.com.mx'
EMPRESA_LOGO_URL = 'https://integrational3.com.mx/logorigen/integrational_std2.png'
```

### Cambiar el Puerto del Servidor

En `app.py`, modifica:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia 5000 por el puerto deseado
```

### Configurar Otro Servidor SMTP

En `.env`, ajusta según tu proveedor:

**Outlook/Hotmail**:
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

**Yahoo**:
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

## 📧 API Endpoints

### Clientes

- `GET /api/clientes` - Obtener todos los clientes
- `POST /api/clientes` - Crear nuevo cliente
- `GET /api/clientes/<id>` - Obtener cliente específico

### Cotizaciones

- `GET /api/cotizaciones` - Obtener todas las cotizaciones
- `POST /api/cotizaciones` - Crear nueva cotización
- `GET /api/cotizaciones/<id>` - Obtener cotización específica
- `GET /api/cotizaciones/<id>/pdf` - Generar y descargar PDF
- `POST /api/cotizaciones/<id>/email` - Enviar por email
- `PUT /api/cotizaciones/<id>/estado` - Actualizar estado

### Configuración

- `GET /api/config` - Obtener configuración de la empresa

## 🐛 Solución de Problemas

### Error al enviar emails

**Problema**: "Error al enviar correo"

**Soluciones**:
1. Verifica que las credenciales en `.env` sean correctas
2. Para Gmail, asegúrate de usar una contraseña de aplicación
3. Verifica que tu firewall permita conexiones SMTP
4. Algunos proveedores requieren habilitar "Aplicaciones menos seguras"

### Error al generar PDFs

**Problema**: "Error al generar PDF"

**Soluciones**:
1. Verifica que ReportLab esté instalado: `pip install reportlab`
2. Asegúrate de que el directorio `pdfs/` tenga permisos de escritura

### Base de datos bloqueada

**Problema**: "Database is locked"

**Solución**:
- Cierra todas las conexiones a la base de datos
- Reinicia el servidor Flask

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y comercial.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes preguntas o problemas, por favor abre un issue en el repositorio.

## 🎯 Roadmap

- [ ] Autenticación de usuarios
- [ ] Múltiples impuestos personalizables
- [ ] Exportación a Excel
- [ ] Plantillas de cotización personalizables
- [ ] Dashboard con estadísticas
- [ ] Historial de cambios en cotizaciones
- [ ] Recordatorios automáticos
- [ ] Integración con sistemas de pago

## ✨ Agradecimientos

Desarrollado con ❤️ usando tecnologías de código abierto.

---

**Nota**: Este sistema está diseñado para uso local en Windows. Para uso en producción, considera implementar medidas de seguridad adicionales.
