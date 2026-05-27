from backend.controller.tipoDispositivo_controller import TipoDispositivoController
from flask import Blueprint, request, render_template, request, url_for, flash, redirect
from backend.utils.decorators import login_required

tipoDispositivo_bp = Blueprint('tipoDispositivo', __name__)

@tipoDispositivo_bp.route('/tipoDispositivo', methods=['POST'])
@login_required
def crear_tipo_dispositivo():
    # 1. Delegamos TODA la lógica al controlador
    # Le pasamos el request.form completo
    success, message = TipoDispositivoController.crear_tipoDispositivo(request.form)
    
    # 2. Dependiendo del resultado, preparamos el mensaje para la UI
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    # 3. Redirigimos a la vista que elijas (ej: gestión de equipos)
    cliente_id = request.form.get('cliente_id')
    return redirect(url_for('equipo.gestion_equipos', cliente_id=cliente_id))
