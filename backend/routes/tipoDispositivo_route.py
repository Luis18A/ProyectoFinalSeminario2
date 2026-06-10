from backend.controller.tipoDispositivo_controller import TipoDispositivoController
from flask import Blueprint, request, render_template, url_for, flash, redirect
from backend.utils.decorators import login_required, role_required

tipoDispositivo_bp = Blueprint('tipoDispositivo', __name__)

@tipoDispositivo_bp.route('/tipoDispositivo', methods=['POST'])
@login_required
@role_required('Administrador', 'Secretario')
def crear_tipo_dispositivo():
    # 1. Delegamos TODA la lógica al controlador
    # Le pasamos el request.form completo
    success, message = TipoDispositivoController.crear_tipoDispositivo(request.form)
    
    # 2. Dependiendo del resultado, preparamos el mensaje para la UI
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    # 3. Redirigimos a la vista de gestión de equipos o clientes de manera segura
    cliente_id = request.form.get('cliente_id')
    return redirect(url_for('equipo.gestion_equipos', cliente_id=cliente_id) if cliente_id else url_for('clientes.gestion_cliente'))

@tipoDispositivo_bp.post('/tipoDispositivo/rapido')
@login_required
@role_required('Administrador', 'Secretario')
def crear_tipo_dispositivo_rapido():
    from flask import jsonify
    success, message = TipoDispositivoController.crear_tipoDispositivo(request.form)
    if success:
        from backend.models.TipoDispositivo import TipoDispositivo
        descripcion = request.form.get('descripcion', '').strip()
        tipo = TipoDispositivo.obtener_por_descripcion(descripcion)
        if not tipo:
            return jsonify({'success': False, 'message': 'Error al recuperar el tipo creado.'}), 500
        return jsonify({
            'success': True,
            'message': message,
            'tipo': {
                'id': tipo.id,
                'descripcion': tipo.descripcion
            }
        })
    else:
        return jsonify({'success': False, 'message': message}), 400
