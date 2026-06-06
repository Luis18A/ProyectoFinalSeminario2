import csv
import io
from backend.controller.ordenServicio_controller import OrdenServicioController
from flask import Blueprint, request, render_template, url_for, flash, redirect, jsonify, session, Response
from backend.utils.decorators import login_required, role_required

ordenServicio_bp = Blueprint('ordenServicio', __name__)

@ordenServicio_bp.post('/ordenServicio')
@login_required
@role_required('Administrador', 'Secretario')
def crear_ordenServicio():
    success, message = OrdenServicioController.crear_ordenServicio(request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
        
    next_url = request.args.get('next') or request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('usuarios.secretary'))

@ordenServicio_bp.post('/ordenServicio/editar/<int:id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def editar_ordenServicio(id):
    success, message = OrdenServicioController.actualizar_ordenServicio(id, request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    rol = session.get('rol_descripcion', '')
    redirecciones = {
        'Técnico': 'usuarios.technician',
        'Tecnico': 'usuarios.technician',
        'Secretario': 'usuarios.secretary',
        'Secretaria': 'usuarios.secretary',
        'Administrador': 'vistas.dashboard'
    }
    destino = redirecciones.get(rol, 'usuarios.secretary')
    return redirect(url_for(destino))

@ordenServicio_bp.get('/ordenServicio/historial/<int:orden_id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def historial_ordenServicio(orden_id):
    rol_actual = session.get('rol_descripcion', '')
    datos = OrdenServicioController.obtener_datos_gestion_ticket(orden_id, rol_actual)
    if not datos:
        flash("Orden de servicio no encontrada.", "error")
        redirecciones = {
            'Técnico': 'usuarios.technician',
            'Secretario': 'usuarios.secretary',
            'Administrador': 'vistas.dashboard'
        }
        destino = redirecciones.get(rol_actual, 'usuarios.secretary')
        return redirect(url_for(destino))
        
    # Forzar vista de solo lectura para consulta histórica
    datos['puede_editar'] = False
    datos['puede_editar_costos'] = False
    
    return render_template('gestionar_ticket.html', **datos)

@ordenServicio_bp.get('/clientes/<int:cliente_id>/equipos')
@login_required
@role_required('Administrador', 'Secretario')
def equipos_por_cliente(cliente_id):
    """Devuelve los equipos de un cliente en formato JSON (para AJAX)."""
    equipos = OrdenServicioController.obtener_equipos_cliente_json(cliente_id)
    if equipos is None:
        return jsonify({'error': 'Cliente no encontrado.'}), 404
    return jsonify(equipos)

@ordenServicio_bp.route('/tablero-tickets/<int:orden_id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def gestionar_ticket(orden_id):
    rol_actual = session.get('rol_descripcion', '')
    datos = OrdenServicioController.obtener_datos_gestion_ticket(orden_id, rol_actual)
    if not datos or 'orden' not in datos:
        flash("Error al cargar la orden o acceso denegado.", "error")
        if rol_actual in ('Técnico', 'Tecnico'):
            return redirect(url_for('usuarios.technician'))
        return redirect(url_for('usuarios.secretary'))
    
    return render_template('gestionar_ticket.html', **datos)

@ordenServicio_bp.route('/historial')
@role_required('Administrador')
def historial():
    ticket_id = request.args.get('ticket_id', '').strip()
    cliente = request.args.get('cliente', '').strip()
    equipo = request.args.get('equipo', '').strip()
    
    ordenes = OrdenServicioController.obtener_historial_filtrado(ticket_id, cliente, equipo)
    return render_template('historial_tickets.html', ordenes=ordenes)

@ordenServicio_bp.route('/historial/exportar')
@role_required('Administrador')
def exportar_csv():
    ticket_id = request.args.get('ticket_id', '').strip()
    cliente = request.args.get('cliente', '').strip()
    equipo = request.args.get('equipo', '').strip()
    
    ordenes = OrdenServicioController.obtener_historial_filtrado(ticket_id, cliente, equipo)
    
    # Crear el archivo CSV en memoria
    output = io.StringIO()
    # Escribir UTF-8 BOM para soporte óptimo de Excel en Windows
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')
    
    # Cabeceras
    writer.writerow([
        'Ticket ID', 
        'Cliente Nombre', 
        'Cliente DNI/CUIL', 
        'Cliente Teléfono', 
        'Cliente Email', 
        'Equipo Tipo', 
        'Equipo Marca', 
        'Equipo Modelo', 
        'Equipo S/N', 
        'Estado', 
        'Fecha Recepción', 
        'Fecha Entrega', 
        'Costo ($)', 
        'Observaciones'
    ])
    
    for o in ordenes:
        fecha_recepcion_str = o.fecha_recepcion.strftime('%d/%m/%Y %H:%M:%S') if o.fecha_recepcion else '—'
        fecha_entrega_str = o.fecha_entrega.strftime('%d/%m/%Y %H:%M:%S') if o.fecha_entrega else '—'
        costo_str = f"{o.costo:.2f}" if o.costo is not None else '0.00'
        tipo_str = o.equipo.tipo.descripcion if (o.equipo and o.equipo.tipo) else '—'
        
        writer.writerow([
            f"TK-{o.id:04d}",
            f"{o.equipo.cliente.apellido}, {o.equipo.cliente.nombre}" if o.equipo and o.equipo.cliente else '—',
            o.equipo.cliente.dni_cuil if o.equipo and o.equipo.cliente else '—',
            o.equipo.cliente.telefono if o.equipo and o.equipo.cliente else '—',
            o.equipo.cliente.email if o.equipo and o.equipo.cliente else '—',
            tipo_str,
            o.equipo.marca if o.equipo else '—',
            o.equipo.modelo if o.equipo else '—',
            o.equipo.numero_serie if o.equipo else '—',
            o.estado.value if o.estado else '—',
            fecha_recepcion_str,
            fecha_entrega_str,
            costo_str,
            o.observaciones or '—'
        ])
        
    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=techflow_historial_tickets.csv"}
    )

@ordenServicio_bp.route('/comprobante/<int:orden_id>')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def comprobante(orden_id):
    orden = OrdenServicioController.obtener_por_id(orden_id)
    if not orden:
        flash("Orden de servicio no encontrada.", "error")
        rol = session.get('rol_descripcion', '')
        if rol in ('Técnico', 'Tecnico'):
            return redirect(url_for('usuarios.technician'))
        return redirect(url_for('usuarios.secretary'))
    return render_template('comprobante.html', orden=orden)

@ordenServicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/agregar')
@login_required
@role_required('Administrador', 'Técnico')
def agregar_repuesto(orden_id):
    titulo = request.form.get('titulo', '').strip()
    precio_raw = request.form.get('precio', '0').strip()
    link = request.form.get('link', '#').strip()
    tienda = request.form.get('tienda', 'Manual').strip()
    
    if not titulo:
        return jsonify({'success': False, 'message': 'La descripción no puede estar vacía.'}), 400
        
    try:
        precio = float(precio_raw)
        if precio < 0:
            raise ValueError
    except ValueError:
        return jsonify({'success': False, 'message': 'El precio debe ser un número válido mayor o igual a 0.'}), 400
        
    success, message = OrdenServicioController.agregar_repuesto(orden_id, titulo, precio, link, tienda)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400

@ordenServicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/eliminar/<int:idx>')
@login_required
@role_required('Administrador', 'Técnico')
def eliminar_repuesto(orden_id, idx):
    success, message = OrdenServicioController.eliminar_repuesto(orden_id, idx)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400

@ordenServicio_bp.post('/ordenServicio/<int:orden_id>/repuesto/editar/<int:idx>')
@login_required
@role_required('Administrador', 'Técnico')
def editar_repuesto(orden_id, idx):
    titulo = request.form.get('titulo', '').strip()
    precio_raw = request.form.get('precio', '0').strip()
    
    if not titulo:
        return jsonify({'success': False, 'message': 'La descripción no puede estar vacía.'}), 400
        
    try:
        precio = float(precio_raw)
        if precio < 0:
            raise ValueError
    except ValueError:
        return jsonify({'success': False, 'message': 'El precio debe ser un número válido mayor o igual a 0.'}), 400
        
    success, message = OrdenServicioController.editar_repuesto(orden_id, idx, titulo, precio)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400

@ordenServicio_bp.post('/ordenServicio/<int:orden_id>/actualizar-estado-flujo')
@login_required
@role_required('Administrador', 'Secretario', 'Técnico')
def cambiar_estado_flujo(orden_id):
    nuevo_estado = request.form.get('estado')
    observaciones = request.form.get('observaciones', '')
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify({'success': False, 'message': 'Sesión expirada.'}), 401
    
    success, message = OrdenServicioController.cambiar_estado_flujo(orden_id, nuevo_estado, usuario_id, observaciones)
    if success:
        flash(message, 'success')
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400