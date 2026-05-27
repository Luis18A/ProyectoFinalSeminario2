from backend.controller.equipo_controller import EquipoController
from backend.models.Equipo import Equipo
from flask import Blueprint, request, render_template, url_for, flash, redirect, jsonify
from backend.utils.decorators import login_required

equipo_bp = Blueprint('equipo', __name__)

@equipo_bp.route('/equipo', methods=['POST'])
@login_required
def crear_equipo():
    success, message = EquipoController.crear_equipo(request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    cliente_id = request.form.get('cliente_id')
    return redirect(url_for('equipo.gestion_equipos', cliente_id=cliente_id))

@equipo_bp.post('/equipo/editar/<int:id>')
@login_required
def editar_equipo(id):
    success, message = EquipoController.editar_equipo(id, request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    cliente_id = request.form.get('cliente_id')
    return redirect(url_for('equipo.gestion_equipos', cliente_id=cliente_id))

@equipo_bp.route('/equipos')
@equipo_bp.route('/equipos/<int:cliente_id>')
@login_required
def gestion_equipos(cliente_id=None):
    tipo_dispositivos, cliente, equipos = EquipoController.obtener_datos_gestion(cliente_id)
    return render_template('gestion_equipos.html',
                           tipo_dispositivos=tipo_dispositivos,
                           cliente=cliente,
                           equipos=equipos)

@equipo_bp.post('/equipo/rapido')
@login_required
def crear_equipo_rapido():
    success, message = EquipoController.crear_equipo(request.form)
    if success:
        serie = request.form.get('numero_serie')
        equipo = Equipo.get_por_numero_serie(serie)
        return jsonify({
            'success': True,
            'message': message,
            'equipo': {
                'id': equipo.id,
                'label': f"{equipo.marca} {equipo.modelo} (S/N: {equipo.numero_serie})"
            }
        })
    else:
        return jsonify({'success': False, 'message': message}), 400