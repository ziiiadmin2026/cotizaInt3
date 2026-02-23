// Variables globales
let clientes = [];
let cotizaciones = [];
let productos = [];
let itemCounter = 0;
let usuarioActual = null;
let inactividadTimer = null;
const TIEMPO_INACTIVIDAD = 5 * 60 * 1000; // 5 minutos en milisegundos

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    verificarSesion();
    iniciarTemporizadorInactividad();
});

// Temporizador de inactividad
function iniciarTemporizadorInactividad() {
    // Eventos que detectan actividad del usuario
    const eventos = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    // Resetear temporizador en cualquier actividad
    eventos.forEach(evento => {
        document.addEventListener(evento, resetearTemporizador, true);
    });
    
    // Iniciar temporizador
    resetearTemporizador();
}

function resetearTemporizador() {
    // Limpiar temporizador anterior
    if (inactividadTimer) {
        clearTimeout(inactividadTimer);
    }
    
    // Iniciar nuevo temporizador
    inactividadTimer = setTimeout(() => {
        mostrarNotificacionInactividad();
        cerrarSesionPorInactividad();
    }, TIEMPO_INACTIVIDAD);
}

function mostrarNotificacionInactividad() {
    showNotification('Sesión cerrada por inactividad', 'warning');
}

async function cerrarSesionPorInactividad() {
    try {
        await fetch('/api/logout', { method: 'POST' });
    } catch (error) {
        console.error('Error al cerrar sesión:', error);
    }
    window.location.href = '/login';
}

// Verificar sesión del usuario
async function verificarSesion() {
    try {
        const response = await fetch('/api/session');
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = '/login';
            return;
        }
        
        usuarioActual = data.usuario;
        
        // Actualizar UI con información del usuario
        document.getElementById('nombreUsuario').textContent = usuarioActual.nombre_completo;
        
        // Mostrar sección de administración solo para admin
        if (usuarioActual.rol === 'admin') {
            const adminSection = document.getElementById('admin-section');
            if (adminSection) {
                adminSection.style.display = 'block';
            }
        }
        
        // Event listeners
        document.getElementById('cliente-form').addEventListener('submit', crearCliente);
        
        // Solo agregar listener de cotizacion-form si existe (página nueva-cotizacion)
        const cotizacionForm = document.getElementById('cotizacion-form');
        if (cotizacionForm) {
            cotizacionForm.addEventListener('submit', crearCotizacion);
        }
        
        document.getElementById('form-producto-rapido').addEventListener('submit', crearProductoRapido);
        
        // Cargar datos (productos primero, luego agregar item inicial solo si existe el contenedor)
        await cargarProductos();
        cargarClientes();
        cargarCotizaciones();
        
        // Agregar un item inicial después de cargar productos (solo en página nueva-cotizacion)
        const itemsContainer = document.getElementById('items-container');
        if (itemsContainer) {
            agregarItem();
        }
        
    } catch (error) {
        console.error('Error al verificar sesión:', error);
        window.location.href = '/login';
    }
}

// Cerrar sesión
async function cerrarSesion() {
    try {
        await fetch('/api/logout', {
            method: 'POST'
        });
        window.location.href = '/login';
    } catch (error) {
        console.error('Error al cerrar sesión:', error);
    }
}

// Navegación de pestañas
function showTab(tabName) {
    // Ocultar todas las pestañas
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remover active de nav-items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    
    // Mostrar la pestaña seleccionada
    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Activar nav-item correspondiente y actualizar breadcrumb
    navItems.forEach(item => {
        const itemOnclick = item.getAttribute('onclick');
        if (itemOnclick && itemOnclick.includes(`'${tabName}'`)) {
            item.classList.add('active');
        }
    });
    
    // Actualizar breadcrumb
    const breadcrumbMap = {
        'clientes': 'Inicio / Clientes',
        'cotizaciones': 'Inicio / Cotizaciones'
    };
    const breadcrumbEl = document.getElementById('breadcrumb-text');
    if (breadcrumbEl && breadcrumbMap[tabName]) {
        breadcrumbEl.textContent = breadcrumbMap[tabName];
    }
    
    // Cerrar sidebar en móvil
    const sidebar = document.getElementById('sidebar');
    if (sidebar && window.innerWidth <= 768) {
        sidebar.classList.remove('active');
    }
    
    // Recargar datos si es necesario
    if (tabName === 'clientes') {
        cargarClientes();
    } else if (tabName === 'cotizaciones') {
        cargarCotizaciones();
    }
}

// Gestión de Clientes
function mostrarFormularioCliente() {
    document.getElementById('form-cliente').style.display = 'block';
}

function ocultarFormularioCliente() {
    document.getElementById('form-cliente').style.display = 'none';
    document.getElementById('cliente-form').reset();
    delete document.getElementById('cliente-form').dataset.clienteId;
    document.querySelector('#form-cliente h3').textContent = 'Nuevo Cliente';
}

async function cargarClientes() {
    try {
        const response = await fetch('/api/clientes');
        clientes = await response.json();
        
        // Actualizar badge
        const badgeClientes = document.getElementById('badge-clientes');
        if (badgeClientes) {
            badgeClientes.textContent = clientes.length;
        }
        
        const tbody = document.getElementById('clientes-tbody');
        
        if (clientes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No hay clientes registrados</td></tr>';
            return;
        }
        
        tbody.innerHTML = clientes.map(cliente => `
            <tr>
                <td>${cliente.nombre}</td>
                <td>${cliente.email}</td>
                <td>${cliente.telefono || 'N/A'}</td>
                <td>${cliente.rfc || 'N/A'}</td>
                <td>
                    <button class="btn btn-small btn-primary" onclick="editarCliente(${cliente.id})">Editar</button>
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error al cargar clientes:', error);
        showNotification('Error al cargar clientes', 'error');
    }
}

async function editarCliente(clienteId) {
    try {
        const response = await fetch(`/api/clientes/${clienteId}`);
        const cliente = await response.json();
        
        // Cambiar título del formulario
        document.querySelector('#form-cliente h3').textContent = 'Editar Cliente';
        
        // Llenar formulario con datos del cliente
        document.getElementById('cliente-nombre').value = cliente.nombre;
        document.getElementById('cliente-email').value = cliente.email;
        document.getElementById('cliente-telefono').value = cliente.telefono || '';
        document.getElementById('cliente-direccion').value = cliente.direccion || '';
        document.getElementById('cliente-rfc').value = cliente.rfc || '';
        
        // Guardar ID del cliente en el formulario
        document.getElementById('cliente-form').dataset.clienteId = clienteId;
        
        // Mostrar formulario
        document.getElementById('form-cliente').style.display = 'block';
        
    } catch (error) {
        console.error('Error al cargar cliente:', error);
        showNotification('Error al cargar cliente', 'error');
    }
}

async function crearCliente(e) {
    e.preventDefault();
    
    const clienteId = e.target.dataset.clienteId;
    const clienteData = {
        nombre: document.getElementById('cliente-nombre').value,
        email: document.getElementById('cliente-email').value,
        telefono: document.getElementById('cliente-telefono').value,
        direccion: document.getElementById('cliente-direccion').value,
        rfc: document.getElementById('cliente-rfc').value
    };
    
    try {
        let response;
        if (clienteId) {
            // Actualizar cliente existente
            response = await fetch(`/api/clientes/${clienteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(clienteData)
            });
        } else {
            // Crear nuevo cliente
            response = await fetch('/api/clientes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(clienteData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(clienteId ? 'Cliente actualizado exitosamente' : 'Cliente creado exitosamente', 'success');
            ocultarFormularioCliente();
            cargarClientes();
        } else {
            showNotification(result.message, 'error');
        }
        
    } catch (error) {
        console.error('Error al guardar cliente:', error);
        showNotification('Error al guardar cliente', 'error');
    }
}

// Gestión de Cotizaciones
async function cargarCotizaciones() {
    try {
        const response = await fetch('/api/cotizaciones');
        cotizaciones = await response.json();
        
        // Actualizar badge
        const badgeCotizaciones = document.getElementById('badge-cotizaciones');
        if (badgeCotizaciones) {
            badgeCotizaciones.textContent = cotizaciones.length;
        }
        
        const tbody = document.getElementById('cotizaciones-tbody');
        
        if (cotizaciones.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No hay cotizaciones registradas</td></tr>';
            return;
        }
        
        tbody.innerHTML = cotizaciones.map(cot => {
            const estadoAprobacion = cot.estado_aprobacion || 'pendiente';
            const iconoEstado = estadoAprobacion === 'aprobado' ? '✅' : 
                               estadoAprobacion === 'rechazado' ? '❌' : '⏳';
            const colorEstado = estadoAprobacion === 'aprobado' ? '#28a745' : 
                               estadoAprobacion === 'rechazado' ? '#dc3545' : '#ffc107';
            
            return `
            <tr>
                <td><strong>${cot.numero_cotizacion}</strong></td>
                <td>${cot.cliente_nombre}</td>
                <td>${formatearFecha(cot.fecha_creacion)}</td>
                <td><strong>$${parseFloat(cot.total).toFixed(2)}</strong></td>
                <td>
                    <span style="display: inline-flex; align-items: center; padding: 5px 10px; background: ${colorEstado}20; color: ${colorEstado}; border-radius: 5px; font-weight: 600;">
                        ${iconoEstado} ${estadoAprobacion.charAt(0).toUpperCase() + estadoAprobacion.slice(1)}
                    </span>
                </td>
                <td>
                    <button class="btn btn-primary btn-sm" onclick="verCotizacion(${cot.id})">Ver</button>
                    <button class="btn btn-warning btn-sm" onclick="editarCotizacion(${cot.id})">Editar</button>
                    <button class="btn btn-success btn-sm" onclick="descargarPDF(${cot.id})">PDF</button>
                    <button class="btn btn-secondary btn-sm" onclick="enviarEmail(${cot.id})">Email</button>
                </td>
            </tr>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error al cargar cotizaciones:', error);
        showNotification('Error al cargar cotizaciones', 'error');
    }
}

async function cargarClientesSelect() {
    try {
        if (clientes.length === 0) {
            const response = await fetch('/api/clientes');
            clientes = await response.json();
        }
        
        const select = document.getElementById('cotizacion-cliente');
        select.innerHTML = '<option value="">Seleccione un cliente...</option>' +
            clientes.map(cliente => `
                <option value="${cliente.id}">${cliente.nombre} (${cliente.email})</option>
            `).join('');
            
    } catch (error) {
        console.error('Error al cargar clientes:', error);
    }
}

// Cargar productos
async function cargarProductos() {
    try {
        const response = await fetch('/api/productos');
        productos = await response.json();
        console.log('Productos cargados:', productos.length);
    } catch (error) {
        console.error('Error al cargar productos:', error);
        productos = [];
    }
}

// Items de cotización
function agregarItem() {
    itemCounter++;
    const container = document.getElementById('items-container');
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'item-row';
    itemDiv.id = `item-${itemCounter}`;
    
    // Generar opciones de productos
    let productosOptions = '<option value="">-- Seleccionar Producto --</option>';
    
    if (productos && productos.length > 0) {
        productos.forEach(producto => {
            productosOptions += `<option value="${producto.id}" data-codigo="${producto.codigo}" data-nombre="${producto.nombre}" data-descripcion="${producto.descripcion || ''}" data-precio="${producto.precio}">${producto.codigo} - ${producto.nombre} ($${formatearMoneda(producto.precio)})</option>`;
        });
    } else {
        productosOptions += '<option value="" disabled>No hay productos en el catálogo</option>';
    }
    
    itemDiv.innerHTML = `
        <h4>Concepto #${itemCounter}</h4>
        <button type="button" class="btn-remove-item" onclick="eliminarItem(${itemCounter})">×</button>
        <div class="item-grid">
            <div class="form-group" style="grid-column: span 2;">
                <label>Producto/Servicio del Catálogo</label>
                <div style="display: flex; gap: 10px;">
                    <select class="item-producto-select" onchange="seleccionarProducto(this, ${itemCounter})" style="flex: 1;">
                        ${productosOptions}
                    </select>
                    <button type="button" class="btn btn-success" onclick="abrirModalProductoRapido(${itemCounter})" style="white-space: nowrap;">Nuevo</button>
                </div>
            </div>
            <div class="form-group">
                <label>Concepto * <small>(editable)</small></label>
                <input type="text" class="item-concepto" required>
            </div>
            <div class="form-group">
                <label>Descripción <small>(editable)</small></label>
                <input type="text" class="item-descripcion">
            </div>
            <div class="form-group">
                <label>Cantidad *</label>
                <input type="number" class="item-cantidad" min="1" value="1" required onchange="calcularTotales()">
            </div>
            <div class="form-group">
                <label>Precio Unitario *</label>
                <input type="number" class="item-precio" min="0" step="0.01" required onchange="calcularTotales()">
            </div>
        </div>
    `;
    
    container.appendChild(itemDiv);
}

// Seleccionar producto del catálogo
function seleccionarProducto(select, itemId) {
    const selectedOption = select.options[select.selectedIndex];
    
    if (selectedOption.value) {
        const itemDiv = document.getElementById(`item-${itemId}`);
        const codigo = selectedOption.getAttribute('data-codigo');
        const nombre = selectedOption.getAttribute('data-nombre');
        const descripcion = selectedOption.getAttribute('data-descripcion');
        const precio = parseFloat(selectedOption.getAttribute('data-precio'));
        
        // Llenar campos automáticamente
        itemDiv.querySelector('.item-concepto').value = `${codigo} - ${nombre}`;
        itemDiv.querySelector('.item-descripcion').value = descripcion;
        itemDiv.querySelector('.item-precio').value = precio.toFixed(2);
        
        // Recalcular totales
        calcularTotales();
    }
}

function eliminarItem(itemId) {
    const item = document.getElementById(`item-${itemId}`);
    if (item) {
        item.remove();
        calcularTotales();
    }
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
    
    const clienteId = document.getElementById('cotizacion-cliente').value;
    
    if (!clienteId) {
        showNotification('Debe seleccionar un cliente', 'error');
        return;
    }
    
    // Recopilar items
    const itemsElements = document.querySelectorAll('.item-row');
    const items = [];
    
    itemsElements.forEach(itemEl => {
        const concepto = itemEl.querySelector('.item-concepto').value;
        const descripcion = itemEl.querySelector('.item-descripcion').value;
        const cantidad = parseInt(itemEl.querySelector('.item-cantidad').value);
        const precio_unitario = parseFloat(itemEl.querySelector('.item-precio').value);
        
        // Validar que tenga concepto y cantidad (precio puede ser 0)
        if (concepto && cantidad && precio_unitario >= 0) {
            items.push({
                concepto,
                descripcion,
                cantidad,
                precio_unitario
            });
        }
    });
    
    if (items.length === 0) {
        showNotification('Debe agregar al menos un concepto', 'error');
        return;
    }
    
    const cotizacionData = {
        cliente_id: parseInt(clienteId),
        items: items,
        fecha_validez: document.getElementById('cotizacion-validez').value || null,
        notas: document.getElementById('cotizacion-notas').value || '',
        condiciones_comerciales: document.getElementById('cotizacion-condiciones')?.value || '',
        iva_porcentaje: 16
    };
    
    try {
        let response, url, method;
        
        // Si estamos editando, usar PUT, sino POST
        if (cotizacionEditando) {
            url = `/api/cotizaciones/${cotizacionEditando}`;
            method = 'PUT';
        } else {
            url = '/api/cotizaciones';
            method = 'POST';
        }
        
        response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cotizacionData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            const mensaje = cotizacionEditando 
                ? `Cotización actualizada exitosamente`
                : `Cotización ${result.numero_cotizacion} creada exitosamente`;
            showNotification(mensaje, 'success');
            limpiarFormularioCotizacion();
            showTab('cotizaciones');
            cargarCotizaciones();
        } else {
            showNotification(result.message, 'error');
        }
        
    } catch (error) {
        console.error('Error al procesar cotización:', error);
        showNotification('Error al procesar cotización', 'error');
    }
}

// Variable para saber si estamos editando
let cotizacionEditando = null;

function limpiarFormularioCotizacion() {
    document.getElementById('cotizacion-form').reset();
    document.getElementById('items-container').innerHTML = '';
    itemCounter = 0;
    cotizacionEditando = null;
    agregarItem();
    calcularTotales();
    
    // Cambiar texto del botón
    const btnSubmit = document.querySelector('#cotizacion-form button[type="submit"]');
    btnSubmit.innerHTML = '💾 Crear Cotización';
}

// Editar cotización existente
async function editarCotizacion(cotizacionId) {
    try {
        // Redirigir a la página de nueva cotización con el ID para editar
        window.location.href = `/nueva-cotizacion?editar=${cotizacionId}`;
    } catch (error) {
        console.error('Error al editar cotización:', error);
        showNotification('Error al cargar cotización: ' + error.message, 'error');
    }
}

// FUNCIÓN ANTERIOR PARA REFERENCIA (YA NO SE USA)
async function editarCotizacionViejo(cotizacionId) {
    try {
        const response = await fetch(`/api/cotizaciones/${cotizacionId}`);
        const cotizacion = await response.json();
        
        // Cambiar a la pestaña de nueva cotización
        showTab('nueva-cotizacion');
        
        // Esperar un momento para que el tab se renderice
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Guardar ID de cotización en edición
        cotizacionEditando = cotizacionId;
        
        // Cargar datos en el formulario
        document.getElementById('cotizacion-cliente').value = cotizacion.cliente_id;
        document.getElementById('cotizacion-validez').value = cotizacion.fecha_validez || '';
        document.getElementById('cotizacion-notas').value = cotizacion.notas || '';
        
        const condicionesField = document.getElementById('cotizacion-condiciones');
        if (condicionesField) {
            condicionesField.value = cotizacion.condiciones_comerciales || '';
        }
        
        // Limpiar items actuales
        const container = document.getElementById('items-container');
        container.innerHTML = '';
        itemCounter = 0;
        
        // Asegurar que los productos estén cargados
        if (!productos || productos.length === 0) {
            await cargarProductos();
        }
        
        // Cargar items de la cotización
        for (const item of cotizacion.items) {
            agregarItem();
            
            // Esperar que el item se agregue al DOM
            await new Promise(resolve => setTimeout(resolve, 50));
            
            const itemDiv = document.getElementById(`item-${itemCounter}`);
            if (itemDiv) {
                const conceptoInput = itemDiv.querySelector('.item-concepto');
                const descripcionInput = itemDiv.querySelector('.item-descripcion');
                const cantidadInput = itemDiv.querySelector('.item-cantidad');
                const precioInput = itemDiv.querySelector('.item-precio');
                
                if (conceptoInput) conceptoInput.value = item.concepto;
                if (descripcionInput) descripcionInput.value = item.descripcion || '';
                if (cantidadInput) cantidadInput.value = item.cantidad;
                if (precioInput) precioInput.value = item.precio_unitario;
            }
        }
        
        calcularTotales();
        
        // Cambiar texto del botón
        const btnSubmit = document.querySelector('#cotizacion-form button[type="submit"]');
        if (btnSubmit) {
            btnSubmit.innerHTML = '💾 Actualizar Cotización';
        }
        
        showNotification('Cotización cargada para edición', 'info');
        
    } catch (error) {
        console.error('Error al cargar cotización:', error);
        showNotification('Error al cargar cotización: ' + error.message, 'error');
    }
}

// Ver detalle de cotización
async function verCotizacion(cotizacionId) {
    try {
        const response = await fetch(`/api/cotizaciones/${cotizacionId}`);
        const cotizacion = await response.json();
        
        const itemsHTML = cotizacion.items.map(item => `
            <tr>
                <td>${item.concepto}</td>
                <td>${item.descripcion}</td>
                <td class="text-center">${item.cantidad}</td>
                <td class="text-center">$${item.precio_unitario.toFixed(2)}</td>
                <td class="text-center"><strong>$${item.subtotal.toFixed(2)}</strong></td>
            </tr>
        `).join('');

        const adjuntosHTML = (cotizacion.adjuntos && cotizacion.adjuntos.length) ? `
            <div class="form-section">
                <h3>Adjuntos</h3>
                <ul>
                    ${cotizacion.adjuntos.map(a => `<li>${a.nombre_original}</li>`).join('')}
                </ul>
            </div>
        ` : '';
        
        const modalBody = document.getElementById('modal-body');
        modalBody.innerHTML = `
            <h2>Cotización ${cotizacion.numero_cotizacion}</h2>
            
            <div class="form-section">
                <h3>Información del Cliente</h3>
                <p><strong>Nombre:</strong> ${cotizacion.nombre}</p>
                <p><strong>Email:</strong> ${cotizacion.email}</p>
                <p><strong>Teléfono:</strong> ${cotizacion.telefono || 'N/A'}</p>
                <p><strong>Dirección:</strong> ${cotizacion.direccion || 'N/A'}</p>
            </div>
            
            <div class="form-section">
                <h3>Conceptos</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Concepto</th>
                            <th>Descripción</th>
                            <th>Cantidad</th>
                            <th>Precio Unit.</th>
                            <th>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>${itemsHTML}</tbody>
                </table>
            </div>
            
            <div class="totales-box">
                <div class="total-row">
                    <span>Subtotal:</span>
                    <span>$${cotizacion.subtotal.toFixed(2)}</span>
                </div>
                <div class="total-row">
                    <span>IVA (16%):</span>
                    <span>$${cotizacion.iva.toFixed(2)}</span>
                </div>
                <div class="total-row total-final">
                    <span>TOTAL:</span>
                    <span>$${cotizacion.total.toFixed(2)}</span>
                </div>
            </div>
            
            ${cotizacion.notas ? `
                <div class="form-section">
                    <h3>Notas</h3>
                    <p>${cotizacion.notas}</p>
                </div>
            ` : ''}

            ${adjuntosHTML}
            
            <div class="form-actions">
                <button class="btn btn-success" onclick="descargarPDF(${cotizacionId})">Descargar PDF</button>
                <button class="btn btn-primary" onclick="enviarEmail(${cotizacionId})">Enviar por Email</button>
                <button class="btn btn-secondary" onclick="cerrarModal()">Cerrar</button>
            </div>
        `;
        
        document.getElementById('modal-cotizacion').style.display = 'block';
        
    } catch (error) {
        console.error('Error al cargar cotización:', error);
        showNotification('Error al cargar cotización', 'error');
    }
}

function cerrarModal() {
    document.getElementById('modal-cotizacion').style.display = 'none';
}

// Descargar PDF
async function descargarPDF(cotizacionId) {
    try {
        showNotification('Generando PDF...', 'info');
        
        // Obtener datos de la cotización para el nombre del archivo
        const cotizacionResponse = await fetch(`/api/cotizaciones/${cotizacionId}`);
        const cotizacion = await cotizacionResponse.json();
        
        const response = await fetch(`/api/cotizaciones/${cotizacionId}/pdf`);
        
        if (!response.ok) {
            throw new Error('Error al generar PDF');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${cotizacion.numero_cotizacion}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('PDF descargado exitosamente', 'success');
        
    } catch (error) {
        console.error('Error al descargar PDF:', error);
        showNotification('Error al generar el PDF', 'error');
    }
}

// Enviar Email
async function enviarEmail(cotizacionId) {
    // Crear modal personalizado para múltiples emails
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 10000;';
    
    modal.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; width: 90%;">
            <h3 style="margin-top: 0;">Enviar Cotización por Email</h3>
            <p style="color: #666; font-size: 14px; margin-bottom: 15px;">Ingrese los emails separados por comas (,) o punto y coma (;)</p>
            <textarea id="emails-input" placeholder="ejemplo@correo.com, otro@correo.com" 
                style="width: 100%; height: 120px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: inherit; resize: vertical;"></textarea>
            <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                <button onclick="this.closest('div').parentElement.parentElement.remove()" 
                    style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">Cancelar</button>
                <button id="enviar-emails-btn" 
                    style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">Enviar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    document.getElementById('emails-input').focus();
    
    document.getElementById('enviar-emails-btn').onclick = async () => {
        const emailsText = document.getElementById('emails-input').value.trim();
        
        if (!emailsText) {
            showNotification('Debe ingresar al menos un email', 'error');
            return;
        }
        
        // Separar y limpiar emails (acepta comas o punto y coma)
        const emails = emailsText.split(/[,;]/)
            .map(e => e.trim())
            .filter(e => e && e.includes('@') && e.includes('.'));
        
        if (emails.length === 0) {
            showNotification('Debe ingresar al menos un email válido', 'error');
            return;
        }
        
        // Validar formato básico de emails
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const emailsInvalidos = emails.filter(e => !emailRegex.test(e));
        
        if (emailsInvalidos.length > 0) {
            showNotification(`Emails inválidos: ${emailsInvalidos.join(', ')}`, 'error');
            return;
        }
        
        modal.remove();
        
        try {
            showNotification(`Enviando a ${emails.length} destinatario(s)...`, 'info');
            
            const response = await fetch(`/api/cotizaciones/${cotizacionId}/email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emails })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showNotification(result.message, 'success');
            } else {
                showNotification(result.message, 'error');
            }
            
        } catch (error) {
            console.error('Error al enviar email:', error);
            showNotification('Error al enviar el correo', 'error');
        }
    };
}

// Utilidades
function formatearFecha(fecha) {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.style.display = 'block';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 4000);
}

// Formatear moneda
function formatearMoneda(precio) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 2
    }).format(precio);
}

// Variable para guardar el item actual
let itemActualProducto = null;

// Abrir modal de producto rápido
function abrirModalProductoRapido(itemId) {
    itemActualProducto = itemId;
    document.getElementById('modal-producto-rapido').style.display = 'block';
    document.getElementById('form-producto-rapido').reset();
    setTimeout(() => document.getElementById('prod-codigo').focus(), 100);
}

// Cerrar modal de producto rápido
function cerrarModalProductoRapido() {
    document.getElementById('modal-producto-rapido').style.display = 'none';
    document.getElementById('form-producto-rapido').reset();
    itemActualProducto = null;
}

// Crear producto rápido desde cotización
async function crearProductoRapido(e) {
    e.preventDefault();
    
    const producto = {
        codigo: document.getElementById('prod-codigo').value.trim(),
        nombre: document.getElementById('prod-nombre').value.trim(),
        descripcion: document.getElementById('prod-descripcion').value.trim(),
        categoria: document.getElementById('prod-categoria').value.trim() || 'General',
        precio: parseFloat(document.getElementById('prod-precio').value),
        tipo: 'producto',
        unidad: 'pza',
        activo: 1
    };
    
    try {
        const response = await fetch('/api/productos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(producto)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Producto creado exitosamente', 'success');
            
            // Recargar lista de productos
            await cargarProductos();
            
            // Actualizar el selector del item y seleccionar el nuevo producto
            if (itemActualProducto) {
                const itemDiv = document.getElementById(`item-${itemActualProducto}`);
                if (itemDiv) {
                    const select = itemDiv.querySelector('.item-producto-select');
                    
                    // Regenerar opciones
                    let options = '<option value="">-- Seleccionar Producto --</option>';
                    productos.forEach(p => {
                        options += `<option value="${p.id}" data-codigo="${p.codigo}" data-nombre="${p.nombre}" data-descripcion="${p.descripcion || ''}" data-precio="${p.precio}">${p.codigo} - ${p.nombre} ($${formatearMoneda(p.precio)})</option>`;
                    });
                    select.innerHTML = options;
                    
                    // Seleccionar el nuevo producto
                    select.value = data.id;
                    
                    // Llenar campos automáticamente
                    itemDiv.querySelector('.item-concepto').value = `${producto.codigo} - ${producto.nombre}`;
                    itemDiv.querySelector('.item-descripcion').value = producto.descripcion;
                    itemDiv.querySelector('.item-precio').value = producto.precio.toFixed(2);
                    
                    calcularTotales();
                }
            }
            
            cerrarModalProductoRapido();
        } else {
            showNotification('❌ Error: ' + (data.message || 'No se pudo crear el producto'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('❌ Error de conexión', 'error');
    }
}

// DESHABILITADO: No cerrar modal al hacer clic fuera para evitar pérdida de datos
// window.onclick = function(event) {
//     const modal = document.getElementById('modal-cotizacion');
//     
//     if (event.target === modal) {
//         cerrarModal();
//     }
// }

// ============================================
// FUNCIONES RESPONSIVE Y SIDEBAR MOBILE
// ============================================

// Toggle sidebar para móviles
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.toggle('active');
        
        // Crear overlay si no existe
        if (!overlay) {
            const newOverlay = document.createElement('div');
            newOverlay.id = 'sidebar-overlay';
            newOverlay.className = 'sidebar-overlay';
            newOverlay.onclick = closeSidebar;
            document.body.appendChild(newOverlay);
            
            // Pequeño delay para la animación
            setTimeout(() => newOverlay.classList.add('active'), 10);
        } else {
            overlay.classList.toggle('active');
        }
        
        // Prevenir scroll del body cuando sidebar está abierto
        if (sidebar.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}

// Cerrar sidebar (para uso programático o overlay)
function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (sidebar) {
        sidebar.classList.remove('active');
    }
    
    if (overlay) {
        overlay.classList.remove('active');
        setTimeout(() => overlay.remove(), 300); // Remover después de la animación
    }
    
    document.body.style.overflow = '';
}

// Cerrar sidebar al hacer clic en un link de navegación (móvil)
document.addEventListener('DOMContentLoaded', () => {
    // Agregar listeners a los nav items si estamos en móvil
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Solo cerrar en pantallas móviles
            if (window.innerWidth <= 768) {
                setTimeout(closeSidebar, 100);
            }
        });
    });
    
    // Cerrar sidebar al redimensionar a desktop
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            closeSidebar();
        }
    });
});

// Touch gestures para cerrar sidebar con swipe
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
}, { passive: true });

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, { passive: true });

function handleSwipe() {
    const sidebar = document.getElementById('sidebar');
    
    if (!sidebar || !sidebar.classList.contains('active')) return;
    
    const swipeDistance = touchEndX - touchStartX;
    
    // Swipe left para cerrar (más de 100px)
    if (swipeDistance < -100 && touchStartX < 280) {
        closeSidebar();
    }
}
