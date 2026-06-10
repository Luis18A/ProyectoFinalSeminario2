/**
 * Core Application Logic - TechFlow Service Hub
 * Maneja funcionalidades compartidas, responsividad (Sidebar/Menú) y Búsqueda Global.
 */

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const mainContent = document.getElementById('main-content');
    const overlay = document.getElementById('sidebar-overlay');
    
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
                <div class="p-4 text-center text-xs text-zinc-500 font-['Space_Grotesk']">
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
                <div class="bg-zinc-50/50 p-2 text-[9px] font-bold text-zinc-400 uppercase tracking-widest font-['Space_Grotesk'] border-t border-zinc-100">Tickets de Servicio</div>
                <div class="py-1">
            `;
            data.ordenes.forEach(o => {
                html += `
                    <a href="${o.url}" class="block px-4 py-2 hover:bg-zinc-50 transition-colors">
                        <div class="flex justify-between items-center">
                            <span class="font-bold text-xs text-primary font-['Space_Grotesk']">${o.codigo}</span>
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
                <div class="bg-zinc-50/50 p-2 text-[9px] font-bold text-zinc-400 uppercase tracking-widest font-['Space_Grotesk'] border-t border-zinc-100">Clientes</div>
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
                <div class="bg-zinc-50/50 p-2 text-[9px] font-bold text-zinc-400 uppercase tracking-widest font-['Space_Grotesk'] border-t border-zinc-100">Equipos</div>
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
