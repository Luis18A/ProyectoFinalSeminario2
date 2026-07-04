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

    // ─── LÓGICA DE CAJÓN DE AYUDA DE PÁGINA (HELP DRAWER) ─────────────────
    const helpBtn = document.getElementById('page-help-btn');
    const closeHelpBtn = document.getElementById('close-help-drawer');
    const helpOverlay = document.getElementById('help-drawer-overlay');
    const helpDrawer = document.getElementById('help-drawer');
    const helpContentDest = document.getElementById('help-drawer-content');
    const helpContentSrc = document.getElementById('page-help-source');

    if (helpBtn && helpDrawer && helpContentDest && helpContentSrc) {
        helpContentDest.innerHTML = helpContentSrc.innerHTML;

        const openHelpDrawer = () => {
            helpDrawer.classList.remove('translate-x-full');
            if (helpOverlay) {
                helpOverlay.classList.remove('hidden');
                setTimeout(() => helpOverlay.classList.add('opacity-100'), 10);
            }
        };

        const closeHelpDrawer = () => {
            helpDrawer.classList.add('translate-x-full');
            if (helpOverlay) {
                helpOverlay.classList.remove('opacity-100');
                setTimeout(() => helpOverlay.classList.add('hidden'), 300);
            }
        };

        helpBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openHelpDrawer();
        });

        if (closeHelpBtn) {
            closeHelpBtn.addEventListener('click', closeHelpDrawer);
        }

        if (helpOverlay) {
            helpOverlay.addEventListener('click', closeHelpDrawer);
        }
    }

    // ─── LÓGICA DE BUSCADOR GLOBAL ─────────────────────────────────────────
    const globalSearchInput = document.getElementById('global-search-input');
    const globalSearchResults = document.getElementById('global-search-results');
    const globalSearchClear = document.getElementById('global-search-clear');
    const mobileSearchToggle = document.getElementById('mobile-search-toggle');
    const mobileSearchBack = document.getElementById('mobile-search-back');
    const header = document.querySelector('header');

    if (globalSearchInput && globalSearchResults) {
        let debounceTimer;
        let activeIndex = -1;

        const performSearch = async (query) => {
            if (query.length < 2) {
                globalSearchResults.innerHTML = '';
                globalSearchResults.classList.add('hidden');
                globalSearchClear?.classList.add('hidden');
                activeIndex = -1;
                return;
            }

            globalSearchClear?.classList.remove('hidden');

            try {
                const response = await fetch(`/api/global-search?q=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Search request failed');
                
                const data = await response.json();
                renderSearchResults(data, query);
            } catch (err) {
                console.error('Error during global search:', err);
                globalSearchResults.innerHTML = `
                    <div class="p-4 text-center text-red-500 font-semibold text-xs">
                        Error al buscar. Por favor, reintente.
                    </div>
                `;
                globalSearchResults.classList.remove('hidden');
            }
        };

        const renderSearchResults = (data, query) => {
            globalSearchResults.innerHTML = '';
            let html = '';
            let hasResults = false;

            const renderEstadoBadge = (estado) => {
                const estadoClean = (estado || '').trim();
                let bgClass = 'bg-zinc-100 text-zinc-600 border-zinc-200';
                let icon = 'build';
                
                if (estadoClean === 'Pendiente') {
                    bgClass = 'bg-yellow-50 text-yellow-700 border-yellow-200';
                    icon = 'info';
                } else if (estadoClean === 'Diagnostico' || estadoClean === 'Diagnóstico') {
                    bgClass = 'bg-blue-50 text-blue-700 border-blue-200';
                    icon = 'build';
                } else if (estadoClean === 'Presupuestado') {
                    bgClass = 'bg-purple-50 text-purple-700 border-purple-200';
                    icon = 'build';
                } else if (estadoClean === 'Reparacion' || estadoClean === 'Reparación') {
                    bgClass = 'bg-orange-50 text-orange-700 border-orange-200';
                    icon = 'build';
                } else if (estadoClean === 'Listo') {
                    bgClass = 'bg-green-50 text-green-700 border-green-200';
                    icon = 'check_circle';
                } else if (estadoClean === 'Entregado') {
                    bgClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                    icon = 'check_circle';
                }
                
                return `<span class="px-2 py-0.5 font-bold uppercase text-[9px] tracking-wider border inline-flex items-center gap-1 ${bgClass}">
                    <span class="material-symbols-outlined text-[10px]">${icon}</span>
                    ${estadoClean}
                </span>`;
            };

            const escapeHTML = (str) => {
                return str.replace(/[&<>'"]/g, 
                    tag => ({
                        '&': '&amp;',
                        '<': '&lt;',
                        '>': '&gt;',
                        "'": '&#39;',
                        '"': '&quot;'
                    }[tag] || tag)
                );
            };

            // Clientes
            if (data.clientes && data.clientes.length > 0) {
                hasResults = true;
                html += `<div class="bg-zinc-50 border-b border-zinc-100 px-4 py-2 text-[9px] font-bold text-zinc-400 tracking-widest uppercase select-none">Clientes</div>`;
                data.clientes.forEach(c => {
                    html += `
                        <a href="${c.url}" class="search-result-item flex items-center justify-between px-4 py-3 hover:bg-zinc-50 border-b border-zinc-100/50 transition-colors group">
                            <div class="flex items-center gap-3">
                                <span class="material-symbols-outlined text-zinc-400 group-hover:text-[#0057FF] transition-colors">person</span>
                                <div class="flex flex-col">
                                    <span class="text-xs font-semibold text-[#1A1A1A]">${escapeHTML(c.nombre)}</span>
                                    <span class="text-[10px] text-zinc-400">DNI/CUIL: ${escapeHTML(c.dni_cuil)}</span>
                                </div>
                            </div>
                            <span class="material-symbols-outlined text-zinc-300 group-hover:text-primary transition-colors text-sm">arrow_forward</span>
                        </a>
                    `;
                });
            }

            // Equipos
            if (data.equipos && data.equipos.length > 0) {
                hasResults = true;
                html += `<div class="bg-zinc-50 border-b border-zinc-100 px-4 py-2 text-[9px] font-bold text-zinc-400 tracking-widest uppercase select-none">Equipos</div>`;
                data.equipos.forEach(e => {
                    html += `
                        <a href="${e.url}" class="search-result-item flex items-center justify-between px-4 py-3 hover:bg-zinc-50 border-b border-zinc-100/50 transition-colors group">
                            <div class="flex items-center gap-3">
                                <span class="material-symbols-outlined text-zinc-400 group-hover:text-[#0057FF] transition-colors">devices</span>
                                <div class="flex flex-col">
                                    <span class="text-xs font-semibold text-[#1A1A1A]">${escapeHTML(e.label)}</span>
                                    <span class="text-[10px] text-zinc-400">Cliente: ${escapeHTML(e.cliente_nombre)}</span>
                                </div>
                            </div>
                            <span class="material-symbols-outlined text-zinc-300 group-hover:text-primary transition-colors text-sm">arrow_forward</span>
                        </a>
                    `;
                });
            }

            // Órdenes
            if (data.ordenes && data.ordenes.length > 0) {
                hasResults = true;
                html += `<div class="bg-zinc-50 border-b border-zinc-100 px-4 py-2 text-[9px] font-bold text-zinc-400 tracking-widest uppercase select-none">Órdenes de Servicio</div>`;
                data.ordenes.forEach(o => {
                    html += `
                        <a href="${o.url}" class="search-result-item flex items-center justify-between px-4 py-3 hover:bg-zinc-50 border-b border-zinc-100/50 transition-colors group">
                            <div class="flex items-center gap-3">
                                <span class="material-symbols-outlined text-zinc-400 group-hover:text-[#0057FF] transition-colors">receipt_long</span>
                                <div class="flex flex-col gap-0.5">
                                    <div class="flex items-center gap-2">
                                        <span class="text-xs font-bold text-[#1A1A1A] font-mono">${escapeHTML(o.codigo)}</span>
                                        ${renderEstadoBadge(o.estado)}
                                    </div>
                                    <span class="text-[11px] font-medium text-[#1A1A1A]">
                                        ${escapeHTML(o.cliente)} • <span class="text-zinc-500 font-normal">${escapeHTML(o.equipo)}</span>
                                    </span>
                                    <span class="text-[10px] text-zinc-400 truncate max-w-[340px]">Falla: ${escapeHTML(o.falla)}</span>
                                </div>
                            </div>
                            <span class="material-symbols-outlined text-zinc-300 group-hover:text-primary transition-colors text-sm">arrow_forward</span>
                        </a>
                    `;
                });
            }

            if (!hasResults) {
                html = `
                    <div class="p-8 text-center text-zinc-400 select-none flex flex-col items-center gap-2">
                        <span class="material-symbols-outlined text-zinc-300 text-3xl">search_off</span>
                        <span class="text-[11px] font-medium">No se encontraron resultados para "${escapeHTML(query)}"</span>
                    </div>
                `;
            }

            globalSearchResults.innerHTML = html;
            globalSearchResults.classList.remove('hidden');
            activeIndex = -1;
        };

        const closeSearch = () => {
            globalSearchResults.innerHTML = '';
            globalSearchResults.classList.add('hidden');
            globalSearchInput.value = '';
            globalSearchClear?.classList.add('hidden');
            header?.classList.remove('mobile-search-active');
            activeIndex = -1;
        };

        // Input listener with debounce
        globalSearchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            debounceTimer = setTimeout(() => {
                performSearch(query);
            }, 250);
        });

        // Clear button click listener
        globalSearchClear?.addEventListener('click', () => {
            globalSearchInput.value = '';
            globalSearchInput.focus();
            performSearch('');
        });

        // Toggle mobile search
        mobileSearchToggle?.addEventListener('click', () => {
            header?.classList.add('mobile-search-active');
            setTimeout(() => {
                globalSearchInput.focus();
            }, 100);
        });

        // Back button on mobile search
        mobileSearchBack?.addEventListener('click', () => {
            closeSearch();
        });

        // Close on clicking outside
        document.addEventListener('click', (e) => {
            if (!globalSearchResults.contains(e.target) && 
                !globalSearchInput.contains(e.target) && 
                !mobileSearchToggle?.contains(e.target)) {
                globalSearchResults.classList.add('hidden');
            }
        });

        // Focus input to reopen results if not empty
        globalSearchInput.addEventListener('focus', () => {
            if (globalSearchInput.value.trim().length >= 2 && globalSearchResults.children.length > 0) {
                globalSearchResults.classList.remove('hidden');
            }
        });

        // Keyboard navigation (Escape, ArrowDown, ArrowUp, Enter)
        globalSearchInput.addEventListener('keydown', (e) => {
            const items = globalSearchResults.querySelectorAll('.search-result-item');
            if (!items.length) return;

            if (e.key === 'Escape') {
                closeSearch();
                globalSearchInput.blur();
                e.preventDefault();
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (activeIndex < items.length - 1) {
                    if (activeIndex >= 0) {
                        items[activeIndex].classList.remove('search-result-item-active');
                    }
                    activeIndex++;
                    items[activeIndex].classList.add('search-result-item-active');
                    items[activeIndex].scrollIntoView({ block: 'nearest' });
                }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (activeIndex > 0) {
                    items[activeIndex].classList.remove('search-result-item-active');
                    activeIndex--;
                    items[activeIndex].classList.add('search-result-item-active');
                    items[activeIndex].scrollIntoView({ block: 'nearest' });
                }
            } else if (e.key === 'Enter') {
                if (activeIndex >= 0 && activeIndex < items.length) {
                    e.preventDefault();
                    items[activeIndex].click();
                }
            }
        });
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

// --- LÓGICA DE ESCUCHA DE NOTIFICACIONES EN TIEMPO REAL (SSE) ---
(function iniciarSSE() {
    const sseSource = new EventSource('/notificaciones/stream');

    sseSource.onmessage = function (event) {
        try {
            const data = JSON.parse(event.data);
            
            // Si el mensaje es un ping, simplemente mantener la conexión viva
            if (data.type === 'ping') {
                return;
            }

            // Si la notificación pertenece al usuario autenticado actual
            if (window.USER_ID && data.usuario_id === window.USER_ID) {
                // 1. Mostrar Toast dinámico en la pantalla
                window.showToast(`${data.titulo}: ${data.mensaje}`, 'success');

                // 2. Incrementar dinámicamente el contador rojo del navbar si existe
                const countBadge = document.querySelector('#notification-btn span');
                if (countBadge) {
                    let currentCount = parseInt(countBadge.textContent.trim()) || 0;
                    countBadge.textContent = currentCount + 1;
                } else {
                    // Si no tiene contador visible, inyectar el elemento badge dinámicamente
                    const notifBtn = document.getElementById('notification-btn');
                    if (notifBtn) {
                        const newBadge = document.createElement('span');
                        newBadge.className = 'absolute top-0 right-0 h-4 w-4 bg-red-500 rounded-full text-[9px] font-bold text-white flex items-center justify-center animate-pulse';
                        newBadge.textContent = '1';
                        notifBtn.appendChild(newBadge);
                    }
                }

                // 3. Inyectar la notificación en la lista del Dropdown en tiempo real
                const notifList = document.querySelector('#notification-dropdown .divide-y');
                if (notifList) {
                    // Quitar cartel de "no tienes notificaciones" si existe
                    const emptyState = notifList.querySelector('.p-8');
                    if (emptyState) emptyState.remove();

                    const date = new Date();
                    const dateStr = `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;

                    const newNotifHtml = `
                        <div onclick="handleNotificationClick(${data.id || 0}, '/tablero-tickets/${data.orden_id}')"
                            class="p-4 hover:bg-zinc-50 cursor-pointer transition-colors relative bg-[#0057FF]/5 border-l-2 border-[#0057FF]">
                            <div class="flex justify-between items-start mb-1">
                                <span class="font-bold text-[#1A1A1A] pr-2">${data.titulo}</span>
                                <span class="text-[9px] text-zinc-400 font-mono whitespace-nowrap">${dateStr}</span>
                            </div>
                            <p class="text-[11px] text-zinc-600 leading-normal">${data.mensaje}</p>
                        </div>
                    `;
                    notifList.insertAdjacentHTML('afterbegin', newNotifHtml);
                }
            }
        } catch (err) {
            console.error('Error al procesar mensaje SSE:', err);
        }
    };

    sseSource.onerror = function () {
        console.warn('Conexión SSE perdida. Reintentando...');
    };
})();
