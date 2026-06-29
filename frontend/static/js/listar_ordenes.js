/**
 * TechFlow Secretary View Logic
 * Maneja la carga dinámica de equipos, alta rápida de clientes y equipos con AJAX,
 * y cambios rápidos de estado del flujo de reparación.
 */

// Funciones globales para control de modales de alta rápida
function abrirCrearClienteRapido() {
    const modal = document.getElementById('modal-cliente-rapido');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function cerrarCrearClienteRapido() {
    const modal = document.getElementById('modal-cliente-rapido');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('form-cliente-rapido').reset();
    }
}

function abrirCrearEquipoRapido() {
    const selectCliente = document.getElementById('select-cliente');
    const modal = document.getElementById('modal-equipo-rapido');
    
    if (!selectCliente.value) {
        window.showToast('Por favor, selecciona un cliente primero.', 'error');
        return;
    }
    
    // Cargar datos del cliente en el modal
    document.getElementById('rapido-cliente-id').value = selectCliente.value;
    
    const selectedOption = selectCliente.options[selectCliente.selectedIndex];
    document.getElementById('rapido-cliente-nombre').textContent = selectedOption.textContent.trim();
    
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function cerrarCrearEquipoRapido() {
    const modal = document.getElementById('modal-equipo-rapido');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('form-equipo-rapido').reset();
    }
}

function abrirCrearTipoDispositivoRapido() {
    const modal = document.getElementById('modal-tipo-dispositivo-rapido');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function cerrarCrearTipoDispositivoRapido() {
    const modal = document.getElementById('modal-tipo-dispositivo-rapido');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('form-tipo-dispositivo-rapido').reset();
    }
}

// Las transiciones rápidas de estado (confirmarPresupuesto, rechazarPresupuesto, entregarEquipo) ahora son globales y residen en app.js

document.addEventListener('DOMContentLoaded', () => {
    const selectCliente = document.getElementById('select-cliente');
    const selectEquipo = document.getElementById('select-equipo');
    const equipoHint = document.getElementById('equipo-hint');
    const btnNuevoEquipo = document.getElementById('btn-nuevo-equipo-rapido');
    const formOrden = document.getElementById('form-orden');
    
    const formClienteRapido = document.getElementById('form-cliente-rapido');
    const formEquipoRapido = document.getElementById('form-equipo-rapido');

    // Validación y atajo de DNI existente en el modal rápido
    if (formClienteRapido) {
        const dniInput = formClienteRapido.querySelector('input[name="dni"]');
        const submitBtn = formClienteRapido.querySelector('button[type="submit"]');
        const warningMsg = document.createElement('p');
        warningMsg.className = 'text-xs text-amber-600 mt-1 hidden font-medium';
        warningMsg.id = 'dni-rapido-warning-msg';
        
        if (dniInput) {
            dniInput.parentNode.appendChild(warningMsg);
            
            dniInput.addEventListener('blur', async function() {
                const dni = this.value.trim().replace(/[- ]/g, '');
                if (dni.length !== 7 && dni.length !== 8 && dni.length !== 11) {
                    warningMsg.classList.add('hidden');
                    if (submitBtn) submitBtn.disabled = false;
                    return;
                }
                
                try {
                    const resp = await fetch(`/clientes/verificar-dni/${dni}`);
                    const data = await resp.json();
                    
                    if (data.exists) {
                        const c = data.cliente;
                        warningMsg.innerHTML = `⚠️ DNI ya registrado para <strong>${c.nombre} ${c.apellido}</strong>. <button type="button" class="text-accent underline font-bold ml-1 hover:text-[#0057FF]" id="btn-select-existing-client">Seleccionar Cliente</button>`;
                        warningMsg.classList.remove('hidden');
                        
                        // Autofill other fields
                        formClienteRapido.querySelector('input[name="nombre"]').value = c.nombre;
                        formClienteRapido.querySelector('input[name="apellido"]').value = c.apellido;
                        formClienteRapido.querySelector('input[name="telefono"]').value = c.telefono;
                        formClienteRapido.querySelector('input[name="email"]').value = c.email;
                        formClienteRapido.querySelector('input[name="domicilio"]').value = c.domicilio;
                        formClienteRapido.querySelector('input[name="localidad"]').value = c.localidad;
                        
                        // Block submit button
                        if (submitBtn) submitBtn.disabled = true;
                        
                        // Bind select existing client handler
                        document.getElementById('btn-select-existing-client').addEventListener('click', function() {
                            let optionExists = false;
                            for (let i = 0; i < selectCliente.options.length; i++) {
                                if (selectCliente.options[i].value == c.id) {
                                    optionExists = true;
                                    break;
                                }
                            }
                            
                            if (!optionExists) {
                                const opt = document.createElement('option');
                                opt.value = c.id;
                                opt.textContent = `${c.nombre} ${c.apellido} (${c.dni_cuil})`;
                                selectCliente.appendChild(opt);
                            }
                            
                            selectCliente.value = c.id;
                            cerrarCrearClienteRapido();
                            // Load equipment
                            cargarEquiposCliente(c.id);
                            window.showToast(`Cliente '${c.nombre} ${c.apellido}' seleccionado correctamente.`, 'success');
                        });
                    } else {
                        warningMsg.classList.add('hidden');
                        if (submitBtn) submitBtn.disabled = false;
                    }
                } catch (err) {
                    console.error(err);
                }
            });
            
            dniInput.addEventListener('input', function() {
                warningMsg.classList.add('hidden');
                if (submitBtn) submitBtn.disabled = false;
            });
        }
    }

    // Función auxiliar para cargar equipos de un cliente seleccionado
    async function cargarEquiposCliente(clienteId) {
        selectEquipo.innerHTML = '<option value="">— Cargando equipos... —</option>';
        selectEquipo.disabled = true;
        btnNuevoEquipo.disabled = true;
        btnNuevoEquipo.classList.add('opacity-40');
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
            // Habilitar botón de agregar equipo para el cliente
            btnNuevoEquipo.disabled = false;
            btnNuevoEquipo.classList.remove('opacity-40');
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

    // Submit de registro rápido de cliente
    if (formClienteRapido) {
        formClienteRapido.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            try {
                const resp = await fetch('/clientes/rapido', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                    },
                    body: formData
                });
                
                const data = await resp.json();
                if (data.success) {
                    window.showToast('Cliente registrado con éxito en segundo plano.', 'success');
                    
                    // Añadir nueva opción al select principal de clientes
                    const opt = document.createElement('option');
                    opt.value = data.cliente.id;
                    opt.textContent = `${data.cliente.nombre} ${data.cliente.apellido} (${data.cliente.dni_cuil})`;
                    selectCliente.appendChild(opt);
                    
                    // Seleccionar el cliente creado
                    selectCliente.value = data.cliente.id;
                    
                    // Cerrar el modal y disparar la carga de equipos (que estará vacía para este nuevo cliente)
                    cerrarCrearClienteRapido();
                    cargarEquiposCliente(data.cliente.id);
                } else {
                    window.showToast('Error al registrar cliente: ' + data.message, 'error');
                }
            } catch (err) {
                console.error(err);
                window.showToast('Ocurrió un error al registrar el cliente.', 'error');
            }
        });
    }

    // Submit de registro rápido de equipo
    if (formEquipoRapido) {
        formEquipoRapido.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            try {
                const resp = await fetch('/equipo/rapido', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                    },
                    body: formData
                });
                
                const data = await resp.json();
                if (data.success) {
                    window.showToast('Dispositivo registrado con éxito.', 'success');
                    
                    // Si el selector no estaba habilitado, habilitarlo ahora
                    selectEquipo.disabled = false;
                    
                    // Si la única opción era de "Sin equipos registrados", limpiamos
                    if (selectEquipo.options.length <= 1 && (selectEquipo.value === "" || selectEquipo.options[0].textContent.includes("Sin equipos"))) {
                        selectEquipo.innerHTML = '';
                    }
                    
                    // Agregar y seleccionar la nueva opción
                    const opt = document.createElement('option');
                    opt.value = data.equipo.id;
                    opt.textContent = data.equipo.label;
                    selectEquipo.appendChild(opt);
                    selectEquipo.value = data.equipo.id;
                    
                    // Esconder advertencia
                    equipoHint.classList.add('hidden');
                    
                    cerrarCrearEquipoRapido();
                } else {
                    window.showToast('Error al registrar equipo: ' + data.message, 'error');
                }
            } catch (err) {
                console.error(err);
                window.showToast('Ocurrió un error al registrar el equipo.', 'error');
            }
        });
    }

    const formTipoDispositivoRapido = document.getElementById('form-tipo-dispositivo-rapido');
    const selectTipoDispositivo = document.getElementById('rapido-select-tipo');

    if (formTipoDispositivoRapido && selectTipoDispositivo) {
        formTipoDispositivoRapido.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            try {
                const resp = await fetch('/tipoDispositivo/rapido', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                    },
                    body: formData
                });
                
                const data = await resp.json();
                if (data.success) {
                    window.showToast('Tipo de dispositivo registrado con éxito.', 'success');
                    
                    // Agregar y seleccionar la nueva opción en el modal de equipo
                    const opt = document.createElement('option');
                    opt.value = data.tipo.id;
                    opt.textContent = data.tipo.descripcion;
                    selectTipoDispositivo.appendChild(opt);
                    selectTipoDispositivo.value = data.tipo.id;
                    
                    cerrarCrearTipoDispositivoRapido();
                } else {
                    window.showToast('Error al registrar el tipo: ' + data.message, 'error');
                }
            } catch (err) {
                console.error(err);
                window.showToast('Ocurrió un error al registrar el tipo de dispositivo.', 'error');
            }
        });
    }
});
