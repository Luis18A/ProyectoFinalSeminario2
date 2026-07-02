/**
 * Gestión de Usuarios - Funciones de Interfaz
 * Maneja la lógica de edición y creación de usuarios a través de modales.
 */

// Lógica para abrir el modal en modo creación
function abrirModalCrearUsuario() {
    const formUsuario = document.getElementById('form-usuario');
    const inputPassword = document.getElementById('input-password');
    const passwordHelp = document.getElementById('password-help');
    const btnSubmitText = document.getElementById('btn-submit-text');

    if (formUsuario) {
        formUsuario.reset();
        formUsuario.action = '/usuarios';
    }
    if (inputPassword) {
        inputPassword.required = true;
    }
    if (passwordHelp) {
        passwordHelp.classList.add('hidden');
    }
    if (btnSubmitText) {
        btnSubmitText.textContent = 'Crear Usuario';
    }

    const titleText = document.getElementById('modal-title-text');
    const titleIcon = document.getElementById('modal-title-icon');
    if (titleText) titleText.textContent = 'Registrar Nuevo Usuario';
    if (titleIcon) titleIcon.textContent = 'person_add';

    const modal = document.getElementById('modal-usuario');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

// Lógica para cerrar el modal
function cerrarModalUsuario() {
    const modal = document.getElementById('modal-usuario');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';
}

/**
 * Prepara el formulario para editar un usuario existente en el modal.
 * 
 * @param {HTMLElement} btn - El botón que disparó la acción.
 */
function abrirModalEditar(btn) {
    const id = btn.getAttribute('data-id');
    const username = btn.getAttribute('data-username');
    const nombre = btn.getAttribute('data-nombre');
    const apellido = btn.getAttribute('data-apellido');
    const rol = btn.getAttribute('data-rol');
    const activo = btn.getAttribute('data-activo') === 'True';

    const inputUsername = document.getElementById('input-username');
    const inputNombre = document.getElementById('input-nombre');
    const inputApellido = document.getElementById('input-apellido');
    const selectRol = document.getElementById('select-rol');
    const checkActivo = document.getElementById('check-activo');
    const inputPassword = document.getElementById('input-password');
    const passwordHelp = document.getElementById('password-help');
    const formUsuario = document.getElementById('form-usuario');
    const btnSubmitText = document.getElementById('btn-submit-text');

    if (inputUsername) inputUsername.value = username;
    if (inputNombre) inputNombre.value = nombre;
    if (inputApellido) inputApellido.value = apellido;
    if (selectRol) selectRol.value = rol;
    if (checkActivo) checkActivo.checked = activo;
    
    if (inputPassword) {
        inputPassword.required = false; 
    }
    if (passwordHelp) {
        passwordHelp.classList.remove('hidden');
    }
    if (formUsuario) {
        formUsuario.action = `/usuarios/actualizar/${id}`;
    }
    if (btnSubmitText) {
        btnSubmitText.textContent = 'Guardar Cambios';
    }

    const titleText = document.getElementById('modal-title-text');
    const titleIcon = document.getElementById('modal-title-icon');
    if (titleText) titleText.textContent = 'Editar Usuario';
    if (titleIcon) titleIcon.textContent = 'edit';

    const modal = document.getElementById('modal-usuario');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Cerrar modal al hacer clic en el backdrop
    const modalUsuario = document.getElementById('modal-usuario');
    if (modalUsuario) {
        modalUsuario.addEventListener('click', function (e) {
            if (e.target === this) cerrarModalUsuario();
        });
    }
});
