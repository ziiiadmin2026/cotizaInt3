// Funciones necesarias para nueva cotización
let productosCotizacion = [];
let itemCounterCotizacion = 0;
let inactividadTimerCotizacion = null;
let cotizacionEditandoLocal = null; // ID de cotización en edición
const TIEMPO_INACTIVIDAD_COTIZACION = 5 * 60 * 1000; // 5 minutos
let cotizacionJsInicializado = false;

// Inicialización (solo si estamos en la página dedicada de nueva cotización)
window.addEventListener('DOMContentLoaded', async () => {
    // Solo inicializar si estamos en la página /nueva-cotizacion
    if (!window.location.pathname.includes('/nueva-cotizacion')) {
        return; // Salir si estamos en el modal de index.html
    }
    
    try {
        const response = await fetch('/api/session');
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = '/login';
            return;
        }
        
        // Actualizar nombre de usuario
        if (document.getElementById('nombreUsuario')) {
            document.getElementById('nombreUsuario').textContent = data.usuario.nombre_completo;
        }
        
        // Cargar datos
        await cargarProductos();
        await cargarClientesSelect();
        
        // Event listeners
        const formCotizacion = document.getElementById('cotizacion-form');
        if (formCotizacion && !cotizacionJsInicializado) {
            formCotizacion.addEventListener('submit', crearCotizacion);
            cotizacionJsInicializado = true;
        }
        
        const adjuntosInput = document.getElementById('cotizacion-adjuntos');
        if (adjuntosInput) {
            adjuntosInput.addEventListener('change', renderAdjuntosSeleccionados);
        }
        const formProdRapido = document.getElementById('form-producto-rapido');
        if (formProdRapido) {
            formProdRapido.addEventListener('submit', crearProductoRapido);
        }
        
        // Protección del modal de producto rápido - NO permitir cierre con ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const modalProducto = document.getElementById('modal-producto-rapido');
                if (modalProducto && modalProducto.style.display === 'flex') {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        });
        
        // Verificar si se está editando una cotización
        const urlParams = new URLSearchParams(window.location.search);
        const editarId = urlParams.get('editar');
        
        if (editarId) {
            // Cargar cotización para editar
            await cargarCotizacionParaEditar(editarId);
        } else {
            // Agregar item inicial solo si es nueva cotización
            agregarItem();
        }
        
        // Iniciar temporizador de inactividad
        iniciarTemporizadorInactividad();
    } catch (error) {
        console.error('Error:', error);
        window.location.href = '/login';
    }
});

// Temporizador de inactividad
function iniciarTemporizadorInactividad() {
    const eventos = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    eventos.forEach(evento => {
        document.addEventListener(evento, resetearTemporizador, true);
    });
    resetearTemporizador();
}

function resetearTemporizador() {
    if (inactividadTimerCotizacion) {
        clearTimeout(inactividadTimerCotizacion);
    }
    inactividadTimerCotizacion = setTimeout(async () => {
        alert('Sesión cerrada por inactividad');
        try {
            await fetch('/api/logout', { method: 'POST' });
        } catch (error) {
            console.error('Error:', error);
        }
        window.location.href = '/login';
    }, TIEMPO_INACTIVIDAD_COTIZACION);
}

// Función para volver al inicio
function volverAlInicio() {
    if (confirm('¿Está seguro que desea salir? Los cambios no guardados se perderán.')) {
        window.location.href = '/';
    }
}

async function cargarProductos() {
    try {
        const response = await fetch('/api/productos');
        productosCotizacion = await response.json();
    } catch (error) {
        console.error('Error al cargar productos:', error);
    }
}

async function cargarClientesSelect() {
    try {
        const response = await fetch('/api/clientes');
        const clientes = await response.json();
        
        const select = document.getElementById('cotizacion-cliente');
        select.innerHTML = '<option value="">Seleccione un cliente...</option>';
        
        clientes.forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente.id;
            option.textContent = cliente.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar clientes:', error);
    }
}

function agregarItem() {
    itemCounterCotizacion++;
    const container = document.getElementById('items-container');
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'item-row';
    itemDiv.id = `item-${itemCounterCotizacion}`;
    itemDiv.innerHTML = `
        <div class="item-grid">
            <div class="form-group">
                <label>Producto/Servicio</label>
                <select class="item-producto" onchange="actualizarPrecioItem(${itemCounterCotizacion})">
                    <option value="">Seleccione...</option>
                    ${productosCotizacion.map(p => `<option value="${p.id}" data-precio="${p.precio}">${p.nombre}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Descripción</label>
                <input type="text" class="item-descripcion" placeholder="Descripción detallada">
            </div>
            <div class="form-group">
                <label>Cantidad</label>
                <input type="number" class="item-cantidad" value="1" min="0" oninput="calcularTotales()">
            </div>
            <div class="form-group">
                <label>Precio Unitario</label>
                <input type="number" class="item-precio" step="0.01" min="0" oninput="calcularTotales()">
            </div>
            <div class="form-group">
                <button type="button" class="btn btn-success" onclick="abrirModalProductoRapido(${itemCounterCotizacion})" style="white-space: nowrap;">Nuevo</button>
            </div>
            <div class="form-group">
                <button type="button" class="btn btn-danger btn-sm" onclick="eliminarItem(${itemCounterCotizacion})">Eliminar</button>
            </div>
        </div>
    `;
    
    container.appendChild(itemDiv);
    calcularTotales();
}

function eliminarItem(itemId) {
    const item = document.getElementById(`item-${itemId}`);
    if (item) {
        item.remove();
        calcularTotales();
    }
}

function actualizarPrecioItem(itemId) {
    const itemDiv = document.getElementById(`item-${itemId}`);
    const select = itemDiv.querySelector('.item-producto');
    const selectedOption = select.options[select.selectedIndex];
    const precio = selectedOption.getAttribute('data-precio');
    
    if (precio) {
        itemDiv.querySelector('.item-precio').value = precio;
        
        const productoId = select.value;
        const producto = productosCotizacion.find(p => p.id == productoId);
        if (producto && producto.descripcion) {
            itemDiv.querySelector('.item-descripcion').value = producto.descripcion;
        }
    }
    
    calcularTotales();
}

function calcularTotales() {
    const items = document.querySelectorAll('.item-row');
    let subtotal = 0;
    
    items.forEach(item => {
        const cantidad = parseFloat(item.querySelector('.item-cantidad').value) || 0;
        const precio = parseFloat(item.querySelector('.item-precio').value) || 0;
        subtotal += cantidad * precio;
    });
    
    const iva = subtotal * 0.16;
    const total = subtotal + iva;
    
    document.getElementById('subtotal-display').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('iva-display').textContent = `$${iva.toFixed(2)}`;
    document.getElementById('total-display').textContent = `$${total.toFixed(2)}`;
}

async function crearCotizacion(e) {
    e.preventDefault();

    const esEdicion = Boolean(cotizacionEditandoLocal);
    
    const items = [];
    document.querySelectorAll('.item-row').forEach(itemDiv => {
        const productoSelect = itemDiv.querySelector('.item-producto');
        const cantidad = parseFloat(itemDiv.querySelector('.item-cantidad').value) || 0;
        const precio = parseFloat(itemDiv.querySelector('.item-precio').value) || 0;
        
        if (cantidad > 0 && precio >= 0) {
            items.push({
                producto_id: productoSelect.value || null,
                concepto: productoSelect.options[productoSelect.selectedIndex].text,
                descripcion: itemDiv.querySelector('.item-descripcion').value,
                cantidad: cantidad,
                precio_unitario: precio
            });
        }
    });
    
    if (items.length === 0) {
        alert('Debe agregar al menos un concepto');
        return;
    }
    
    const data = {
        cliente_id: document.getElementById('cotizacion-cliente').value,
        fecha_validez: document.getElementById('cotizacion-validez').value,
        items: items,
        notas: document.getElementById('cotizacion-notas').value,
        condiciones_comerciales: document.getElementById('cotizacion-condiciones').value
    };
    
    try {
        let response;
        if (esEdicion) {
            // Actualizar cotización existente
            response = await fetch(`/api/cotizaciones/${cotizacionEditandoLocal}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
        } else {
            // Crear nueva cotización
            response = await fetch('/api/cotizaciones', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
        }
        
        if (response.ok) {
            const result = await response.json();
            const cotizacionId = cotizacionEditandoLocal || result.cotizacion_id;

            if (!cotizacionEditandoLocal) {
                cotizacionEditandoLocal = cotizacionId;
            }

            const adjuntosResult = await subirAdjuntos(cotizacionId);
            if (!adjuntosResult.success) {
                alert(`Adjuntos: ${adjuntosResult.message}`);
                if (!esEdicion) {
                    await cargarCotizacionParaEditar(cotizacionId);
                }
                return;
            }

            // Detectar si estamos en modal o página dedicada
            const modalNuevaCot = document.getElementById('modalNuevaCotizacion');
            const esModal = modalNuevaCot && modalNuevaCot.style.display !== 'none';
            
            if (esModal) {
                // Estamos en el modal dentro de index.html
                if (typeof showNotification === 'function') {
                    showNotification(esEdicion ? 'Cotización actualizada exitosamente' : 'Cotización creada exitosamente', 'success');
                } else {
                    alert(esEdicion ? 'Cotización actualizada exitosamente' : 'Cotización creada exitosamente');
                }
                
                // Cerrar modal
                if (typeof cerrarModalNuevaCotizacion === 'function') {
                    cerrarModalNuevaCotizacion();
                }
                
                // Recargar cotizaciones si la función existe
                if (typeof cargarCotizaciones === 'function') {
                    await cargarCotizaciones();
                }
                
                // Cambiar a la pestaña de cotizaciones
                if (typeof showTab === 'function') {
                    showTab('cotizaciones');
                }
            } else {
                // Estamos en la página dedicada /nueva-cotizacion
                alert(esEdicion ? 'Cotización actualizada exitosamente' : 'Cotización creada exitosamente');
                setTimeout(() => window.location.href = '/', 1000);
            }
        } else {
            const error = await response.json();
            alert('Error: ' + (error.message || 'Error al procesar cotización'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al procesar cotización');
    }
}

function abrirModalProductoRapido(itemId) {
    // Guardar el ID del item para usarlo después
    document.getElementById('prod-item-id').value = itemId;
    document.getElementById('modal-producto-rapido').style.display = 'flex';
    
    // Limpiar formulario
    document.getElementById('form-producto-rapido').reset();
    // Establecer valores por defecto
    document.getElementById('prod-activo').value = '1';
    document.getElementById('prod-tipo').value = 'producto';
    document.getElementById('prod-unidad').value = 'pza';
    
    // Limpiar preview de imagen
    const preview = document.getElementById('prod-imagen-preview');
    if (preview) {
        preview.innerHTML = '<span class="imagen-preview-text-rapido">Sin imagen</span>';
    }
    
    // Agregar listener para URL de imagen si no existe
    const imagenUrlInput = document.getElementById('prod-imagen-url');
    if (imagenUrlInput && !imagenUrlInput.hasAttribute('data-listener-added')) {
        imagenUrlInput.addEventListener('input', function() {
            actualizarPreviewImagenRapido(this.value);
        });
        imagenUrlInput.setAttribute('data-listener-added', 'true');
    }
    
}

function cerrarModalProductoRapido() {
    document.getElementById('modal-producto-rapido').style.display = 'none';
    document.getElementById('form-producto-rapido').reset();
    
    // Limpiar preview de imagen
    const preview = document.getElementById('prod-imagen-preview');
    if (preview) {
        preview.innerHTML = '<span class="imagen-preview-text-rapido">Sin imagen</span>';
    }
    
    // Limpiar input de archivo de imagen
    const fileInput = document.getElementById('prod-imagen-file');
    if (fileInput) {
        fileInput.value = '';
    }
}

async function crearProductoRapido(e) {
    e.preventDefault();
    
    const data = {
        codigo: document.getElementById('prod-codigo').value.trim(),
        tipo: document.getElementById('prod-tipo').value,
        nombre: document.getElementById('prod-nombre').value.trim(),
        descripcion: document.getElementById('prod-descripcion').value.trim(),
        precio: parseFloat(document.getElementById('prod-precio').value),
        unidad: document.getElementById('prod-unidad').value,
        categoria: document.getElementById('prod-categoria').value.trim(),
        activo: parseInt(document.getElementById('prod-activo').value),
        imagen_url: document.getElementById('prod-imagen-url').value.trim() || null
    };
    
    // Validar datos
    if (!data.codigo || !data.nombre || !data.precio) {
        alert('Por favor completa todos los campos obligatorios');
        return;
    }
    
    try {
        const response = await fetch('/api/productos', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            // Recargar productos
            await cargarProductos();
            
            // Obtener el item ID para actualizar el select
            const itemId = document.getElementById('prod-item-id').value;
            if (itemId) {
                const itemDiv = document.getElementById(`item-${itemId}`);
                if (itemDiv) {
                    const select = itemDiv.querySelector('.item-producto');
                    
                    // Agregar el nuevo producto al select y seleccionarlo
                    const nuevoProducto = productosCotizacion[productosCotizacion.length - 1];
                    const option = document.createElement('option');
                    option.value = nuevoProducto.id;
                    option.setAttribute('data-precio', nuevoProducto.precio);
                    option.setAttribute('data-descripcion', nuevoProducto.descripcion || '');
                    option.textContent = `${nuevoProducto.codigo} - ${nuevoProducto.nombre}`;
                    option.selected = true;
                    select.appendChild(option);
                    
                    // Actualizar precio automáticamente
                    actualizarPrecioItem(itemId);
                }
            }
            
            cerrarModalProductoRapido();
            
            // Mostrar notificación de éxito
            mostrarNotificacion('✅ Producto creado exitosamente', 'success');
        } else {
            alert(result.message || 'Error al crear producto');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al crear producto. Por favor intenta nuevamente.');
    }
}

// Función para subir imagen local en modal de producto rápido
async function subirImagenProductoRapido() {
    const fileInput = document.getElementById('prod-imagen-file');
    const file = fileInput ? fileInput.files[0] : null;
    
    if (!file) {
        mostrarNotificacion('Por favor selecciona una imagen', 'warning');
        return;
    }
    
    // Validar tipo de archivo
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        mostrarNotificacion('Tipo de archivo no permitido. Use PNG, JPG, JPEG, GIF o WEBP', 'error');
        return;
    }
    
    // Validar tamaño (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        mostrarNotificacion('La imagen no debe superar 5 MB', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('imagen', file);
    
    const btnUpload = document.getElementById('btn-subir-imagen-rapido');
    const originalText = btnUpload ? btnUpload.textContent : '';
    
    try {
        if (btnUpload) {
            btnUpload.disabled = true;
            btnUpload.textContent = '⏳ Subiendo...';
        }
        
        mostrarNotificacion('Subiendo imagen...', 'info');
        const response = await fetch('/api/productos/upload-imagen', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.success) {
            document.getElementById('prod-imagen-url').value = data.url;
            actualizarPreviewImagenRapido(data.url);
            mostrarNotificacion('¡Imagen subida exitosamente!', 'success');
            fileInput.value = '';
        } else {
            mostrarNotificacion(data.message || 'Error al subir imagen', 'error');
        }
    } catch (error) {
        console.error('Error al subir imagen:', error);
        mostrarNotificacion('Error al subir imagen', 'error');
    } finally {
        if (btnUpload) {
            btnUpload.disabled = false;
            btnUpload.textContent = originalText || '📤 Subir Imagen';
        }
    }
}

// Actualizar preview de imagen en modal de producto rápido
function actualizarPreviewImagenRapido(url) {
    const preview = document.getElementById('prod-imagen-preview');
    
    if (!url || url.trim() === '') {
        preview.innerHTML = '<span class="imagen-preview-text-rapido">Sin imagen</span>';
        return;
    }
    
    // Crear elemento de imagen
    const img = document.createElement('img');
    img.src = url;
    img.alt = 'Preview';
    img.onerror = function() {
        preview.innerHTML = '<span class="imagen-preview-text-rapido">⚠️ Error al cargar imagen</span>';
    };
    
    preview.innerHTML = '';
    preview.appendChild(img);
}

// Listener para actualizar preview cuando se cambia la URL manualmente
document.addEventListener('DOMContentLoaded', function() {
    // Agregar listener para cambio de URL de imagen (solo si existe el elemento)
    const imagenUrlInput = document.getElementById('prod-imagen-url');
    if (imagenUrlInput && !imagenUrlInput.hasAttribute('data-listener-added')) {
        imagenUrlInput.addEventListener('input', function() {
            actualizarPreviewImagenRapido(this.value);
        });
        imagenUrlInput.setAttribute('data-listener-added', 'true');
    }
});

// Cargar cotización para editar
async function cargarCotizacionParaEditar(cotizacionId) {
    try {
        const response = await fetch(`/api/cotizaciones/${cotizacionId}`);
        const cotizacion = await response.json();
        
        // Guardar ID de cotización en edición
        cotizacionEditandoLocal = cotizacionId;
        
        // Cargar datos en el formulario
        document.getElementById('cotizacion-cliente').value = cotizacion.cliente_id;
        document.getElementById('cotizacion-validez').value = cotizacion.fecha_validez || '';
        document.getElementById('cotizacion-notas').value = cotizacion.notas || '';
        
        const condicionesField = document.getElementById('cotizacion-condiciones');
        if (condicionesField) {
            condicionesField.value = cotizacion.condiciones_comerciales || '';
        }

        renderAdjuntosExistentes(cotizacion.adjuntos || []);
        
        // Limpiar items actuales
        const container = document.getElementById('items-container');
        container.innerHTML = '';
        itemCounterCotizacion = 0;
        
        // Cargar items de la cotización
        for (const item of cotizacion.items) {
            agregarItem();
            
            // Esperar que el item se agregue al DOM
            await new Promise(resolve => setTimeout(resolve, 50));
            
            const itemDiv = document.getElementById(`item-${itemCounterCotizacion}`);
            if (itemDiv) {
                const productoSelect = itemDiv.querySelector('.item-producto');
                const conceptoInput = itemDiv.querySelector('.item-concepto');
                const descripcionInput = itemDiv.querySelector('.item-descripcion');
                const cantidadInput = itemDiv.querySelector('.item-cantidad');
                const precioInput = itemDiv.querySelector('.item-precio');
                
                // Si tiene producto_id, seleccionarlo
                if (item.producto_id && productoSelect) {
                    productoSelect.value = item.producto_id;
                }
                
                if (conceptoInput) conceptoInput.value = item.concepto;
                if (descripcionInput) descripcionInput.value = item.descripcion || '';
                if (cantidadInput) cantidadInput.value = item.cantidad;
                if (precioInput) precioInput.value = item.precio_unitario;
            }
        }
        
        calcularTotales();
        
        // Cambiar títulos de la página
        const tituloHeader = document.querySelector('header h2');
        if (tituloHeader) {
            tituloHeader.textContent = 'Editar Cotización';
        }
        
        const tituloSeccion = document.querySelector('.tab-content h2');
        if (tituloSeccion) {
            tituloSeccion.textContent = 'Editar Cotización';
        }
        
        // Cambiar texto del botón
        const btnSubmit = document.querySelector('#cotizacion-form button[type="submit"]');
        if (btnSubmit) {
            btnSubmit.innerHTML = '💾 Actualizar Cotización';
        }
        
    } catch (error) {
        console.error('Error al cargar cotización:', error);
        alert('Error al cargar cotización: ' + error.message);
    }
}

function renderAdjuntosExistentes(adjuntos) {
    const contenedor = document.getElementById('adjuntos-existentes');
    if (!contenedor) return;

    contenedor.innerHTML = '';
    if (!adjuntos.length) return;

    const titulo = document.createElement('p');
    titulo.textContent = 'Adjuntos actuales:';
    contenedor.appendChild(titulo);

    const lista = document.createElement('ul');
    adjuntos.forEach(adjunto => {
        const item = document.createElement('li');
        item.textContent = adjunto.nombre_original;
        lista.appendChild(item);
    });
    contenedor.appendChild(lista);
}

function renderAdjuntosSeleccionados() {
    const input = document.getElementById('cotizacion-adjuntos');
    const contenedor = document.getElementById('adjuntos-seleccionados');
    if (!input || !contenedor) return;

    contenedor.innerHTML = '';
    const archivos = Array.from(input.files || []);
    if (archivos.length === 0) return;

    const titulo = document.createElement('p');
    titulo.textContent = 'Adjuntos por subir:';
    contenedor.appendChild(titulo);

    const lista = document.createElement('ul');
    archivos.forEach(archivo => {
        const item = document.createElement('li');
        item.textContent = archivo.name;
        lista.appendChild(item);
    });
    contenedor.appendChild(lista);
}

async function subirAdjuntos(cotizacionId) {
    const input = document.getElementById('cotizacion-adjuntos');
    if (!input || !input.files || input.files.length === 0) {
        return { success: true };
    }

    const formData = new FormData();
    Array.from(input.files).forEach(archivo => {
        formData.append('archivos', archivo);
    });

    try {
        const response = await fetch(`/api/cotizaciones/${cotizacionId}/adjuntos`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (!response.ok) {
            return { success: false, message: result.message || 'Error al subir adjuntos' };
        }

        return { success: true };
    } catch (error) {
        console.error('Error al subir adjuntos:', error);
        return { success: false, message: 'Error al subir adjuntos' };
    }
}

// Función auxiliar para mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'success') {
    // Buscar elemento de notificación o alert simple
    const notifElement = document.getElementById('notification');
    
    if (notifElement) {
        notifElement.textContent = mensaje;
        notifElement.className = `notification ${tipo}`;
        notifElement.style.display = 'block';
        
        setTimeout(() => {
            notifElement.style.display = 'none';
        }, 3000);
    } else {
        // Fallback a alert si no hay elemento de notificación
        if (tipo === 'success') {
            alert(mensaje);
        }
    }
}
