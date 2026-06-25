/**
 * Core Application Logic - TechFlow Service Hub
 * Maneja funcionalidades compartidas, responsividad (Sidebar/Menú) y Búsqueda Global.
 */

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const mainContent = document.getElementById('main-content');
    const overlay = document.getElementById('sidebar-overlay');
    
    // Auto-hide alert toasts
    const toasts = document.querySelectorAll('.toast-alert');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.classList.add('opacity-0', 'translate-x-10');
            toast.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            setTimeout(() => {
                toast.remove();
            }, 500);
        }, 4000);
    });

    // Toggle notifications dropdown
    const notifBtn = document.getElementById('notification-btn');
    const notifDropdown = document.getElementById('notification-dropdown');
    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', (e) => {
            if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
                notifDropdown.classList.add('hidden');
            }
        });
    }
    
    // Función para manejar la visibilidad del sidebar de forma responsiva y animada
    function toggleSidebar(open) {
        if (window.innerWidth > 1024) {
            // En escritorio: Colapsar/Expandir
            if (open === undefined) {
                document.body.classList.toggle('sidebar-collapsed');
            } else {
                document.body.classList.toggle('sidebar-collapsed', !open);
            }
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        } else {
            // En móvil/tablet: Abrir/Cerrar Overlay
            const isCurrentlyOpen = document.body.classList.contains('sidebar-open');
            const shouldOpen = open === undefined ? !isCurrentlyOpen : open;
            
            if (shouldOpen) {
                document.body.classList.add('sidebar-open');
                if (overlay) {
                    overlay.classList.remove('hidden');
                    setTimeout(() => overlay.classList.add('opacity-100'), 10);
                }
            } else {
                document.body.classList.remove('sidebar-open');
                if (overlay) {
                    overlay.classList.remove('opacity-100');
                    setTimeout(() => overlay.classList.add('hidden'), 300);
                }
            }
        }
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleSidebar();
        });
    }

    // Cerrar el menú móvil al hacer clic en el contenido principal o en el overlay
    if (mainContent) {
        mainContent.addEventListener('click', () => {
            if (window.innerWidth <= 1024) {
                toggleSidebar(false);
            }
        });
    }
    if (overlay) {
        overlay.addEventListener('click', () => {
            toggleSidebar(false);
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
            if (overlay) {
                overlay.classList.remove('opacity-100');
                overlay.classList.add('hidden');
            }
        } else {
            // Sincronizar overlay en móvil si por algún motivo la clase sidebar-open quedó activa
            if (document.body.classList.contains('sidebar-open') && overlay) {
                overlay.classList.remove('hidden');
                overlay.classList.add('opacity-100');
            }
        }
    });

    // ─── LÓGICA DE BÚSQUEDA GLOBAL ──────────────────────────────────────────
    const globalSearchInput = document.getElementById('global-search-input');
    const globalSearchResults = document.getElementById('global-search-results');
    const globalSearchResultsContent = document.getElementById('global-search-results-content');
    let searchTimeoutId;

    if (globalSearchInput && globalSearchResults && globalSearchResultsContent) {
        globalSearchInput.addEventListener('input', function() {
            clearTimeout(searchTimeoutId);
            const query = this.value.trim();

            if (query.length < 2) {
                globalSearchResults.classList.add('hidden');
                globalSearchResultsContent.innerHTML = '';
                return;
            }

            searchTimeoutId = setTimeout(() => {
                fetch(`/api/global-search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        renderGlobalResults(data, query);
                    })
                    .catch(err => {
                        console.error('Error fetching global search results:', err);
                    });
            }, 300);
        });

        // Cerrar dropdown al hacer click fuera o presionar escape
        document.addEventListener('click', (e) => {
            if (!globalSearchInput.contains(e.target) && !globalSearchResults.contains(e.target)) {
                globalSearchResults.classList.add('hidden');
            }
        });

        globalSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                globalSearchResults.classList.add('hidden');
            }
        });
    }

    function renderGlobalResults(data, query) {
        globalSearchResultsContent.innerHTML = '';
        const hasResults = (data.clientes && data.clientes.length > 0) ||
                           (data.equipos && data.equipos.length > 0) ||
                           (data.ordenes && data.ordenes.length > 0);

        if (!hasResults) {
            globalSearchResultsContent.innerHTML = `
                <div class="p-4 text-center text-xs text-zinc-500">
                    No se encontraron resultados para "${query}"
                </div>
            `;
            globalSearchResults.classList.remove('hidden');
            return;
        }

        let html = '';

        // 1. Órdenes / Tickets
        if (data.ordenes && data.ordenes.length > 0) {
            html += `
                <div class="bg-zinc-50/50 p-2 text-[9px] font-bold text-zinc-400 uppercase tracking-widest border-t border-zinc-100">Tickets de Servicio</div>
                <div class="py-1">
            `;
            data.ordenes.forEach(o => {
                html += `
                    <a href="${o.url}" class="block px-4 py-2 hover:bg-zinc-50 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="font-bold text-xs text-primary">${o.codigo}</span>
                            <span class="text-[9px] bg-zinc-100 text-zinc-600 px-1.5 py-0.5 font-bold uppercase tracking-wider">${o.estado}</span>
                        </div>
                        <div class="text-xs text-zinc-600 truncate mt-0.5">${o.falla}</div>
                    </a>
                `;
            });
            html += `</div>`;
        }

        // 2. Clientes
        if (data.clientes && data.clientes.length > 0) {
            html += `
                <div class="bg-zinc-50/50 p-2 text-[9px] font-bold text-zinc-400 uppercase tracking-widest border-t border-zinc-100">Clientes</div>
                <div class="py-1">
            `;
            data.clientes.forEach(c => {
                html += `
                    <a href="${c.url}" class="block px-4 py-2 hover:bg-zinc-50 transition-colors">
                        <div class="font-bold text-xs text-zinc-800">${c.nombre}</div>
                        <div class="text-[9px] text-zinc-400 font-mono">DNI/CUIL: ${c.dni_cuil}</div>
                    </a>
                `;
            });
            html += `</div>`;
        }

        // 3. Equipos
        if (data.equipos && data.equipos.length > 0) {
            html += `
                <div class="bg-zinc-50/50 p-2 text-[9px] font-bold text-zinc-400 uppercase tracking-widest border-t border-zinc-100">Equipos</div>
                <div class="py-1">
            `;
            data.equipos.forEach(e => {
                html += `
                    <a href="${e.url}" class="block px-4 py-2 hover:bg-zinc-50 transition-colors">
                        <div class="font-bold text-xs text-zinc-800 truncate">${e.label}</div>
                        <div class="text-[9px] text-zinc-400">Cliente: ${e.cliente_nombre}</div>
                    </a>
                `;
            });
            html += `</div>`;
        }

        globalSearchResultsContent.innerHTML = html;
        globalSearchResults.classList.remove('hidden');
    }

    console.log('TechFlow Responsive Terminal initialized with Global Search.');
});

// Mark a single notification as read and redirect
window.handleNotificationClick = async function(id, redirectUrl) {
    try {
        const resp = await fetch(`/notificaciones/${id}/leer`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            }
        });
        const data = await resp.json();
        if (data.success) {
            window.location.href = redirectUrl;
        } else {
            console.error('Error marking notification as read:', data.message);
            window.location.href = redirectUrl;
        }
    } catch (err) {
        console.error('Network error:', err);
        window.location.href = redirectUrl;
    }
};

// Mark all notifications as read
window.markAllNotificationsAsRead = async function() {
    try {
        const resp = await fetch('/notificaciones/leer-todas', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            }
        });
        const data = await resp.json();
        if (data.success) {
            window.location.reload();
        } else {
            window.showToast('Error al marcar notificaciones: ' + data.message, 'error');
        }
    } catch (err) {
        console.error('Network error:', err);
        window.showToast('Error de red al marcar notificaciones.', 'error');
    }
};

// Global JS helper to trigger toasts programmatically
window.showToast = function (message, category = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-alert pointer-events-auto flex items-center gap-3 p-4 bg-white border-l-4 shadow-lg transition-all duration-300 transform translate-x-10 opacity-0 ${category === 'success' ? 'border-emerald-500 text-emerald-800' : 'border-red-500 text-red-800'}`;
    toast.setAttribute('role', 'alert');

    toast.innerHTML = `
        <span class="material-symbols-outlined">
            ${category === 'success' ? 'check_circle' : 'error'}
        </span>
        <div class="flex-grow font-label-mono text-xs uppercase tracking-wider pr-2">
            ${message}
        </div>
        <button class="text-zinc-400 hover:text-zinc-900 transition-colors" onclick="this.parentElement.remove()">
            <span class="material-symbols-outlined text-sm">close</span>
        </button>
    `;

    container.appendChild(toast);

    // Trigger slide-in
    setTimeout(() => {
        toast.classList.remove('opacity-0', 'translate-x-10');
    }, 10);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-10');
        toast.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, 4000);
};

// Funciones globales compartidas para control de transiciones de estado de la orden
window.confirmarPresupuesto = async function(ordenId, costo) {
    if (!confirm(`¿Confirmar que el cliente acepta el presupuesto de $${costo} y empezar reparación?`)) {
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('estado', 'REPARACION');
        formData.append('observaciones', 'Aprobado por el cliente por comunicación telefónica.');
        
        const resp = await fetch(`/ordenServicio/${ordenId}/actualizar-estado-flujo`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            },
            body: formData
        });
        
        const data = await resp.json();
        if (data.success) {
            window.showToast('Presupuesto aprobado. El técnico ya puede comenzar con la reparación.', 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            window.showToast('Error: ' + data.message, 'error');
        }
    } catch (err) {
        console.error(err);
        window.showToast('Ocurrió un error al confirmar el presupuesto.', 'error');
    }
};

window.rechazarPresupuesto = async function(ordenId) {
    const motivo = prompt("Ingrese el motivo del rechazo del presupuesto (ej: Presupuesto muy elevado, el cliente retira el equipo):");
    if (motivo === null) {
        return;
    }
    
    const motivoLimpio = motivo.trim();
    if (!motivoLimpio) {
        window.showToast('Debe ingresar un motivo para poder rechazar el presupuesto.', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('estado', 'DIAGNOSTICO');
        formData.append('observaciones', `Rechazado por el cliente. Motivo: ${motivoLimpio}`);
        
        const resp = await fetch(`/ordenServicio/${ordenId}/actualizar-estado-flujo`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            },
            body: formData
        });
        
        const data = await resp.json();
        if (data.success) {
            window.showToast('Presupuesto rechazado. La orden volvió al estado de diagnóstico.', 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            window.showToast('Error: ' + data.message, 'error');
        }
    } catch (err) {
        console.error(err);
        window.showToast('Ocurrió un error al rechazar el presupuesto.', 'error');
    }
};

window.entregarEquipo = async function(ordenId) {
    if (!confirm('¿Registrar la entrega formal del equipo y cerrar el ciclo de la orden?')) {
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('estado', 'ENTREGADO');
        formData.append('observaciones', 'Equipo entregado formalmente al cliente. Ciclo de servicio finalizado.');
        
        const resp = await fetch(`/ordenServicio/${ordenId}/actualizar-estado-flujo`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            },
            body: formData
        });
        
        const data = await resp.json();
        if (data.success) {
            window.showToast('Equipo entregado y ciclo cerrado exitosamente.', 'success');
            setTimeout(() => window.location.reload(), 1500);
        } else {
            window.showToast('Error: ' + data.message, 'error');
        }
    } catch (err) {
        console.error(err);
        window.showToast('Ocurrió un error al registrar la entrega del equipo.', 'error');
    }
};
