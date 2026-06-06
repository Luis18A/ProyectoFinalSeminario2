/**
 * Gestión de Usuarios - Funciones de Interfaz
 * Maneja la lógica de edición y estados del formulario de usuarios.
 */

/**
 * Prepara el formulario para editar un usuario existente.
 * Extrae los datos del botón presionado y actualiza la acción del formulario.
 * 
 * @param {HTMLElement} btn - El botón que disparó la acción, contiene data-attributes con la info del usuario.
 */
function abrirModalEditar(btn) {
    // 1. Extraer datos del botón utilizando el dataset
    // El botón debe tener atributos como data-id, data-username, etc.
    const id = btn.getAttribute('data-id');
    const username = btn.getAttribute('data-username');
    const nombre = btn.getAttribute('data-nombre');
    const apellido = btn.getAttribute('data-apellido');
    const rol = btn.getAttribute('data-rol');
    const activo = btn.getAttribute('data-activo') === 'True';

    // 2. Llenar los campos del formulario principal
    const inputUsername = document.getElementById('input-username');
    const inputNombre = document.getElementById('input-nombre');
    const inputApellido = document.getElementById('input-apellido');
    const selectRol = document.getElementById('select-rol');
    const checkActivo = document.getElementById('check-activo');
    const inputPassword = document.getElementById('input-password');
    const passwordHelp = document.getElementById('password-help');
    const formUsuario = document.getElementById('form-usuario');
    const btnSubmit = document.getElementById('btn-submit');
    const btnCancelar = document.getElementById('btn-cancelar');

    if (inputUsername) inputUsername.value = username;
    if (inputNombre) inputNombre.value = nombre;
    if (inputApellido) inputApellido.value = apellido;
    if (selectRol) selectRol.value = rol;
    if (checkActivo) checkActivo.checked = activo;
    
    // 3. Ajustes específicos para el modo edición
    if (inputPassword) {
        // Al editar, la contraseña no es obligatoria (se asume que si se deja vacía no cambia)
        inputPassword.required = false; 
    }
    if (passwordHelp) {
        passwordHelp.classList.remove('hidden');
    }
    if (formUsuario) {
        // Cambiar la ruta del form para apuntar al endpoint de actualización
        formUsuario.action = `/usuarios/actualizar/${id}`;
    }
    if (btnSubmit) {
        btnSubmit.innerText = 'GUARDAR CAMBIOS';
    }
    if (btnCancelar) {
        btnCancelar.classList.remove('hidden');
    }

    // 4. Desplazamiento suave hacia el formulario para facilitar la experiencia al usuario
    if (formUsuario) {
        formUsuario.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Resetea el formulario de usuarios a su estado inicial (modo creación).
 * Limpia los campos y restaura las etiquetas y acciones originales.
 */
function cancelarEdicion() {
    const formUsuario = document.getElementById('form-usuario');
    const inputPassword = document.getElementById('input-password');
    const passwordHelp = document.getElementById('password-help');
    const btnSubmit = document.getElementById('btn-submit');
    const btnCancelar = document.getElementById('btn-cancelar');

    // 1. Resetear todos los valores del formulario
    if (formUsuario) {
        formUsuario.reset();
        // Restaurar la ruta original de creación
        formUsuario.action = '/usuarios';
    }
    
    // 2. Revertir cambios visuales y requerimientos de campos
    if (inputPassword) {
        inputPassword.required = true;
    }
    if (passwordHelp) {
        passwordHelp.classList.add('hidden');
    }
    if (btnSubmit) {
        btnSubmit.innerText = 'CREAR USUARIO';
    }
    if (btnCancelar) {
        btnCancelar.classList.add('hidden');
    }
}
