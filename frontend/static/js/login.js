/**
 * Lógica para la página de Inicio de Sesión.
 * Maneja interacciones de la interfaz de usuario en el login.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const passwordInput = document.getElementById('password');
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

    // Lógica para el botón de ayuda/credenciales
    const helpBtn = document.getElementById('help-btn');
    const closeHelpBtn = document.getElementById('close-help-btn');
    const credentialsBox = document.getElementById('demo-credentials-box');
    const usernameInput = document.getElementById('username');

    if (helpBtn && credentialsBox) {
        helpBtn.addEventListener('click', () => {
            credentialsBox.classList.toggle('hidden');
        });
    }

    if (closeHelpBtn && credentialsBox) {
        closeHelpBtn.addEventListener('click', () => {
            credentialsBox.classList.add('hidden');
        });
    }

    window.fillCredentials = (user, pass) => {
        if (usernameInput && passwordInput) {
            usernameInput.value = user;
            passwordInput.value = pass;
            passwordInput.type = 'password';
            if (toggleIcon) {
                toggleIcon.textContent = 'visibility_off';
            }
            toggleButton.classList.remove('text-secondary');

            // Feedback visual breve
            usernameInput.classList.add('bg-blue-50/50');
            passwordInput.classList.add('bg-blue-50/50');
            setTimeout(() => {
                usernameInput.classList.remove('bg-blue-50/50');
                passwordInput.classList.remove('bg-blue-50/50');
            }, 500);
        }
    };

    // Lógica para el panel explicativo de la plataforma
    const aboutBtn = document.getElementById('about-btn');
    const closeAboutBtn = document.getElementById('close-about-btn');
    const aboutBox = document.getElementById('about-box');

    if (aboutBtn && aboutBox) {
        aboutBtn.addEventListener('click', () => {
            aboutBox.classList.toggle('hidden');
        });
    }

    if (closeAboutBtn && aboutBox) {
        closeAboutBtn.addEventListener('click', () => {
            aboutBox.classList.add('hidden');
        });
    }
});
