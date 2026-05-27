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

// Funciones globales para control rápido de transiciones de estado
async function confirmarPresupuesto(ordenId, costo) {
    if (!confirm(`¿Confirmar que el cliente acepta el presupuesto de $${costo} y empezar reparación?`)) {
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('estado', 'REPARACION');
        formData.append('observaciones', 'Aprobado por el cliente por comunicación telefónica.');
        
        const resp = await fetch(`/ordenServicio/${ordenId}/actualizar-estado-flujo`, {
            method: 'POST',
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

async function entregarEquipo(ordenId) {
    if (!confirm('¿Registrar la entrega formal del equipo y cerrar el ciclo de la orden?')) {
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('estado', 'ENTREGADO');
        formData.append('observaciones', 'Equipo entregado formalmente al cliente. Ciclo de servicio finalizado.');
        
        const resp = await fetch(`/ordenServicio/${ordenId}/actualizar-estado-flujo`, {
            method: 'POST',
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
        window.showToast('Ocurrió un error al registrar la entrega.', 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const selectCliente = document.getElementById('select-cliente');
    const selectEquipo = document.getElementById('select-equipo');
    const equipoHint = document.getElementById('equipo-hint');
    const btnNuevoEquipo = document.getElementById('btn-nuevo-equipo-rapido');
    const formOrden = document.getElementById('form-orden');
    
    const formClienteRapido = document.getElementById('form-cliente-rapido');
    const formEquipoRapido = document.getElementById('form-equipo-rapido');

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
});
