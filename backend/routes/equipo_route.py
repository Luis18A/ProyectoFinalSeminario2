from flask import Blueprint, request, render_template, url_for, flash, redirect, jsonify
from backend.controller import equipo_controller
from backend.utils.decorators import login_required, role_required

equipo_bp = Blueprint('equipo', __name__)

@equipo_bp.post('/equipo')
@login_required
@role_required('Administrador', 'Secretario')
def crear_equipo():
    cliente_id = request.form.get('cliente_id')
    success, result = equipo_controller.crear_equipo(request.form)
    if success:
        flash("Equipo creado exitosamente.", "success")
    else:
        flash(result, "error")
    
    # Estandarización de redirección
    destino = url_for('equipo.gestion_equipos', cliente_id=cliente_id) if cliente_id else url_for('clientes.gestion_cliente')
    return redirect(destino)

@equipo_bp.post('/equipo/editar/<int:id>')
@login_required
@role_required('Administrador', 'Secretario')
def editar_equipo(id):
    cliente_id = request.form.get('cliente_id')
    success, message = equipo_controller.editar_equipo(id, request.form)
    flash(message, 'success' if success else 'error')
    
    destino = url_for('equipo.gestion_equipos', cliente_id=cliente_id) if cliente_id else url_for('clientes.gestion_cliente')
    return redirect(destino)

@equipo_bp.get('/equipos/<int:cliente_id>')
@login_required
@role_required('Administrador', 'Secretario')
def gestion_equipos(cliente_id):
    tipo_dispositivos, cliente, equipos = equipo_controller.obtener_datos_gestion_cliente(cliente_id)
    if not cliente:
        flash("Cliente no encontrado para gestionar sus equipos.", "error")
        return redirect(url_for('clientes.gestion_cliente'))
        
    return render_template('gestion_equipos.html',
                           tipo_dispositivos=tipo_dispositivos,
                           cliente=cliente,
                           equipos=equipos)

@equipo_bp.get('/clientes/<int:cliente_id>/equipos')
@login_required
@role_required('Administrador', 'Secretario')
def equipos_por_cliente(cliente_id):
    equipos = equipo_controller.obtener_equipos_cliente_json(cliente_id)
    return jsonify(equipos if equipos is not None else {'error': 'Cliente no encontrado.'}), (200 if equipos is not None else 404)