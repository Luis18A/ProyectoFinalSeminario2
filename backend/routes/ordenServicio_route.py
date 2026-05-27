from backend.controller.ordenServicio_controller import OrdenServicioController
from flask import Blueprint, request, render_template, url_for, flash, redirect, jsonify
from backend.utils.decorators import login_required

ordenServicio_bp = Blueprint('ordenServicio', __name__)

@ordenServicio_bp.post('/ordenServicio')
@login_required
def crear_ordenServicio():
    success, message = OrdenServicioController.crear_ordenServicio(request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('usuarios.secretary'))

@ordenServicio_bp.post('/ordenServicio/editar/<int:id>')
@login_required
def editar_ordenServicio(id):
    success, message = OrdenServicioController.actualizar_ordenServicio(id, request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('usuarios.secretary'))

@ordenServicio_bp.get('/ordenServicio/historial/<int:orden_id>')
@login_required
def historial_ordenServicio(orden_id):
    return render_template('historial_tickets.html', orden_id=orden_id)

@ordenServicio_bp.get('/clientes/<int:cliente_id>/equipos')
@login_required
def equipos_por_cliente(cliente_id):
    """Devuelve los equipos de un cliente en formato JSON (para AJAX)."""
    return jsonify(OrdenServicioController.obtener_equipos_cliente_json(cliente_id))

@ordenServicio_bp.route('/tablero-tickets')
@login_required
def tickets():
    pendientes, en_trabajo, listos = OrdenServicioController.obtener_tickets_tablero()
    return render_template('tickets.html',
                           pendientes=pendientes,
                           en_trabajo=en_trabajo,
                           listos=listos)

@ordenServicio_bp.route('/tablero-tickets/<int:orden_id>')
@login_required
def gestionar_ticket(orden_id):
    from flask import session
    rol_actual = session.get('rol_descripcion', '')
    datos = OrdenServicioController.obtener_datos_gestion_ticket(orden_id, rol_actual)
    if not datos:
        flash("Orden no encontrada.", "error")
        return redirect(url_for('ordenServicio.tickets'))
    
    return render_template('gestionar_ticket.html', **datos)

@ordenServicio_bp.route('/historial')
@login_required
def historial():
    ordenes = OrdenServicioController.obtener_todos()
    return render_template('historial_tickets.html', ordenes=ordenes)

@ordenServicio_bp.route('/comprobante/<int:orden_id>')
@login_required
def comprobante(orden_id):
    orden = OrdenServicioController.obtener_por_id(orden_id)
    if not orden:
        flash("Orden de servicio no encontrada.", "error")
        return redirect(url_for('ordenServicio.tickets'))
    return render_template('comprobante.html', orden=orden)

@ordenServicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/agregar')
@login_required
def agregar_repuesto(orden_id):
    titulo = request.form.get('titulo')
    precio = request.form.get('precio')
    link = request.form.get('link')
    tienda = request.form.get('tienda')
    
    success, message = OrdenServicioController.agregar_repuesto(orden_id, titulo, precio, link, tienda)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400

@ordenServicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/eliminar/<int:idx>')
@login_required
def eliminar_repuesto(orden_id, idx):
    success, message = OrdenServicioController.eliminar_repuesto(orden_id, idx)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400

@ordenServicio_bp.post('/ordenServicio/<int:orden_id>/actualizar-estado-flujo')
@login_required
def cambiar_estado_flujo(orden_id):
    from flask import session
    nuevo_estado = request.form.get('estado')
    observaciones = request.form.get('observaciones', '')
    usuario_id = session.get('usuario_id', 1)
    
    success, message = OrdenServicioController.cambiar_estado_flujo(orden_id, nuevo_estado, usuario_id, observaciones)
    if success:
        flash(message, 'success')
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400