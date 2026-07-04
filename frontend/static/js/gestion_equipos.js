/**
 * TechFlow Equipment Management & Spare Parts Logic
 * Maneja el modal de edición de equipos y el buscador de ofertas de repuestos (FastAPI).
 */

// Lógica para el Modal de Registrar Equipo
function abrirModalRegistrarEquipo() {
    const modal = document.getElementById('modal-registrar-equipo');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function cerrarModalRegistrarEquipo() {
    const modal = document.getElementById('modal-registrar-equipo');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('form-registrar-equipo').reset();
    }
    document.body.style.overflow = 'auto';
}

// Lógica para el Modal de Nuevo Tipo
function abrirModalNuevoTipo() {
    const modal = document.getElementById('modal-nuevo-tipo');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function cerrarModalNuevoTipo() {
    const modal = document.getElementById('modal-nuevo-tipo');
    if (modal) {
        modal.classList.add('hidden');
        document.getElementById('form-nuevo-tipo').reset();
    }
}

function escapeHTML(str) {
    if (!str) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Lógica para el Modal de Editar Equipo (Globales para invocación inline)
function abrirEditar(id, tipo_id, marca, modelo, serie, descripcion) {
    const modal = document.getElementById('modal-editar-equipo');
    const form = document.getElementById('form-editar-equipo');

    // Configurar la acción del formulario
    form.action = `/equipo/editar/${id}`;

    // Cargar datos en los inputs
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-tipo').value = tipo_id;
    document.getElementById('edit-marca').value = marca;
    document.getElementById('edit-modelo').value = modelo;
    document.getElementById('edit-serie').value = serie;
    document.getElementById('edit-descripcion').value = descripcion;

    // Mostrar modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function cerrarModal() {
    const modal = document.getElementById('modal-editar-equipo');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';
}

function mostrarOrdenesEquipo(equipoId, equipoNombre) {
    const modal = document.getElementById('modal-ver-ordenes');
    const title = document.getElementById('modal-equipo-nombre');
    const content = document.getElementById('modal-ordenes-contenido');
    const source = document.getElementById(`ordenes-equipo-${equipoId}`);

    if (modal && title && content && source) {
        title.textContent = equipoNombre;
        content.innerHTML = source.innerHTML;
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function cerrarModalOrdenes() {
    const modal = document.getElementById('modal-ver-ordenes');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';
}

document.addEventListener('DOMContentLoaded', function () {
    // === VALIDACIONES PREMIUM DE ENTRADA Y FORMULARIOS DE EQUIPOS ===

    const restringirEntrada = (input, regex) => {
        if (!input) return;
        input.addEventListener('input', function() {
            const start = this.selectionStart;
            const end = this.selectionEnd;
            const originalVal = this.value;
            const newVal = originalVal.replace(regex, '');
            
            if (originalVal !== newVal) {
                this.value = newVal;
                this.setSelectionRange(start - (originalVal.length - newVal.length), end - (originalVal.length - newVal.length));
            }
        });
    };

    // Filtros de caracteres en tiempo real
    const brandModelRegex = /[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\-\.\+\/()"]/g;
    restringirEntrada(document.getElementById('marca'), brandModelRegex);
    restringirEntrada(document.getElementById('edit-marca'), brandModelRegex);
    restringirEntrada(document.getElementById('modelo'), brandModelRegex);
    restringirEntrada(document.getElementById('edit-modelo'), brandModelRegex);

    const serialRegex = /[^a-zA-Z0-9\s\-\.\/_]/g;
    restringirEntrada(document.getElementById('numero_serie'), serialRegex);
    restringirEntrada(document.getElementById('edit-serie'), serialRegex);

    const descRegex = /[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s'",\.\-\+\/()#\?!:;*%=\$@&º°_]/g;
    restringirEntrada(document.getElementById('descripcion'), descRegex);
    restringirEntrada(document.getElementById('edit-descripcion'), descRegex);

    // Función de validación sincronizada
    const validarFormularioEquipo = (datos) => {
        const marca = datos.marca.trim();
        const modelo = datos.modelo.trim();
        const serie = datos.serie.trim();
        const descripcion = datos.descripcion ? datos.descripcion.trim() : "";

        if (!marca) return "La marca es obligatoria.";
        if (marca.length > 80) return "La marca no puede tener más de 80 caracteres.";
        const brandModelPattern = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ][a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\-\.\+\/()"]*$/;
        if (!brandModelPattern.test(marca)) return "La marca contiene caracteres no permitidos o no comienza con una letra o número.";
        if (!/[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ]/.test(marca)) return "La marca debe contener al menos una letra o número.";

        if (!modelo) return "El modelo es obligatorio.";
        if (modelo.length > 80) return "El modelo no puede tener más de 80 caracteres.";
        if (!brandModelPattern.test(modelo)) return "El modelo contiene caracteres no permitidos o no comienza con una letra o número.";
        if (!/[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ]/.test(modelo)) return "El modelo debe contener al menos una letra o número.";

        if (!serie) return "El número de serie es obligatorio.";
        if (serie.length > 80) return "El número de serie no puede tener más de 80 caracteres.";
        const serialPattern = /^[a-zA-Z0-9][a-zA-Z0-9\s\-\.\/_]*$/;
        if (!serialPattern.test(serie)) return "El número de serie contiene caracteres no permitidos o no comienza con una letra o número.";
        if (!/[a-zA-Z0-9]/.test(serie)) return "El número de serie debe contener al menos una letra o número.";

        if (descripcion) {
            if (descripcion.length > 500) return "La descripción no puede tener más de 500 caracteres.";
            const descPattern = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s'",\.\-\+\/()#\?!:;*%=\$@&º°_]+$/;
            if (!descPattern.test(descripcion)) return "La descripción contiene caracteres no permitidos.";
        }

        return null;
    };

    // Validar Formulario de Registro al enviar
    const formCreacion = document.getElementById('form-registrar-equipo');
    if (formCreacion) {
        formCreacion.addEventListener('submit', function (e) {
            const datos = {
                marca: document.getElementById('marca').value,
                modelo: document.getElementById('modelo').value,
                serie: document.getElementById('numero_serie').value,
                descripcion: document.getElementById('descripcion').value
            };

            const error = validarFormularioEquipo(datos);
            if (error) {
                e.preventDefault();
                if (window.showToast) {
                    window.showToast(error, 'error');
                } else {
                    alert(error);
                }
            }
        });
    }

    // Validar Formulario de Edición al enviar
    const formEdicion = document.getElementById('form-editar-equipo');
    if (formEdicion) {
        formEdicion.addEventListener('submit', function (e) {
            const datos = {
                marca: document.getElementById('edit-marca').value,
                modelo: document.getElementById('edit-modelo').value,
                serie: document.getElementById('edit-serie').value,
                descripcion: document.getElementById('edit-descripcion').value
            };

            const error = validarFormularioEquipo(datos);
            if (error) {
                e.preventDefault();
                if (window.showToast) {
                    window.showToast(error, 'error');
                } else {
                    alert(error);
                }
            }
        });
    }

    // Listener seguro para ver órdenes de un equipo
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-ver-ordenes-equipo');
        if (btn) {
            const id = btn.getAttribute('data-id');
            const nombre = btn.getAttribute('data-nombre');
            mostrarOrdenesEquipo(id, nombre);
        }
    });

    // Listener seguro para editar un equipo
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-editar-equipo');
        if (btn) {
            const id = btn.getAttribute('data-id');
            const tipoId = btn.getAttribute('data-tipo-id');
            const marca = btn.getAttribute('data-marca');
            const modelo = btn.getAttribute('data-modelo');
            const serie = btn.getAttribute('data-serie');
            const descripcion = btn.getAttribute('data-descripcion');
            abrirEditar(id, tipoId, marca, modelo, serie, descripcion);
        }
    });
    // Cerrar modal de Registrar Equipo al hacer clic fuera
    const modalRegistrar = document.getElementById('modal-registrar-equipo');
    if (modalRegistrar) {
        modalRegistrar.addEventListener('click', function (e) {
            if (e.target === this) cerrarModalRegistrarEquipo();
        });
    }

    // Cerrar modal de Nuevo Tipo al hacer clic fuera
    const modalNuevoTipo = document.getElementById('modal-nuevo-tipo');
    if (modalNuevoTipo) {
        modalNuevoTipo.addEventListener('click', function (e) {
            if (e.target === this) cerrarModalNuevoTipo();
        });
    }

    // Submit de registro de nuevo tipo de equipo via AJAX
    const formNuevoTipo = document.getElementById('form-nuevo-tipo');
    const selectTipoDispositivo = document.getElementById('select-tipo-dispositivo');
    const editTipoDispositivo = document.getElementById('edit-tipo');

    if (formNuevoTipo && selectTipoDispositivo) {
        formNuevoTipo.addEventListener('submit', async function (e) {
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
                    
                    // Agregar y seleccionar la nueva opción en el selector del modal de registro
                    const opt1 = document.createElement('option');
                    opt1.value = data.tipo.id;
                    opt1.textContent = data.tipo.descripcion;
                    selectTipoDispositivo.appendChild(opt1);
                    selectTipoDispositivo.value = data.tipo.id;
                    
                    // También agregarlo al selector del modal de edición por consistencia
                    if (editTipoDispositivo) {
                        const opt2 = document.createElement('option');
                        opt2.value = data.tipo.id;
                        opt2.textContent = data.tipo.descripcion;
                        editTipoDispositivo.appendChild(opt2);
                    }

                    cerrarModalNuevoTipo();
                } else {
                    window.showToast('Error al registrar el tipo: ' + data.message, 'error');
                }
            } catch (err) {
                console.error(err);
                window.showToast('Ocurrió un error al registrar el tipo de dispositivo.', 'error');
            }
        });
    }

    // Cerrar modal al hacer clic fuera
    const modalEditar = document.getElementById('modal-editar-equipo');
    if (modalEditar) {
        modalEditar.addEventListener('click', function (e) {
            if (e.target === this) cerrarModal();
        });
    }

    // Cerrar modal de órdenes al hacer clic fuera
    const modalOrdenes = document.getElementById('modal-ver-ordenes');
    if (modalOrdenes) {
        modalOrdenes.addEventListener('click', function (e) {
            if (e.target === this) cerrarModalOrdenes();
        });
    }

    // Lógica para el Buscador de Repuestos (FastAPI microservice on port 8000)
    const searchInput = document.getElementById('ml-search-input');
    const searchBtn = document.getElementById('ml-search-btn');
    const loading = document.getElementById('ml-loading');
    const resultsContainer = document.getElementById('ml-results-container');
    const resultsBody = document.getElementById('ml-results-body');
    const noResults = document.getElementById('ml-no-results');

    function formatCurrency(amount) {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS',
            maximumFractionDigits: 0
        }).format(amount);
    }

    async function buscarRepuestos() {
        const query = searchInput.value.trim();
        if (!query) return;

        loading.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        noResults.classList.add('hidden');
        resultsBody.innerHTML = '';

        try {
            // 1. Iniciar la tarea en segundo plano en el servidor
            const startResp = await fetch('/api/buscar-repuestos/iniciar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                },
                body: JSON.stringify({ q: query })
            });

            if (!startResp.ok) {
                const errData = await startResp.json().catch(() => ({}));
                throw new Error(errData.error || 'No se pudo iniciar la búsqueda');
            }

            const { task_id } = await startResp.json();

            // 2. Función de sondeo (polling)
            const pollTask = async () => {
                try {
                    const statusResp = await fetch(`/api/buscar-repuestos/estado/${task_id}`);
                    if (!statusResp.ok) {
                        throw new Error('Error al consultar el estado de la búsqueda');
                    }

                    const statusData = await statusResp.json();

                    if (statusData.status === 'completed') {
                        loading.classList.add('hidden');
                        const data = statusData.results || [];
                        if (data.length === 0) {
                            noResults.textContent = "No se encontraron repuestos para tu búsqueda.";
                            noResults.classList.remove('hidden');
                        } else {
                            data.forEach(item => {
                                const tr = document.createElement('tr');
                                tr.className = 'hover:bg-background transition-colors';

                                let tiendaHtml = '';
                                if (item.tienda === 'MercadoLibre') {
                                    tiendaHtml = `<span class="px-2 py-1 bg-yellow-100 text-yellow-800 border border-yellow-200 font-label-bold text-[10px] uppercase tracking-wider text-center flex items-center justify-center">Mercado Libre</span>`;
                                } else if (item.tienda === 'Megatone') {
                                    tiendaHtml = `<span class="px-2 py-1 bg-red-100 text-red-800 border border-red-200 font-label-bold text-[10px] uppercase tracking-wider text-center flex items-center justify-center">Megatone</span>`;
                                } else if (item.tienda === 'Fravega') {
                                    tiendaHtml = `<span class="px-2 py-1 bg-purple-100 text-purple-800 border border-purple-200 font-label-bold text-[10px] uppercase tracking-wider text-center flex items-center justify-center">Fravega</span>`;
                                } else {
                                    tiendaHtml = `<span class="px-2 py-1 bg-gray-100 text-gray-800 border border-gray-200 font-label-bold text-[10px] uppercase tracking-wider text-center flex items-center justify-center">${item.tienda}</span>`;
                                }

                                let condicionText = item.condicion === 'new' ? 'Nuevo' : (item.condicion === 'used' ? 'Usado' : item.condicion);

                                tr.innerHTML = `
                                    <td>${tiendaHtml}</td>
                                    <td class="text-sm text-primary max-w-xs truncate" title="${escapeHTML(item.titulo)}">${escapeHTML(item.titulo)}</td>
                                    <td class="text-xs text-on-surface-variant uppercase">${escapeHTML(condicionText)}</td>
                                    <td class="text-right font-label-mono font-bold text-accent">${formatCurrency(item.precio)}</td>
                                    <td class="text-center">
                                        <a href="${escapeHTML(item.link)}" target="_blank" class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-zinc-100 hover:bg-secondary hover:text-white transition-colors text-primary mx-auto" title="Ver publicación">
                                            <span class="material-symbols-outlined text-[18px]">open_in_new</span>
                                        </a>
                                    </td>
                                `;
                                resultsBody.appendChild(tr);
                            });
                            resultsContainer.classList.remove('hidden');
                        }
                    } else if (statusData.status === 'running') {
                        // Reintentar en 1.5 segundos
                        setTimeout(pollTask, 1500);
                    } else {
                        throw new Error(statusData.error || 'La tarea falló');
                    }
                } catch (pollErr) {
                    console.error(pollErr);
                    loading.classList.add('hidden');
                    noResults.textContent = "Error al sondear el resultado de búsqueda: " + pollErr.message;
                    noResults.classList.remove('hidden');
                }
            };

            // Iniciar sondeo inicial
            setTimeout(pollTask, 500);

        } catch (error) {
            console.error('Error al buscar repuestos:', error);
            loading.classList.add('hidden');
            noResults.textContent = "Ocurrió un error al buscar los repuestos. Verifica la cola Celery.";
            noResults.classList.remove('hidden');
        }
    }

    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', buscarRepuestos);
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                buscarRepuestos();
            }
        });
    }
});
