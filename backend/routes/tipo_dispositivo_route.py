from flask import Blueprint, request, url_for, flash, redirect, jsonify
from backend.controller.tipo_dispositivo_controller import TipoDispositivoController
from backend.utils.decorators import login_required, role_required

tipo_dispositivo_bp = Blueprint('tipo_dispositivo', __name__)

@tipo_dispositivo_bp.post('/tipoDispositivo')
@login_required
@role_required('Administrador', 'Secretario')
def crear_tipo_dispositivo():
    cliente_id = request.form.get('cliente_id')
    success, message = TipoDispositivoController.crear_tipoDispositivo(request.form)
    flash(message, 'success' if success else 'error')
    
    destino = url_for('equipo.gestion_equipos', cliente_id=cliente_id) if cliente_id else url_for('clientes.gestion_cliente')
    return redirect(destino)

@tipo_dispositivo_bp.post('/tipoDispositivo/rapido')
@login_required
@role_required('Administrador', 'Secretario')
def crear_tipo_dispositivo_rapido():
    # La ruta delega TODO. El controlador debe devolver el objeto 'tipo' si tiene éxito.
    success, message, tipo_data = TipoDispositivoController.crear_tipo_rapido(request.form)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400

    return jsonify({
        'success': True,
        'message': message,
        'tipo': tipo_data
    })