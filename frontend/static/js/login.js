/**
 * Lógica para la página de Inicio de Sesión.
 * Maneja interacciones de la interfaz de usuario en el login.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const passwordInput = document.getElementById('passcode');
    const toggleButton = document.querySelector('button[aria-label="Toggle password visibility"]');
    const toggleIcon = toggleButton?.querySelector('.material-symbols-outlined');

    /**
     * Alterna la visibilidad de la contraseña.
     * Cambia el tipo de input entre 'password' y 'text' y actualiza el icono.
     */
    if (toggleButton && passwordInput) {
        toggleButton.addEventListener('click', () => {
            const isPassword = passwordInput.type === 'password';
            
            // Cambiar tipo de input
            passwordInput.type = isPassword ? 'text' : 'password';
            
            // Actualizar icono de Material Symbols
            if (toggleIcon) {
                toggleIcon.textContent = isPassword ? 'visibility' : 'visibility_off';
            }
            
            // Feedback visual en el botón
            toggleButton.classList.toggle('text-secondary', isPassword);
        });
    }
});
