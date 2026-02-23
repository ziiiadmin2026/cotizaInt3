// Variables globales
let usuarios = [];
let modoEdicion = false;
let usuarioActual = null;

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    verificarSesion();
});

// Verificar sesión y permisos
async function verificarSesion() {
    try {
        const response = await fetch('/api/session');
        const data = await response.json();
        
        if (!data.authenticated) {
            window.location.href = '/login';
            return;
        }
        
        usuarioActual = data.usuario;
        
        // Solo admin puede acceder
        if (usuarioActual.rol !== 'admin') {
            window.location.href = '/';
            return;
        }
        
        // Actualizar UI
        document.getElementById('nombreUsuario').textContent = usuarioActual.nombre_completo;
        
        // Cargar usuarios
        cargarUsuarios();
        
        // Event listeners
        document.getElementById('formUsuario').addEventListener('submit', guardarUsuario);
        document.getElementById('formPassword').addEventListener('submit', cambiarPassword);
        
        // Prevenir cierre con tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const modalUsuario = document.getElementById('modalUsuario');
                const modalPassword = document.getElementById('modalPassword');
                if ((modalUsuario && modalUsuario.classList.contains('show')) || 
                    (modalPassword && modalPassword.classList.contains('show'))) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        });
        
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

// Cargar lista de usuarios
async function cargarUsuarios() {
    try {
        const response = await fetch('/api/usuarios');
        usuarios = await response.json();
        
        const tbody = document.getElementById('tablaUsuarios');
        
        if (usuarios.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 40px;">
                        No hay usuarios registrados
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = usuarios.map(usuario => `
            <tr>
                <td><strong>${usuario.username}</strong></td>
                <td>${usuario.nombre_completo}</td>
                <td>${usuario.email}</td>
                <td>
                    <span class="badge badge-${usuario.rol}">
                        ${usuario.rol === 'admin' ? 'Administrador' : 'Usuario'}
                    </span>
                </td>
                <td>
                    <span class="badge badge-${usuario.activo ? 'activo' : 'inactivo'}">
                        ${usuario.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td>${usuario.ultimo_acceso ? formatearFecha(usuario.ultimo_acceso) : 'Nunca'}</td>
                <td>
                    <button class="btn-action btn-edit" onclick="editarUsuario(${usuario.id})">
                        Editar
                    </button>
                    <button class="btn-action btn-password" onclick="abrirModalPassword(${usuario.id})">
                        Contraseña
                    </button>
                    ${usuario.id !== usuarioActual.id ? `
                        <button class="btn-action btn-delete" onclick="eliminarUsuario(${usuario.id})">
                            Eliminar
                        </button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error al cargar usuarios:', error);
        mostrarAlerta('Error al cargar usuarios', 'danger');
    }
}

// Abrir modal para nuevo usuario
function abrirModalNuevoUsuario() {
    modoEdicion = false;
    document.getElementById('modalTitulo').textContent = 'Nuevo Usuario';
    document.getElementById('formUsuario').reset();
    document.getElementById('usuarioId').value = '';
    document.getElementById('username').disabled = false;
    document.getElementById('passwordGroup').style.display = 'block';
    document.getElementById('password').required = true;
    document.getElementById('activo').value = '1';
    document.getElementById('modalUsuario').classList.add('show');
}

// Editar usuario
async function editarUsuario(id) {
    try {
        const response = await fetch(`/api/usuarios/${id}`);
        const usuario = await response.json();
        
        modoEdicion = true;
        document.getElementById('modalTitulo').textContent = 'Editar Usuario';
        document.getElementById('usuarioId').value = usuario.id;
        document.getElementById('username').value = usuario.username;
        document.getElementById('username').disabled = true;
        document.getElementById('nombreCompleto').value = usuario.nombre_completo;
        document.getElementById('email').value = usuario.email;
        document.getElementById('rol').value = usuario.rol;
        document.getElementById('activo').value = usuario.activo;
        document.getElementById('passwordGroup').style.display = 'none';
        document.getElementById('password').required = false;
        document.getElementById('modalUsuario').classList.add('show');
        
    } catch (error) {
        console.error('Error al cargar usuario:', error);
        mostrarAlerta('Error al cargar usuario', 'danger');
    }
}

// Guardar usuario (crear o actualizar)
async function guardarUsuario(e) {
    e.preventDefault();
    
    const id = document.getElementById('usuarioId').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const nombreCompleto = document.getElementById('nombreCompleto').value;
    const email = document.getElementById('email').value;
    const rol = document.getElementById('rol').value;
    const activo = parseInt(document.getElementById('activo').value);
    
    try {
        if (modoEdicion) {
            // Actualizar usuario existente
            const response = await fetch(`/api/usuarios/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nombre_completo: nombreCompleto,
                    email: email,
                    rol: rol,
                    activo: activo
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                mostrarAlerta('Usuario actualizado exitosamente', 'success');
                cerrarModal();
                cargarUsuarios();
            } else {
                mostrarAlerta(data.message || 'Error al actualizar usuario', 'danger');
            }
            
        } else {
            // Crear nuevo usuario
            const response = await fetch('/api/usuarios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    nombre_completo: nombreCompleto,
                    email: email,
                    rol: rol
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                mostrarAlerta('Usuario creado exitosamente', 'success');
                cerrarModal();
                cargarUsuarios();
            } else {
                mostrarAlerta(data.message || 'Error al crear usuario', 'danger');
            }
        }
        
    } catch (error) {
        console.error('Error al guardar usuario:', error);
        mostrarAlerta('Error al guardar usuario', 'danger');
    }
}

// Eliminar usuario
async function eliminarUsuario(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/usuarios/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarAlerta('Usuario eliminado exitosamente', 'success');
            cargarUsuarios();
        } else {
            mostrarAlerta(data.message || 'Error al eliminar usuario', 'danger');
        }
        
    } catch (error) {
        console.error('Error al eliminar usuario:', error);
        mostrarAlerta('Error al eliminar usuario', 'danger');
    }
}

// Abrir modal de cambio de contraseña
function abrirModalPassword(id) {
    document.getElementById('passwordUsuarioId').value = id;
    document.getElementById('formPassword').reset();
    document.getElementById('modalPassword').classList.add('show');
}

// Cambiar contraseña
async function cambiarPassword(e) {
    e.preventDefault();
    
    const id = document.getElementById('passwordUsuarioId').value;
    const nuevaPassword = document.getElementById('nuevaPassword').value;
    const confirmarPassword = document.getElementById('confirmarPassword').value;
    
    if (nuevaPassword !== confirmarPassword) {
        mostrarAlerta('Las contraseñas no coinciden', 'danger');
        return;
    }
    
    if (nuevaPassword.length < 6) {
        mostrarAlerta('La contraseña debe tener al menos 6 caracteres', 'danger');
        return;
    }
    
    try {
        const response = await fetch(`/api/usuarios/${id}/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nueva_password: nuevaPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarAlerta('Contraseña actualizada exitosamente', 'success');
            cerrarModalPassword();
        } else {
            mostrarAlerta(data.message || 'Error al actualizar contraseña', 'danger');
        }
        
    } catch (error) {
        console.error('Error al cambiar contraseña:', error);
        mostrarAlerta('Error al cambiar contraseña', 'danger');
    }
}

// Cerrar modales
function cerrarModal() {
    document.getElementById('modalUsuario').classList.remove('show');
}

function cerrarModalPassword() {
    document.getElementById('modalPassword').classList.remove('show');
}

// DESHABILITADO: No cerrar modales al hacer clic fuera para evitar pérdida de datos
// document.addEventListener('click', function(e) {
//     const modalUsuario = document.getElementById('modalUsuario');
//     const modalPassword = document.getElementById('modalPassword');
//     
//     if (e.target === modalUsuario) {
//         cerrarModal();
//     }
//     
//     if (e.target === modalPassword) {
//         cerrarModalPassword();
//     }
// });

// Mostrar alertas
function mostrarAlerta(mensaje, tipo = 'success') {
    const alert = document.getElementById('alert');
    alert.textContent = mensaje;
    alert.className = `alert alert-${tipo} show`;
    
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

// Formatear fecha
function formatearFecha(fecha) {
    const date = new Date(fecha);
    const opciones = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('es-MX', opciones);
}
