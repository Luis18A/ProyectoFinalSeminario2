/**
 * TechFlow Client Management Logic
 * Maneja modales de edición y búsqueda de clientes en tiempo real con debounce.
 */

// Lógica para el Modal de Editar
function abrirEditar(id, dni, nombre, apellido, telefono, email, domicilio, localidad) {
    const modal = document.getElementById('modal-editar');
    const form = document.getElementById('form-editar');

    form.action = `/clientes/editar/${id}`;

    document.getElementById('edit-dni').value = dni;
    document.getElementById('edit-nombre').value = nombre;
    document.getElementById('edit-apellido').value = apellido;
    document.getElementById('edit-telefono').value = telefono;
    document.getElementById('edit-email').value = email;
    document.getElementById('edit-domicilio').value = domicilio;
    document.getElementById('edit-localidad').value = localidad;

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function cerrarModal() {
    const modal = document.getElementById('modal-editar');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';
}

document.addEventListener('DOMContentLoaded', function () {
    const modalEditar = document.getElementById('modal-editar');
    if (modalEditar) {
        // Cerrar modal al hacer clic fuera del card
        modalEditar.addEventListener('click', function (e) {
            if (e.target === this) cerrarModal();
        });
    }

    // Lógica para el Buscador en Tiempo Real
    const searchInput = document.getElementById('search-input');
    const tbody = document.getElementById('clientes-table-body');
    let timeoutId;

    if (searchInput && tbody) {
        searchInput.addEventListener('input', function () {
            clearTimeout(timeoutId);
            const query = this.value.trim();

            timeoutId = setTimeout(() => {
                if (query.length > 0) {
                    fetch(`/clientes/buscar?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            renderClientes(data);
                        });
                } else {
                    // Si se borra la búsqueda, recargamos para ver todos
                    window.location.reload();
                }
            }, 300); // Debounce de 300ms
        });
    }

    function renderClientes(clientes) {
        tbody.innerHTML = '';
        if (clientes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="p-8 text-center text-on-surface-variant">No se encontraron resultados</td></tr>`;
            return;
        }

        clientes.forEach(c => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-background transition-colors';

            // Nos aseguramos de manejar nulos
            const emailStr = c.email ? c.email : '';
            const domicilioStr = c.domicilio ? c.domicilio : '';
            const localidadStr = c.localidad ? c.localidad : '';

            tr.innerHTML = `
                <td>
                    <div class="font-bold">${c.nombre} ${c.apellido}</div>
                    <div class="text-[10px] text-on-surface-variant font-label-mono uppercase">ID: #${String(c.id).padStart(3, '0')}</div>
                </td>
                <td>
                    <div class="text-sm">${c.telefono}</div>
                    <div class="text-[11px] text-on-surface-variant">${emailStr}</div>
                </td>
                <td class="font-label-mono text-xs">${c.dni_cuil}</td>
                <td class="text-right">
                    <div class="flex justify-end gap-2">
                        <a href="/equipos?cliente_id=${c.id}" class="p-2 text-on-surface-variant hover:text-accent transition-colors" title="Ver Equipos">
                            <span class="material-symbols-outlined text-[18px]">devices</span>
                        </a>
                        <button onclick="abrirEditar('${c.id}', '${c.dni_cuil}', '${c.nombre}', '${c.apellido}', '${c.telefono}', '${emailStr}', '${domicilioStr}', '${localidadStr}')" class="p-2 text-on-surface-variant hover:text-primary transition-colors" title="Editar">
                            <span class="material-symbols-outlined text-[18px]">edit</span>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
});
