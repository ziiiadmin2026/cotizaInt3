# Dockerfile para Sistema de Cotización - Producción
FROM python:3.11-slim-bookworm

# Metadatos
LABEL maintainer="contacto@integrational3.com.mx"
LABEL description="Sistema de Cotización Local - Integrational3"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 -s /bin/bash appuser

# Crear directorio de la aplicación
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn gevent python-dotenv

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Crear directorios necesarios y asignar permisos
RUN mkdir -p /app/pdfs /app/uploads /app/uploads/productos /app/static/images && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/clientes || exit 1

# Comando de inicio
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
