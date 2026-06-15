from flask import Blueprint, request, render_template, url_for, flash, redirect, jsonify, session, Response
from backend.controller import orden_presupuesto_controller
from backend.controller import orden_flujo_controller
from backend.controller import orden_servicio_controller
from backend.utils.decorators import login_required, role_required

orden_servicio_bp = Blueprint('orden_servicio', __name__)

@orden_servicio_bp.post('/ordenServicio')
@login_required
@role_required('Administrador', 'Secretario')
def crear_ordenServicio():
    success, message = orden_servicio_controller.crear_ordenServicio(request.form)
    flash(message, 'success' if success else 'error')
    
    next_url = request.args.get('next') or request.form.get('next')
    return redirect(next_url) if next_url else redirect(url_for('vistas.secretary'))

@orden_servicio_bp.post('/ordenServicio/editar/<int:id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def editar_ordenServicio(id):
    # La ruta entrega los datos, el controlador aplica las reglas de negocio
    success, message = orden_flujo_controller.actualizar_ordenServicio(id, request.form, session.get('rol_descripcion', ''))
    flash(message, 'success' if success else 'error')
    
    if not success:
        return redirect(url_for('orden_servicio.gestionar_ticket', orden_id=id))
        
    redirecciones = {'Técnico': 'vistas.technician', 'Secretario': 'vistas.secretary', 'Administrador': 'vistas.dashboard'}
    return redirect(url_for(redirecciones.get(session.get('rol_descripcion'), 'vistas.secretary')))

@orden_servicio_bp.route('/tablero-tickets/<int:orden_id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def gestionar_ticket(orden_id):
    datos = orden_flujo_controller.obtener_datos_gestion_ticket(orden_id, session.get('rol_descripcion', ''))
    if not datos:
        flash("Acceso denegado o ticket inexistente.", "error")
        return redirect(url_for('vistas.technician') if session.get('rol_descripcion') == 'Técnico' else url_for('vistas.secretary'))
    
    if request.args.get('readonly') == 'true':
        datos.update({'puede_editar': False, 'puede_editar_costos': False})
        
    return render_template('gestionar_ticket.html', **datos)

# --- RUTAS DE REPUESTOS (Delegación total al controlador) ---
@orden_servicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/agregar')
@login_required
@role_required('Administrador', 'Técnico')
def agregar_repuesto(orden_id):
    success, message = orden_presupuesto_controller.agregar_repuesto(orden_id, **request.form.to_dict())
    return jsonify({'success': success, 'message': message}), (200 if success else 400)

@orden_servicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/editar/<int:idx>')
@login_required
@role_required('Administrador', 'Técnico')
def editar_repuesto(orden_id, idx):
    # La validación de que sea un número y el título no sea vacío se movió al controller
    success, message = orden_presupuesto_controller.editar_repuesto(orden_id, idx, **request.form.to_dict())
    return jsonify({'success': success, 'message': message}), (200 if success else 400)

@orden_servicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/eliminar/<int:idx>')
@login_required
@role_required('Administrador', 'Técnico')
def eliminar_repuesto(orden_id, idx):
    success, message = orden_presupuesto_controller.eliminar_repuesto(orden_id, idx)
    return jsonify({'success': success, 'message': message}), (200 if success else 400)


@orden_servicio_bp.route('/historial/exportar')
@login_required
@role_required('Administrador')
def exportar_csv():
    # El controller debe devolver un objeto con los datos, la ruta solo orquesta la descarga
    csv_data = orden_servicio_controller.generar_csv_historial(request.args) 
    return Response(csv_data, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=historial.csv"})


@orden_servicio_bp.get('/ordenServicio/historial/<int:orden_id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def historial_ordenServicio(orden_id):
    return redirect(url_for('orden_servicio.gestionar_ticket', orden_id=orden_id, readonly='true'))


@orden_servicio_bp.get('/historial')
@login_required
@role_required('Administrador')
def historial():
    ordenes = orden_servicio_controller.obtener_historial_filtrado(
        ticket_id=request.args.get('ticket_id'),
        cliente_query=request.args.get('cliente'),
        equipo_query=request.args.get('equipo')
    )
    return render_template('historial_tickets.html', ordenes=ordenes)


@orden_servicio_bp.get('/comprobante/<int:orden_id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def comprobante(orden_id):
    orden = orden_servicio_controller.obtener_por_id(orden_id)
    if not orden:
        flash("Orden de servicio no encontrada.", "error")
        return redirect(url_for('vistas.technician') if session.get('rol_descripcion') == 'Técnico' else url_for('vistas.secretary'))
    return render_template('comprobante.html', orden=orden)

@orden_servicio_bp.post('/ordenServicio/<int:orden_id>/actualizar-estado-flujo')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def cambiar_estado_flujo(orden_id):
    # La validación de session.get('usuario_id') ya ocurre en el @login_required.
    # Aquí solo extraemos datos y delegamos al controller.
    success, message = orden_flujo_controller.cambiar_estado_flujo(
        orden_id=orden_id,
        nuevo_estado_name=request.form.get('estado'),
        usuario_id=session.get('usuario_id'),
        observacion=request.form.get('observaciones'),
        rol_actual=session.get('rol_descripcion', '')
    )
    return jsonify({'success': success, 'message': message}), (200 if success else 400)

@orden_servicio_bp.get('/ordenServicio/activas')
@login_required
@role_required('Administrador', 'Secretario')
def listar_ordenes_view():
    # Delegación total: la ruta no sabe qué datos se necesitan, solo los renderiza.
    return render_template('listar_ordenes.html', **orden_servicio_controller.obtener_datos_lista_activas())