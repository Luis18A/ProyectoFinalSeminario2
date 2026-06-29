// Lógica Interactiva para Técnicos (Presupuestos, Cálculos y Scraping)
document.addEventListener('DOMContentLoaded', () => {
    // Proteger las propiedades críticas de ticketConfig contra manipulación en consola
    if (window.ticketConfig) {
        try {
            Object.defineProperty(window.ticketConfig, 'ordenId', { writable: false, configurable: false });
            Object.defineProperty(window.ticketConfig, 'puedeEditar', { writable: false, configurable: false });
            Object.defineProperty(window.ticketConfig, 'puedeEditarCostos', { writable: false, configurable: false });
            Object.defineProperty(window.ticketConfig, 'ordenCostoInicial', { writable: false, configurable: false });
        } catch (e) {
            console.warn('No se pudo congelar ticketConfig:', e);
        }
    }

    const config = window.ticketConfig || {
        repuestosActivos: [],
        ordenId: null,
        ordenCostoInicial: 0.0,
        puedeEditar: false,
        technicianUrl: '#'
    };

    const repuestosActivos = config.repuestosActivos;
    const ordenId = config.ordenId;
    const ordenCostoInicial = config.ordenCostoInicial;
    const puedeEditar = config.puedeEditar !== undefined ? config.puedeEditar : false;
    const puedeEditarCostos = config.puedeEditarCostos !== undefined ? config.puedeEditarCostos : false;
    const technicianUrl = config.technicianUrl;

    let editIdx = null;
    const inputManoObra = document.getElementById('input-mano-obra');
    const inputCostoTotal = document.getElementById('input-costo-total');

    function recalcularDesglose() {
        const totalRepuestos = Math.max(0, repuestosActivos.reduce((acc, curr) => acc + curr.precio, 0));
        
        let manoObra = 0;
        if (inputManoObra) {
            manoObra = parseFloat(inputManoObra.value) || 0;
            if (manoObra < 0) {
                manoObra = 0;
                inputManoObra.value = "0.00";
            }
        }
        
        const total = manoObra + totalRepuestos;
        
        if (inputCostoTotal && inputCostoTotal.hasAttribute('readonly')) {
            inputCostoTotal.value = total.toFixed(2);
        }
        
        const displayRepuestos = document.getElementById('costo-repuestos-display');
        const displayLabor = document.getElementById('costo-labor-display');
        const displayTotal = document.getElementById('costo-total-display');
        
        if (displayRepuestos) displayRepuestos.textContent = '$' + totalRepuestos.toFixed(2);
        if (displayLabor) displayLabor.textContent = '$' + manoObra.toFixed(2);
        if (displayTotal) {
            if (inputCostoTotal && !inputCostoTotal.hasAttribute('readonly')) {
                let manualTotal = parseFloat(inputCostoTotal.value) || 0;
                if (manualTotal < 0) {
                    manualTotal = 0;
                    inputCostoTotal.value = "0.00";
                }
                displayTotal.textContent = '$' + manualTotal.toFixed(2);
            } else {
                displayTotal.textContent = '$' + total.toFixed(2);
            }
        }
    }

    function renderRepuestos() {
        const container = document.getElementById('tabla-repuestos-container');
        const itemsCountLabel = document.getElementById('repuestos-count-label');
        if (!container) return;

        const selectEstadoEl = document.getElementById('select-estado');
        const estadoSeleccionado = selectEstadoEl ? selectEstadoEl.value : '';
        const ocultarPorEstado = ['REPARACION', 'LISTO', 'ENTREGADO'].includes(estadoSeleccionado);
        const mostrarAcciones = puedeEditar && puedeEditarCostos && !ocultarPorEstado;

        if (itemsCountLabel) {
            itemsCountLabel.textContent = `ÍTEMS: ${repuestosActivos.length}`;
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
            } else if (r.tienda === 'Manual') {
                badge = `<span class="px-2 py-0.5 bg-zinc-100 text-zinc-700 border border-zinc-300 text-[8px] font-bold uppercase rounded">Manual</span>`;
            } else {
                badge = `<span class="px-2 py-0.5 bg-purple-50 text-purple-700 border border-purple-200 text-[8px] font-bold uppercase rounded">${r.tienda}</span>`;
            }

            const hasLink = r.link && r.link !== '#' && r.link.trim() !== '';
            const linkHtml = hasLink
                ? `<a href="${r.link}" target="_blank" class="hover:underline text-primary flex items-center gap-1">
                      ${r.titulo.substring(0, 60)}${r.titulo.length > 60 ? '...' : ''} 
                      <span class="material-symbols-outlined text-[12px]">open_in_new</span>
                   </a>`
                : `<span class="text-zinc-700 font-semibold">${r.titulo.substring(0, 60)}${r.titulo.length > 60 ? '...' : ''}</span>`;

            if (idx === editIdx) {
                tbodyHtml += `
                    <tr class="bg-zinc-50 transition-colors">
                        <td class="p-3">${badge}</td>
                        <td class="p-3">
                            <input type="text" id="edit-repuesto-titulo-${idx}" class="input-swiss text-xs py-1 px-2 w-full bg-white border border-zinc-300" value="${r.titulo}">
                        </td>
                        <td class="p-3 text-right">
                            <input type="number" step="0.01" id="edit-repuesto-precio-${idx}" class="input-swiss text-xs py-1 px-2 w-28 bg-white border border-zinc-300 text-right font-bold" value="${r.precio}">
                        </td>
                        <td class="p-3 text-center">
                            <div class="flex items-center justify-center gap-2">
                                <button type="button" class="btn-guardar-repuesto text-emerald-600 hover:text-emerald-800 transition-colors" data-idx="${idx}" title="Guardar cambios">
                                    <span class="material-symbols-outlined text-[18px]">check_circle</span>
                                </button>
                                <button type="button" class="btn-cancelar-repuesto text-zinc-500 hover:text-zinc-700 transition-colors" data-idx="${idx}" title="Cancelar">
                                    <span class="material-symbols-outlined text-[18px]">cancel</span>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            } else {
                tbodyHtml += `
                    <tr class="hover:bg-zinc-50 transition-colors">
                        <td class="p-3">${badge}</td>
                        <td class="p-3 font-semibold text-zinc-700">
                            ${linkHtml}
                        </td>
                        <td class="p-3 text-right font-bold text-zinc-800">
                            $${r.precio.toFixed(2)}
                        </td>
                        ${mostrarAcciones ? `
                        <td class="p-3 text-center">
                            <div class="flex items-center justify-center gap-2">
                                <button type="button" class="btn-editar-repuesto text-blue-500 hover:text-blue-700 transition-colors" data-idx="${idx}" title="Editar repuesto">
                                    <span class="material-symbols-outlined text-[18px]">edit</span>
                                </button>
                                <button type="button" class="btn-eliminar-repuesto text-red-500 hover:text-red-700 transition-colors" data-idx="${idx}" title="Remover repuesto">
                                    <span class="material-symbols-outlined text-[18px]">delete</span>
                                </button>
                            </div>
                        </td>` : ''}
                    </tr>
                `;
            }
        });

        container.innerHTML = `
            <div class="border border-[#1A1A1A]/10 overflow-hidden">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-zinc-50 border-b border-zinc-100 text-[10px] uppercase font-bold text-zinc-400">
                            <th class="p-3">Proveedor</th>
                            <th class="p-3">Producto</th>
                            <th class="p-3 text-right">Precio</th>
                            ${mostrarAcciones ? '<th class="p-3 text-center">Acciones</th>' : ''}
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

        // Bind click events on edit/save/cancel buttons
        container.querySelectorAll('.btn-editar-repuesto').forEach(btn => {
            btn.addEventListener('click', (e) => {
                editIdx = parseInt(btn.getAttribute('data-idx'));
                renderRepuestos();
            });
        });

        container.querySelectorAll('.btn-cancelar-repuesto').forEach(btn => {
            btn.addEventListener('click', (e) => {
                editIdx = null;
                renderRepuestos();
            });
        });

        container.querySelectorAll('.btn-guardar-repuesto').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const idx = parseInt(btn.getAttribute('data-idx'));
                const inputTitulo = document.getElementById(`edit-repuesto-titulo-${idx}`);
                const inputPrecio = document.getElementById(`edit-repuesto-precio-${idx}`);
                if (inputTitulo && inputPrecio) {
                    const nuevoTitulo = inputTitulo.value.trim();
                    const nuevoPrecioRaw = inputPrecio.value.trim();
                    if (!nuevoTitulo) {
                        window.showToast('La descripción no puede estar vacía.', 'error');
                        return;
                    }
                    if (!nuevoPrecioRaw || isNaN(parseFloat(nuevoPrecioRaw)) || parseFloat(nuevoPrecioRaw) < 0) {
                        window.showToast('El precio debe ser un número válido mayor o igual a 0.', 'error');
                        return;
                    }
                    const nuevoPrecio = parseFloat(nuevoPrecioRaw);
                    await guardarEdicionRepuesto(idx, nuevoTitulo, nuevoPrecio);
                }
            });
        });

        recalcularDesglose();
    }

    // Inicializar desglose
    const totalRepuestosInicial = repuestosActivos.reduce((acc, curr) => acc + curr.precio, 0);
    if (inputManoObra) {
        const manoObraInicial = Math.max(0, ordenCostoInicial - totalRepuestosInicial);
        inputManoObra.value = manoObraInicial.toFixed(2);
        
        // Evitar números negativos en tiempo real
        inputManoObra.addEventListener('input', () => {
            if (parseFloat(inputManoObra.value) < 0) {
                inputManoObra.value = 0;
            }
            recalcularDesglose();
        });
    }
    
    if (inputCostoTotal && !inputCostoTotal.hasAttribute('readonly')) {
        // Evitar números negativos en tiempo real
        inputCostoTotal.addEventListener('input', () => {
            if (parseFloat(inputCostoTotal.value) < 0) {
                inputCostoTotal.value = 0;
            }
            const displayTotal = document.getElementById('costo-total-display');
            if (displayTotal) {
                const val = parseFloat(inputCostoTotal.value) || 0;
                displayTotal.textContent = '$' + val.toFixed(2);
            }
        });
    }
    
    // renderRepuestos() is called inside actualizarVisibilidadPresupuesto() below

    // Evitar que el formulario se envíe al presionar ENTER en cualquier input
    const formActualizar = document.querySelector('form[action*="/ordenServicio/editar/"]');
    if (formActualizar) {
        formActualizar.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.tagName === 'INPUT') {
                e.preventDefault();
            }
        });

        formActualizar.addEventListener('submit', (e) => {
            const selectEstadoEl = document.getElementById('select-estado');
            const inputDiagEl = document.getElementsByName('estado_diagnostico')[0];

            const estadoDestino = selectEstadoEl ? selectEstadoEl.value : '';
            const diagVal = inputDiagEl ? inputDiagEl.value.trim() : '';

            if (estadoDestino && estadoDestino !== 'PENDIENTE' && !diagVal) {
                e.preventDefault();
                window.showToast('El diagnóstico técnico es obligatorio para el estado seleccionado o actual.', 'error');
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
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                },
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
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                }
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

    async function guardarEdicionRepuesto(idx, titulo, precio) {
        try {
            const formData = new FormData();
            formData.append('titulo', titulo);
            formData.append('precio', precio);
            
            const resp = await fetch(`/ordenServicio/${ordenId}/repuesto/editar/${idx}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                },
                body: formData
            });
            const data = await resp.json();
            if (data.success) {
                repuestosActivos[idx].titulo = titulo;
                repuestosActivos[idx].precio = precio;
                editIdx = null;
                renderRepuestos();
                window.showToast('Repuesto actualizado con éxito.', 'success');
            } else {
                window.showToast('Error al editar: ' + data.message, 'error');
            }
        } catch (err) {
            console.error(err);
            window.showToast('Ocurrió un error al guardar los cambios.', 'error');
        }
    }

    async function solicitarAprobacionPresupuesto() {
        if (!inputCostoTotal || !inputCostoTotal.value || parseFloat(inputCostoTotal.value) <= 0) {
            window.showToast('Por favor, ingresá un costo de reparación mayor a $0 en el formulario de arriba primero.', 'error');
            return;
        }

        const inputDiagEl = document.getElementsByName('estado_diagnostico')[0];
        const diagVal = inputDiagEl ? inputDiagEl.value.trim() : '';
        if (!diagVal) {
            window.showToast('El diagnóstico técnico es obligatorio para poder enviar el presupuesto.', 'error');
            return;
        }
        
        if (!confirm('¿Enviar el presupuesto actual para confirmación del cliente? El ticket pasará a estado PRESUPUESTADO.')) {
            return;
        }
        
        try {
            if (formActualizar) {
                const formD = new FormData(formActualizar);
                formD.set('estado', 'PRESUPUESTADO');
                
                const response = await fetch(formActualizar.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                    },
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
            const scraperHost = window.location.hostname;
            const resp = await fetch(`http://${scraperHost}:8000/search?q=${encodeURIComponent(query)}`);
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

    // Gestión de Repuestos Manuales
    const btnAgregarManual = document.getElementById('btn-agregar-manual');
    const inputManualTitulo = document.getElementById('repuesto-manual-titulo');
    const inputManualPrecio = document.getElementById('repuesto-manual-precio');

    if (btnAgregarManual && inputManualTitulo && inputManualPrecio) {
        btnAgregarManual.addEventListener('click', async () => {
            const titulo = inputManualTitulo.value.trim();
            const precioRaw = inputManualPrecio.value.trim();
            
            if (!titulo) {
                window.showToast('Por favor, ingresá una descripción para el repuesto.', 'error');
                return;
            }
            if (!precioRaw || isNaN(parseFloat(precioRaw)) || parseFloat(precioRaw) < 0) {
                window.showToast('Por favor, ingresá un precio válido (mayor o igual a 0).', 'error');
                return;
            }
            
            const precio = parseFloat(precioRaw);
            
            // Deshabilitar botón para evitar doble envío
            btnAgregarManual.disabled = true;
            btnAgregarManual.textContent = 'Agregando...';
            
            try {
                await agregarRepuestoAlPresupuesto(titulo, precio, '#', 'Manual');
                // Limpiar inputs
                inputManualTitulo.value = '';
                inputManualPrecio.value = '';
            } catch (err) {
                console.error(err);
            } finally {
                btnAgregarManual.disabled = false;
                btnAgregarManual.innerHTML = '<span class="material-symbols-outlined text-[14px]">add</span> Agregar';
            }
        });

        // Permitir presionar ENTER para agregar desde los inputs de repuesto manual
        const handleManualEnter = (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                btnAgregarManual.click();
            }
        };
        inputManualTitulo.addEventListener('keydown', handleManualEnter);
        inputManualPrecio.addEventListener('keydown', handleManualEnter);
    }

    // Aceptar Presupuesto por parte de la Secretaria (desde vista detalle)
    async function confirmarPresupuestoSecretaria() {
        if (!confirm(`¿Confirmar que el cliente acepta el presupuesto de $${ordenCostoInicial.toFixed(2)} y empezar reparación?`)) {
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
    }
    window.confirmarPresupuestoSecretaria = confirmarPresupuestoSecretaria;

    // Rechazar Presupuesto por parte de la Secretaria (desde vista detalle)
    async function rechazarPresupuestoSecretaria() {
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
    }
    window.rechazarPresupuestoSecretaria = rechazarPresupuestoSecretaria;

    // Entregar Equipo por parte de la Secretaria (desde vista detalle)
    async function entregarEquipoSecretaria() {
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
    }
    window.entregarEquipoSecretaria = entregarEquipoSecretaria;

    // Lógica para mostrar/ocultar secciones de presupuesto según el estado seleccionado
    const selectEstado = document.getElementById('select-estado');
    const seccionAgregarManual = document.getElementById('seccion-agregar-manual');
    const seccionBuscadorRepuestos = document.getElementById('seccion-buscador-repuestos');
    const contenedorEnviarPresupuesto = document.getElementById('contenedor-enviar-presupuesto');

    function actualizarVisibilidadPresupuesto() {
        if (selectEstado) {
            const estadoSeleccionado = selectEstado.value;
            const ocultar = ['REPARACION', 'LISTO', 'ENTREGADO'].includes(estadoSeleccionado);

            if (ocultar) {
                if (seccionAgregarManual) seccionAgregarManual.classList.add('hidden');
                if (seccionBuscadorRepuestos) seccionBuscadorRepuestos.classList.add('hidden');
                if (contenedorEnviarPresupuesto) contenedorEnviarPresupuesto.classList.add('hidden');
                if (inputManoObra) inputManoObra.disabled = true;
            } else {
                if (seccionAgregarManual) seccionAgregarManual.classList.remove('hidden');
                if (seccionBuscadorRepuestos) seccionBuscadorRepuestos.classList.remove('hidden');
                if (contenedorEnviarPresupuesto) contenedorEnviarPresupuesto.classList.remove('hidden');
                if (inputManoObra) inputManoObra.disabled = !(puedeEditar && puedeEditarCostos);
            }
        }
        
        // Renderizar la tabla de repuestos cotizados
        renderRepuestos();
    }

    if (selectEstado) {
        selectEstado.addEventListener('change', actualizarVisibilidadPresupuesto);
        // Inicializar visibilidad al cargar la página
        actualizarVisibilidadPresupuesto();
    } else {
        // Si no existe select-estado (modo de lectura), renderizar repuestos de todos modos
        renderRepuestos();
    }
});
