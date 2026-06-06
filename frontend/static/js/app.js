/**
 * Core Application Logic - TechFlow Service Hub
 * Maneja funcionalidades compartidas y responsividad (Sidebar/Menú).
 */

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const mainContent = document.getElementById('main-content');
    
    // Función para manejar el toggle del sidebar
    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (window.innerWidth > 1024) {
                // En escritorio: Colapsar/Expandir
                document.body.classList.toggle('sidebar-collapsed');
                const isCollapsed = document.body.classList.contains('sidebar-collapsed');
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            } else {
                // En móvil: Abrir/Cerrar Overlay
                document.body.classList.toggle('sidebar-open');
            }
        });
    }

    // Cerrar el menú móvil al hacer clic en el contenido principal
    if (mainContent) {
        mainContent.addEventListener('click', () => {
            if (window.innerWidth <= 1024) {
                document.body.classList.remove('sidebar-open');
            }
        });
    }

    // Restaurar estado (solo en escritorio)
    if (window.innerWidth > 1024 && localStorage.getItem('sidebarCollapsed') === 'true') {
        document.body.classList.add('sidebar-collapsed');
    }

    // Ajustar al cambiar el tamaño de la ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 1024) {
            document.body.classList.remove('sidebar-open');
        }
    });

    console.log('TechFlow Responsive Terminal initialized.');
});
