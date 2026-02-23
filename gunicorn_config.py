"""
Configuración de Gunicorn para producción
Sistema de Cotización - Integrational3
"""
import multiprocessing
import os

# Server Socket
bind = '0.0.0.0:5000'
backlog = 2048

# Worker Processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gevent'  # Para manejar muchas conexiones simultáneas
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Restart workers
graceful_timeout = 30
preload_app = False

# Logging
accesslog = '/app/logs/access.log' if os.path.exists('/app/logs') else '-'
errorlog = '/app/logs/error.log' if os.path.exists('/app/logs') else '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = 'gunicorn_cotizador'

# Server Mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (si se usa)
# keyfile = '/app/ssl/key.pem'
# certfile = '/app/ssl/cert.pem'

def on_starting(server):
    """Llamado justo antes de que el master inicie"""
    print("=" * 60)
    print("Sistema de Cotización - Integrational3")
    print("Iniciando servidor Gunicorn...")
    print(f"Workers: {workers}")
    print(f"Worker class: {worker_class}")
    print(f"Bind: {bind}")
    print("=" * 60)

def on_reload(server):
    """Llamado para recargar la configuración"""
    print("Recargando configuración...")

def when_ready(server):
    """Llamado justo después de que el servidor esté iniciado"""
    print("Servidor listo!")

def worker_int(worker):
    """Llamado justo después de que un worker reciba la señal SIGINT o SIGQUIT"""
    print(f"Worker recibió señal de interrupción: {worker.pid}")

def worker_abort(worker):
    """Llamado cuando un worker recibe la señal SIGABRT"""
    print(f"Worker abortado: {worker.pid}")
