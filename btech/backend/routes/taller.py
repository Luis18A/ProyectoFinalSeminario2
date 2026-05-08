from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
# Importamos el controlador (el cerebro)
from backend.controllers import taller_controller
from flask import abort
from backend.utils.decorators import role_required

taller_bp = Blueprint('taller', __name__)

@taller_bp.route('/tickets')
@login_required
@role_required('Administrador', 'Secretaria', 'Tecnico')
def tickets():
    ordenes = taller_controller.obtener_todos_los_tickets()
    estados = taller_controller.obtener_estados_disponibles()
    
    # CORREGIDO: Ahora leemos el '.value' del Enum y usamos los textos exactos de tu estado_orden.py
    resumen = {
        'pendientes': len([o for o in ordenes if o.estado and o.estado.value == 'Pendiente']),
        'en_reparacion': len([o for o in ordenes if o.estado and o.estado.value == 'Reparacion']),
        'listos': len([o for o in ordenes if o.estado and o.estado.value == 'Listo'])
    }
    
    return render_template('taller/tickets.html', ordenes=ordenes, estados=estados, resumen=resumen)

@taller_bp.route('/equipo/<int:equipo_id>/nuevo_ticket', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Secretaria')
def nuevo_ticket(equipo_id):
    if request.method == 'POST':
        falla = request.form.get('falla')
        accesorios = request.form.get('accesorios')
        
        # Le pasamos los datos al controlador
        exito, resultado = taller_controller.crear_ticket(
            equipo_id=equipo_id,
            usuario_id=current_user.id,
            falla=falla,
            accesorios=accesorios
        )
        
        if exito:
            flash(f'Ticket #{resultado} generado correctamente.', 'success')
            return redirect(url_for('taller.tickets'))
        else:
            flash(resultado, 'danger')
            
    # Si es GET, buscamos el equipo para mostrarlo en el formulario
    equipo = taller_controller.obtener_equipo_por_id(equipo_id)
    return render_template('taller/nuevo_ticket.html', equipo=equipo)

@taller_bp.route('/ticket/<int:orden_id>/gestionar', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Tecnico')
def gestionar_ticket(orden_id):
    if request.method == 'POST':
        # CORREGIDO: Cambiamos 'estado_id' por 'estado' ya que recibimos el nombre del Enum (Ej: "REPARACION")
        nuevo_estado = request.form.get('estado')
        observacion = request.form.get('observacion_tecnica')
        costo = request.form.get('costo_total')
        
        # El controlador hace toda la validación y el registro de auditoría
        taller_controller.actualizar_ticket(
            orden_id=orden_id,
            usuario_id=current_user.id,
            nuevo_estado_id=nuevo_estado, # Mantenemos el nombre del argumento para no tocar el controlador de nuevo
            observacion=observacion,
            costo=costo
        )
        flash('Ticket actualizado correctamente.', 'success')
        return redirect(url_for('taller.gestionar_ticket', orden_id=orden_id))
        
    # Petición GET: Traemos los datos para dibujar la pantalla
    orden = taller_controller.obtener_ticket_por_id(orden_id)
    estados = taller_controller.obtener_estados_disponibles()
    historial = taller_controller.obtener_historial_ticket(orden_id)
    
    return render_template('taller/gestionar_ticket.html', orden=orden, historial=historial, estados=estados)

@taller_bp.route('/ticket/<int:orden_id>/comprobante')
@login_required
@role_required('Administrador', 'Secretaria', 'Tecnico')
def comprobante_ticket(orden_id):
    orden = taller_controller.obtener_ticket_por_id(orden_id)
    return render_template('taller/comprobante.html', orden=orden)

@taller_bp.route('/tickets/historial')
@login_required
@role_required('Administrador', 'Secretaria', 'Tecnico')
def historial_tickets():
    ordenes = taller_controller.obtener_todos_los_tickets() 
    return render_template('taller/historial_tickets.html', ordenes=ordenes)