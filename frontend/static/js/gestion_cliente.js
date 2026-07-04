/**
 * TechFlow Client Management Logic
 * Maneja modales de edición y búsqueda de clientes en tiempo real con de-bounce.
 */

function escapeHTML(str) {
    if (!str) return '';
    return str.toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Lógica para el Modal de Registrar
function abrirModalRegistrar() {
    const modal = document.getElementById('modal-registrar');
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function cerrarModalRegistrar() {
    const modal = document.getElementById('modal-registrar');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = 'auto';
}

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
    // Capturador seguro de clics para editar clientes (elimina onclick inline)
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.btn-editar-cliente');
        if (btn) {
            const id = btn.getAttribute('data-id');
            const dni = btn.getAttribute('data-dni');
            const nombre = btn.getAttribute('data-nombre');
            const apellido = btn.getAttribute('data-apellido');
            const telefono = btn.getAttribute('data-telefono');
            const email = btn.getAttribute('data-email');
            const domicilio = btn.getAttribute('data-domicilio');
            const localidad = btn.getAttribute('data-localidad');
            
            abrirEditar(id, dni, nombre, apellido, telefono, email, domicilio, localidad);
        }
    });

    // === VALIDACIONES PREMIUM DE ENTRADA Y FORMULARIOS ===

    // Input Helpers para filtrar caracteres no válidos en tiempo real
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

    // Restricción de caracteres en tiempo real
    restringirEntrada(document.getElementById('dni'), /[^0-9\s-]/g);
    restringirEntrada(document.getElementById('edit-dni'), /[^0-9\s-]/g);
    
    const telRegex = /[^0-9\s+-]/g;
    restringirEntrada(document.getElementById('telefono'), telRegex);
    restringirEntrada(document.getElementById('edit-telefono'), telRegex);
    
    // Permitir letras, espacios, apóstrofes y guiones (nombres/apellidos compuestos o localidad)
    const letterRegex = /[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]/g;
    restringirEntrada(document.getElementById('nombre'), letterRegex);
    restringirEntrada(document.getElementById('apellido'), letterRegex);
    restringirEntrada(document.getElementById('edit-nombre'), letterRegex);
    restringirEntrada(document.getElementById('edit-apellido'), letterRegex);

    // Permitir letras, espacios, apóstrofes, guiones y puntos en la localidad
    const localityRegex = /[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\.-]/g;
    restringirEntrada(document.getElementById('localidad'), localityRegex);
    restringirEntrada(document.getElementById('edit-localidad'), localityRegex);

    // Permitir letras, números, espacios, comillas, comas, puntos, guiones, barras, paréntesis y numerales en el domicilio
    const domRegex = /[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s'",\.\-°ºª\/()#]/g;
    restringirEntrada(document.getElementById('domicilio'), domRegex);
    restringirEntrada(document.getElementById('edit-domicilio'), domRegex);

    // Algoritmo matemático para validar CUIT/CUIL argentino
    const validarCuitCuil = (cuit) => {
        if (cuit.length !== 11 || !/^\d+$/.test(cuit)) return false;
        const multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
        let total = 0;
        for (let i = 0; i < 10; i++) {
            total += parseInt(cuit[i]) * multipliers[i];
        }
        const remainder = total % 11;
        let calculated = 11 - remainder;
        
        if (calculated === 11) {
            calculated = 0;
        } else if (calculated === 10) {
            calculated = 9;
        }
        
        const provided = parseInt(cuit[10]);
        if (calculated === 9) {
            return provided === 9 || provided === 4;
        }
        return provided === calculated;
    };

    // Función global de validación sincronizada
    const validarFormularioCliente = (datos) => {
        const nombre = datos.nombre.trim();
        const apellido = datos.apellido.trim();
        const telefono = datos.telefono.trim();
        const email = datos.email.trim();
        const domicilio = datos.domicilio.trim();
        const localidad = datos.localidad.trim();

        // 1. Nombre y Apellido
        if (nombre.length < 2) {
            return "El nombre debe tener al menos 2 caracteres.";
        }
        if (nombre.length > 50) {
            return "El nombre es demasiado largo (máximo 50 caracteres).";
        }
        if (apellido.length < 2) {
            return "El apellido debe tener al menos 2 caracteres.";
        }
        if (apellido.length > 50) {
            return "El apellido es demasiado largo (máximo 50 caracteres).";
        }

        const letterPattern = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$/;
        if (!letterPattern.test(nombre)) {
            return "El nombre solo debe contener letras, espacios o guiones.";
        }
        if (!letterPattern.test(apellido)) {
            return "El apellido solo debe contener letras, espacios o guiones.";
        }
        
        // 2. DNI / CUIL
        if (datos.dni !== undefined) {
            const dni = datos.dni.trim();
            const cleanDni = dni.replace(/[- ]/g, '');
            if (!cleanDni) {
                return "El DNI/CUIL es obligatorio.";
            }
            if (cleanDni.length !== 7 && cleanDni.length !== 8 && cleanDni.length !== 11) {
                return "El DNI/CUIL debe contener exactamente 7, 8 u 11 números.";
            }
            if (cleanDni.length === 11 && !validarCuitCuil(cleanDni)) {
                return "El número de CUIL/CUIT no es válido. El dígito verificador es incorrecto.";
            }
        }

        // 3. Teléfono
        if (!telefono) {
            return "El teléfono es obligatorio.";
        }
        if (telefono.length > 30) {
            return "El teléfono es demasiado largo.";
        }
        const cleanTel = telefono.replace(/[-+ ]/g, '');
        if (cleanTel.length < 8 || cleanTel.length > 15) {
            return "El teléfono debe contener entre 8 y 15 dígitos numéricos netos.";
        }

        // 4. Email
        if (email) {
            if (email.length > 254) {
                return "El correo electrónico es demasiado largo (máximo 254 caracteres).";
            }
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(email)) {
                return "El formato del correo electrónico no es válido (ej. correo@ejemplo.com).";
            }
        }

        // 5. Domicilio
        if (domicilio.length < 3) {
            return "El domicilio debe tener al menos 3 caracteres.";
        }
        if (domicilio.length > 150) {
            return "El domicilio es demasiado largo (máximo 150 caracteres).";
        }
        const addressPattern = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s'",\.\-°ºª/()#]+$/;
        if (!addressPattern.test(domicilio)) {
            return "El domicilio contiene caracteres no permitidos.";
        }
        if (!/[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ]/.test(domicilio)) {
            return "El domicilio es inválido (debe contener letras o números).";
        }

        // 6. Localidad
        if (localidad.length < 2) {
            return "La localidad debe tener al menos 2 caracteres.";
        }
        if (localidad.length > 100) {
            return "La localidad es demasiado larga (máximo 100 caracteres).";
        }
        const localityPattern = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\.-]+$/;
        if (!localityPattern.test(localidad)) {
            return "La localidad solo debe contener letras, espacios, puntos, guiones o apóstrofes.";
        }

        return null; // Datos válidos
    };

    // Validar Formulario de Creación al enviar
    const formCreacion = document.querySelector('form[action="/clientes"]');
    if (formCreacion) {
        formCreacion.addEventListener('submit', function (e) {
            const datos = {
                dni: document.getElementById('dni').value,
                nombre: document.getElementById('nombre').value,
                apellido: document.getElementById('apellido').value,
                telefono: document.getElementById('telefono').value,
                email: document.getElementById('email').value,
                domicilio: document.getElementById('domicilio').value,
                localidad: document.getElementById('localidad').value
            };

            const error = validarFormularioCliente(datos);
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
    const formEdicion = document.getElementById('form-editar');
    if (formEdicion) {
        formEdicion.addEventListener('submit', function (e) {
            const datos = {
                nombre: document.getElementById('edit-nombre').value,
                apellido: document.getElementById('edit-apellido').value,
                telefono: document.getElementById('edit-telefono').value,
                email: document.getElementById('edit-email').value,
                domicilio: document.getElementById('edit-domicilio').value,
                localidad: document.getElementById('edit-localidad').value
            };

            const error = validarFormularioCliente(datos);
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

    const modalEditar = document.getElementById('modal-editar');
    if (modalEditar) {
        modalEditar.addEventListener('click', function (e) {
            if (e.target === this) cerrarModal();
        });
    }

    const modalRegistrar = document.getElementById('modal-registrar');
    if (modalRegistrar) {
        modalRegistrar.addEventListener('click', function (e) {
            if (e.target === this) cerrarModalRegistrar();
        });
    }

    // Validación y Autofill por DNI existente (Búsqueda en tiempo real)
    const dniInput = document.getElementById('dni');
    const submitBtn = formCreacion ? formCreacion.querySelector('button[type="submit"]') : null;
    const warningMsg = document.createElement('p');
    warningMsg.className = 'text-xs text-amber-600 mt-1 hidden font-medium';
    warningMsg.id = 'dni-warning-msg';
    
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
                    warningMsg.innerHTML = `⚠️ DNI ya registrado para <strong>${c.nombre} ${c.apellido}</strong>. <button type="button" class="text-accent underline font-bold ml-1 hover:text-[#0057FF]" id="btn-autofill-edit">Editar Cliente</button>`;
                    warningMsg.classList.remove('hidden');
                    
                    // Autofill
                    document.getElementById('nombre').value = c.nombre;
                    document.getElementById('apellido').value = c.apellido;
                    document.getElementById('telefono').value = c.telefono;
                    document.getElementById('email').value = c.email;
                    document.getElementById('domicilio').value = c.domicilio;
                    document.getElementById('localidad').value = c.localidad;
                    
                    // Block submit to avoid DB duplicate failure
                    if (submitBtn) submitBtn.disabled = true;
                    
                    document.getElementById('btn-autofill-edit').addEventListener('click', function() {
                        abrirEditar(c.id, c.dni_cuil, c.nombre, c.apellido, c.telefono, c.email, c.domicilio, c.localidad);
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

    // Lógica para el Buscador en Tiempo Real con sanitización y de-bounce
    const searchInput = document.getElementById('search-input');
    const tbody = document.getElementById('clientes-table-body');
    let timeoutId;

    if (searchInput && tbody) {
        searchInput.addEventListener('input', function () {
            clearTimeout(timeoutId);
            const query = this.value.trim();

            timeoutId = setTimeout(() => {
                if (query.length > 0) {
                    if (query.length > 100) {
                        tbody.innerHTML = `<tr><td colspan="4" class="p-8 text-center text-on-surface-variant">Búsqueda demasiado larga</td></tr>`;
                        return;
                    }
                    // Mostrar skeleton loader mientras se realiza la búsqueda
                    tbody.innerHTML = `
                        <tr class="skeleton-row">
                            <td>
                                <div class="skeleton-bar w-3/4"></div>
                                <div class="skeleton-bar-sm w-1/4"></div>
                            </td>
                            <td>
                                <div class="skeleton-bar w-1/2"></div>
                                <div class="skeleton-bar-sm w-1/3"></div>
                            </td>
                            <td>
                                <div class="skeleton-bar w-2/3"></div>
                            </td>
                            <td class="text-right">
                                <div class="flex justify-end gap-2">
                                    <div class="skeleton-circle"></div>
                                    <div class="skeleton-circle"></div>
                                </div>
                            </td>
                        </tr>
                    `;
                    fetch(`/clientes/buscar?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            renderClientes(data);
                        });
                } else {
                    window.location.reload();
                }
            }, 300);
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

            const emailStr = c.email ? c.email : '';
            const domicilioStr = c.domicilio ? c.domicilio : '';
            const localidadStr = c.localidad ? c.localidad : '';

            tr.innerHTML = `
                <td>
                    <div class="font-bold">${escapeHTML(c.nombre)} ${escapeHTML(c.apellido)}</div>
                    <div class="text-[10px] text-on-surface-variant font-label-mono uppercase">ID: #${String(c.id).padStart(3, '0')}</div>
                </td>
                <td>
                    <div class="text-sm">${escapeHTML(c.telefono)}</div>
                    <div class="text-[11px] text-on-surface-variant">${escapeHTML(emailStr)}</div>
                </td>
                <td class="font-label-mono text-xs">${escapeHTML(c.dni_cuil)}</td>
                <td class="text-right">
                    <div class="flex justify-end gap-2">
                        <a href="/equipos/${c.id}" class="p-2 text-on-surface-variant hover:text-accent transition-colors" title="Ver Equipos">
                            <span class="material-symbols-outlined text-[18px]">devices</span>
                        </a>
                        <button 
                            class="p-2 text-on-surface-variant hover:text-primary transition-colors btn-editar-cliente" 
                            data-id="${c.id}" 
                            data-dni="${escapeHTML(c.dni_cuil)}" 
                            data-nombre="${escapeHTML(c.nombre)}" 
                            data-apellido="${escapeHTML(c.apellido)}" 
                            data-telefono="${escapeHTML(c.telefono)}" 
                            data-email="${escapeHTML(emailStr)}" 
                            data-domicilio="${escapeHTML(domicilioStr)}" 
                            data-localidad="${escapeHTML(localidadStr)}"
                            title="Editar">
                            <span class="material-symbols-outlined text-[18px]">edit</span>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
});
