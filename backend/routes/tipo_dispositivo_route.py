from flask import Blueprint, request, url_for, flash, redirect, jsonify
from backend.controller import tipo_dispositivo_controller
from backend.utils.decorators import login_required, role_required

tipo_dispositivo_bp = Blueprint('tipo_dispositivo', __name__)


@tipo_dispositivo_bp.post('/tipoDispositivo/rapido')
@login_required
@role_required('Administrador', 'Secretario')
def crear_tipo_dispositivo_rapido():
    success, message, tipo_data = tipo_dispositivo_controller.crear_tipo_rapido(request.form)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400

    return jsonify({
        'success': True,
        'message': message,
        'tipo': tipo_data
    })