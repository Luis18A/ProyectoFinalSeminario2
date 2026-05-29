// Lógica Interactiva para Técnicos (Presupuestos, Cálculos y Scraping)
document.addEventListener('DOMContentLoaded', () => {
    const config = window.ticketConfig || {
        repuestosActivos: [],
        ordenId: null,
        ordenCostoInicial: 0.0,
        technicianUrl: '#'
    };

    const repuestosActivos = config.repuestosActivos;
    const ordenId = config.ordenId;
    const ordenCostoInicial = config.ordenCostoInicial;
    const technicianUrl = config.technicianUrl;

    const inputManoObra = document.getElementById('input-mano-obra');
    const inputCostoTotal = document.getElementById('input-costo-total');

    function recalcularDesglose() {
        const totalRepuestos = repuestosActivos.reduce((acc, curr) => acc + curr.precio, 0);
        
        let manoObra = 0;
        if (inputManoObra) {
            manoObra = parseFloat(inputManoObra.value) || 0;
        }
        
        const total = manoObra + totalRepuestos;
        
        if (inputCostoTotal) {
            inputCostoTotal.value = total.toFixed(2);
        }
        
        const displayRepuestos = document.getElementById('costo-repuestos-display');
        const displayLabor = document.getElementById('costo-labor-display');
        const displayTotal = document.getElementById('costo-total-display');
        
        if (displayRepuestos) displayRepuestos.textContent = '$' + totalRepuestos.toFixed(2);
        if (displayLabor) displayLabor.textContent = '$' + manoObra.toFixed(2);
        if (displayTotal) displayTotal.textContent = '$' + total.toFixed(2);
    }

    function renderRepuestos() {
        const container = document.getElementById('tabla-repuestos-container');
        const itemsCountLabel = document.getElementById('repuestos-count-label');
        if (!container) return;

        if (itemsCountLabel) {
            itemsCountLabel.textContent = `ITEMS: ${repuestosActivos.length}`;
        }

        if (repuestosActivos.length === 0) {
            container.innerHTML = `
                <p class="text-xs text-zinc-400 italic bg-zinc-50 p-4 text-center border border-dashed border-zinc-200">
                    No se han agregado repuestos al presupuesto de este equipo.
                </p>
            `;
            recalcularDesglose();
            return;
        }

        let tbodyHtml = '';
        repuestosActivos.forEach((r, idx) => {
            let badge = '';
            if (r.tienda === 'MercadoLibre') {
                badge = `<span class="px-2 py-0.5 bg-yellow-50 text-yellow-700 border border-yellow-200 text-[8px] font-bold uppercase rounded">ML</span>`;
            } else if (r.tienda === 'Megatone') {
                badge = `<span class="px-2 py-0.5 bg-red-50 text-red-700 border border-red-200 text-[8px] font-bold uppercase rounded">Mega</span>`;
            } else if (r.tienda === 'Fravega') {
                badge = `<span class="px-2 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 text-[8px] font-bold uppercase rounded">Fravega</span>`;
            } else {
                badge = `<span class="px-2 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 text-[8px] font-bold uppercase rounded">${r.tienda}</span>`;
            }

            tbodyHtml += `
                <tr class="hover:bg-zinc-50 transition-colors">
                    <td class="p-3">${badge}</td>
                    <td class="p-3 font-semibold text-zinc-700">
                        <a href="${r.link}" target="_blank" class="hover:underline text-primary flex items-center gap-1">
                            ${r.titulo.substring(0, 60)}${r.titulo.length > 60 ? '...' : ''} 
                            <span class="material-symbols-outlined text-[12px]">open_in_new</span>
                        </a>
                    </td>
                    <td class="p-3 text-right font-bold text-zinc-800">
                        $${r.precio.toFixed(2)}
                    </td>
                    <td class="p-3 text-center">
                        <button type="button" class="btn-eliminar-repuesto text-red-500 hover:text-red-700 transition-colors" data-idx="${idx}" title="Remover repuesto">
                            <span class="material-symbols-outlined text-[18px]">delete</span>
                        </button>
                    </td>
                </tr>
            `;
        });

        container.innerHTML = `
            <div class="border border-[#1A1A1A]/10 overflow-hidden">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-zinc-50 border-b border-zinc-100 text-[10px] uppercase font-bold text-zinc-400">
                            <th class="p-3">Proveedor</th>
                            <th class="p-3">Producto</th>
                            <th class="p-3 text-right">Precio</th>
                            <th class="p-3 text-center">Remover</th>
                        </tr>
                    </thead>
                    <tbody class="text-xs divide-y divide-zinc-50">
                        ${tbodyHtml}
                    </tbody>
                </table>
            </div>
        `;

        // Bind click events on newly rendered delete buttons
        container.querySelectorAll('.btn-eliminar-repuesto').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(btn.getAttribute('data-idx'));
                eliminarRepuesto(idx);
            });
        });

        recalcularDesglose();
    }

    // Inicializar desglose
    const totalRepuestosInicial = repuestosActivos.reduce((acc, curr) => acc + curr.precio, 0);
    if (inputManoObra) {
        const manoObraInicial = Math.max(0, ordenCostoInicial - totalRepuestosInicial);
        inputManoObra.value = manoObraInicial.toFixed(2);
        inputManoObra.addEventListener('input', recalcularDesglose);
    }
    
    renderRepuestos();

    // Evitar que el formulario se envíe al presionar ENTER en cualquier input
    const formActualizar = document.querySelector('form[action*="editar_ordenServicio"]');
    if (formActualizar) {
        formActualizar.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
                e.preventDefault();
            }
        });
    }

    // Si se presiona Enter en el input de búsqueda de repuestos, iniciar búsqueda
    const repuestoQueryInput = document.getElementById('repuesto-query');
    if (repuestoQueryInput) {
        repuestoQueryInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                buscarRepuestosTaller();
            }
        });
    }

    // Vincular botón de búsqueda de repuestos
    const btnBuscarRepuestos = document.getElementById('btn-buscar-repuestos');
    if (btnBuscarRepuestos) {
        btnBuscarRepuestos.addEventListener('click', buscarRepuestosTaller);
    }

    // Vincular botón de solicitud de aprobación
    const btnEnviarPresupuesto = document.querySelector('button[onclick="solicitarAprobacionPresupuesto()"]');
    if (btnEnviarPresupuesto) {
        // Reemplazar onclick inline por event listener
        btnEnviarPresupuesto.removeAttribute('onclick');
        btnEnviarPresupuesto.addEventListener('click', solicitarAprobacionPresupuesto);
    }

    // Gestión de Repuestos (AJAX)
    async function agregarRepuestoAlPresupuesto(titulo, precio, link, tienda) {
        try {
            const formData = new FormData();
            formData.append('titulo', titulo);
            formData.append('precio', precio);
            formData.append('link', link);
            formData.append('tienda', tienda);
            
            const resp = await fetch(`/ordenServicio/${ordenId}/repuesto/agregar`, {
                method: 'POST',
                body: formData
            });
            const data = await resp.json();
            if (data.success) {
                repuestosActivos.push({
                    titulo: titulo,
                    precio: parseFloat(precio),
                    link: link,
                    tienda: tienda
                });
                renderRepuestos();
                window.showToast('Repuesto agregado al presupuesto con éxito.', 'success');
            } else {
                window.showToast('Error al agregar: ' + data.message, 'error');
            }
        } catch (err) {
            console.error(err);
            window.showToast('Ocurrió un error al agregar el repuesto.', 'error');
        }
    }

    // Exponer agregarRepuestoAlPresupuesto globalmente para el botón '+ Cotizar' inyectado dinámicamente
    window.agregarRepuestoAlPresupuesto = agregarRepuestoAlPresupuesto;

    async function eliminarRepuesto(idx) {
        if (!confirm('¿Seguro que querés remover este repuesto del presupuesto?')) {
            return;
        }
        
        try {
            const resp = await fetch(`/ordenServicio/${ordenId}/repuesto/eliminar/${idx}`, {
                method: 'POST'
            });
            const data = await resp.json();
            if (data.success) {
                repuestosActivos.splice(idx, 1);
                renderRepuestos();
                window.showToast('Repuesto eliminado y presupuesto actualizado.', 'success');
            } else {
                window.showToast('Error: ' + data.message, 'error');
            }
        } catch (err) {
            console.error(err);
            window.showToast('Ocurrió un error al eliminar el repuesto.', 'error');
        }
    }

    async function solicitarAprobacionPresupuesto() {
        if (!inputCostoTotal || !inputCostoTotal.value || parseFloat(inputCostoTotal.value) <= 0) {
            window.showToast('Por favor, ingresá un costo de reparación mayor a $0 en el formulario de arriba primero.', 'error');
            return;
        }
        
        if (!confirm('¿Enviar el presupuesto actual para confirmación del cliente? El ticket pasará a estado PRESUPUESTADO.')) {
            return;
        }
        
        try {
            if (formActualizar) {
                const formD = new FormData(formActualizar);
                formD.set('estado', 'PRESUPUESTADO');
                formD.set('observaciones', 'Presupuesto de repuestos y mano de obra enviado a secretaría para confirmación del cliente.');
                
                const response = await fetch(formActualizar.action, {
                    method: 'POST',
                    body: formD
                });
                
                if (response.ok) {
                    window.showToast('Presupuesto enviado. Se notificará a secretaría en el panel.', 'success');
                    setTimeout(() => window.location.href = technicianUrl, 1500);
                } else {
                    window.showToast('Error al procesar la actualización.', 'error');
                }
            }
        } catch (err) {
            console.error(err);
            window.showToast('Ocurrió un error al guardar y enviar el presupuesto.', 'error');
        }
    }

    // Buscador de Repuestos (Scraping)
    async function buscarRepuestosTaller() {
        const queryValInput = document.getElementById('repuesto-query');
        if (!queryValInput) return;
        const query = queryValInput.value.trim();
        if (!query) {
            window.showToast('Ingresá algún término de búsqueda para repuestos.', 'error');
            return;
        }
        
        const loading = document.getElementById('repuestos-loading');
        const container = document.getElementById('repuestos-results-container');
        const tbody = document.getElementById('repuestos-results-body');
        
        loading.classList.remove('hidden');
        container.classList.add('hidden');
        tbody.innerHTML = '';
        
        try {
            const resp = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`);
            if (!resp.ok) {
                throw new Error('Servidor de Scraping no responde');
            }
            
            const data = await resp.json();
            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" class="p-6 text-center text-zinc-400">No se encontraron repuestos para tu búsqueda.</td></tr>`;
            } else {
                data.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.className = 'hover:bg-zinc-50 border-b border-zinc-100 transition-colors';
                    
                    let tiendaHtml = '';
                    if (item.tienda === 'MercadoLibre') {
                        tiendaHtml = `<span class="px-2 py-0.5 bg-yellow-100 text-yellow-800 border border-yellow-200 text-[9px] font-bold uppercase rounded">ML</span>`;
                    } else if (item.tienda === 'Megatone') {
                        tiendaHtml = `<span class="px-2 py-0.5 bg-red-100 text-red-800 border border-red-200 text-[9px] font-bold uppercase rounded">Mega</span>`;
                    } else if (item.tienda === 'Fravega') {
                        tiendaHtml = `<span class="px-2 py-0.5 bg-purple-100 text-purple-800 border border-purple-200 text-[9px] font-bold uppercase rounded">Fravega</span>`;
                    } else {
                        tiendaHtml = `<span class="px-2 py-0.5 bg-gray-100 text-gray-800 border border-gray-200 text-[9px] font-bold uppercase rounded">${item.tienda}</span>`;
                    }
                    
                    const escTitulo = item.titulo.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                    
                    tr.innerHTML = `
                        <td class="p-2.5 text-center">${tiendaHtml}</td>
                        <td class="p-2.5 max-w-[240px] truncate" title="${item.titulo}">
                            <a href="${item.link}" target="_blank" class="text-primary hover:underline font-medium">
                                ${item.titulo}
                            </a>
                        </td>
                        <td class="p-2.5 text-right font-bold text-accent">$${item.precio.toLocaleString('es-AR')}</td>
                        <td class="p-2.5 text-center">
                            <button type="button" onclick="agregarRepuestoAlPresupuesto('${escTitulo}', ${item.precio}, '${item.link}', '${item.tienda}')"
                                    class="px-2 py-1 bg-zinc-900 text-white font-bold uppercase text-[9px] hover:bg-primary transition-all">
                                + Cotizar
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }
            container.classList.remove('hidden');
        } catch (err) {
            console.error(err);
            tbody.innerHTML = `<tr><td colspan="4" class="p-6 text-center text-red-500 font-semibold">El microservicio de Scraping de FastAPI (puerto 8000) no responde. Asegurate de que esté encendido para buscar ofertas.</td></tr>`;
            container.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    }
});
