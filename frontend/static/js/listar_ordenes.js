/**
 * TechFlow Secretary View Logic
 * Maneja la carga dinámica de equipos, alta rápida de clientes y equipos con AJAX,
 * y cambios rápidos de estado del flujo de reparación.
 */



function abrirModalRegistrarOrden() {
    const modal = document.getElementById('modal-registrar-orden');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function cerrarModalRegistrarOrden() {
    const modal = document.getElementById('modal-registrar-orden');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('form-orden').reset();
        
        // Reset dynamic fields
        const selectCliente = document.getElementById('select-cliente');
        if (selectCliente) {
            selectCliente.value = '';
        }
        const buscarClienteInput = document.getElementById('buscar-cliente-input');
        if (buscarClienteInput) {
            buscarClienteInput.value = '';
        }
        const buscarClienteDropdown = document.getElementById('buscar-cliente-dropdown');
        if (buscarClienteDropdown) {
            buscarClienteDropdown.classList.add('hidden');
            buscarClienteDropdown.innerHTML = '';
        }
        const selectEquipo = document.getElementById('select-equipo');
        if (selectEquipo) {
            selectEquipo.innerHTML = '<option value="">— Primero seleccione un cliente —</option>';
            selectEquipo.disabled = true;
        }
        const equipoHint = document.getElementById('equipo-hint');
        if (equipoHint) {
            equipoHint.classList.add('hidden');
        }
    }
    document.body.style.overflow = 'auto';
}

// Las transiciones rápidas de estado (confirmarPresupuesto, rechazarPresupuesto, entregarEquipo) ahora son globales y residen en app.js

document.addEventListener('DOMContentLoaded', () => {
    const selectCliente = document.getElementById('select-cliente');
    const selectEquipo = document.getElementById('select-equipo');
    const equipoHint = document.getElementById('equipo-hint');
    const formOrden = document.getElementById('form-orden');

    // Función auxiliar para cargar equipos de un cliente seleccionado
    async function cargarEquiposCliente(clienteId) {
        selectEquipo.innerHTML = '<option value="">— Cargando equipos... —</option>';
        selectEquipo.disabled = true;
        equipoHint.classList.add('hidden');

        if (!clienteId) {
            selectEquipo.innerHTML = '<option value="">— Primero seleccione un cliente —</option>';
            return;
        }

        try {
            const resp = await fetch(`/clientes/${clienteId}/equipos`);
            const equipos = await resp.json();

            selectEquipo.innerHTML = '';

            if (equipos.length === 0) {
                selectEquipo.innerHTML = '<option value="">Sin equipos registrados</option>';
                equipoHint.classList.remove('hidden');
            } else {
                selectEquipo.innerHTML = '<option value="">— Seleccionar equipo —</option>';
                equipos.forEach(eq => {
                    const opt = document.createElement('option');
                    opt.value = eq.id;
                    opt.textContent = eq.label;
                    selectEquipo.appendChild(opt);
                });
                selectEquipo.disabled = false;
            }
        } catch (err) {
            selectEquipo.innerHTML = '<option value="">Error al cargar equipos</option>';
            console.error(err);
        }
    }

    if (selectCliente && selectEquipo && equipoHint) {
        selectCliente.addEventListener('change', function () {
            cargarEquiposCliente(this.value);
        });
    }

    // Buscador en tiempo real de clientes en el modal de nueva orden
    const buscarClienteInput = document.getElementById('buscar-cliente-input');
    const buscarClienteDropdown = document.getElementById('buscar-cliente-dropdown');
    
    if (buscarClienteInput && buscarClienteDropdown && selectCliente) {
        let searchTimeout;
        buscarClienteInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            if (query.length === 0) {
                buscarClienteDropdown.classList.add('hidden');
                buscarClienteDropdown.innerHTML = '';
                selectCliente.value = '';
                selectCliente.dispatchEvent(new Event('change'));
                return;
            }
            
            searchTimeout = setTimeout(async () => {
                try {
                    const resp = await fetch(`/clientes/buscar?q=${encodeURIComponent(query)}`);
                    const data = await resp.json();
                    
                    buscarClienteDropdown.innerHTML = '';
                    if (data.length === 0) {
                        const div = document.createElement('div');
                        div.className = 'p-3 text-xs text-zinc-500 italic text-center';
                        div.textContent = 'No se encontraron clientes';
                        buscarClienteDropdown.appendChild(div);
                    } else {
                        data.forEach(c => {
                            const btn = document.createElement('button');
                            btn.type = 'button';
                            btn.className = 'w-full text-left p-3 text-xs hover:bg-zinc-100 transition-colors flex flex-col gap-0.5';
                            btn.innerHTML = `<span class="font-bold text-zinc-800">${c.nombre} ${c.apellido}</span><span class="text-[10px] text-zinc-400 font-label-mono">DNI/CUIL: ${c.dni_cuil}</span>`;
                            btn.addEventListener('click', () => {
                                buscarClienteInput.value = `${c.nombre} ${c.apellido} (${c.dni_cuil})`;
                                selectCliente.value = c.id;
                                selectCliente.dispatchEvent(new Event('change'));
                                buscarClienteDropdown.classList.add('hidden');
                                buscarClienteDropdown.innerHTML = '';
                            });
                            buscarClienteDropdown.appendChild(btn);
                        });
                    }
                    buscarClienteDropdown.classList.remove('hidden');
                } catch (err) {
                    console.error(err);
                }
            }, 250);
        });

        // Cerrar dropdown al hacer clic en cualquier parte fuera
        document.addEventListener('click', function(e) {
            if (!buscarClienteInput.contains(e.target) && !buscarClienteDropdown.contains(e.target)) {
                buscarClienteDropdown.classList.add('hidden');
            }
        });
    }

    // Validación antes de enviar orden de ingreso
    if (formOrden && selectEquipo) {
        formOrden.addEventListener('submit', function (e) {
            const equipo = selectEquipo.value;
            if (!equipo) {
                e.preventDefault();
                window.showToast('Por favor, seleccioná un equipo antes de registrar la orden.', 'error');
            }
        });
    }



    // Submit de registro rápido de equipo (removido)

    const modalRegistrarOrden = document.getElementById('modal-registrar-orden');
    if (modalRegistrarOrden) {
        modalRegistrarOrden.addEventListener('click', function (e) {
            if (e.target === this) cerrarModalRegistrarOrden();
        });
    }
});
