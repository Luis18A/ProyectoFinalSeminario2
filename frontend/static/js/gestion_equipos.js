/**
 * TechFlow Equipment Management & Spare Parts Logic
 * Maneja el modal de edición de equipos y el buscador de ofertas de repuestos (FastAPI).
 */

// Lógica para el Modal de Editar Equipo (Globales para invocación inline)
function abrirEditar(id, tipo_id, marca, modelo, serie, descripcion) {
    const modal = document.getElementById('modal-editar-equipo');
    const form = document.getElementById('form-editar-equipo');

    // Configurar la acción del formulario
    form.action = `/equipo/editar/${id}`;

    // Cargar datos en los inputs
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

document.addEventListener('DOMContentLoaded', function () {
    // Cerrar modal al hacer clic fuera
    const modalEditar = document.getElementById('modal-editar-equipo');
    if (modalEditar) {
        modalEditar.addEventListener('click', function (e) {
            if (e.target === this) cerrarModal();
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
            // Hacer petición al microservicio FastAPI en el puerto 8000
            const response = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`);

            if (!response.ok) {
                throw new Error('Error en el servidor de scraping');
            }

            const data = await response.json();

            if (data.length === 0) {
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
                        <td class="text-sm text-primary max-w-xs truncate" title="${item.titulo}">${item.titulo}</td>
                        <td class="text-xs text-on-surface-variant uppercase">${condicionText}</td>
                        <td class="text-right font-label-mono font-bold text-accent">${formatCurrency(item.precio)}</td>
                        <td class="text-center">
                            <a href="${item.link}" target="_blank" class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-zinc-100 hover:bg-secondary hover:text-white transition-colors text-primary mx-auto" title="Ver publicación">
                                <span class="material-symbols-outlined text-[18px]">open_in_new</span>
                            </a>
                        </td>
                    `;
                    resultsBody.appendChild(tr);
                });
                resultsContainer.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error al buscar repuestos:', error);
            noResults.textContent = "Ocurrió un error al buscar los repuestos. Verifica que el servidor de FastAPI esté encendido.";
            noResults.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
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
