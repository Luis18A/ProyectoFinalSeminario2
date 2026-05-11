from backend.models.TipoDispositivo import TipoDispositivo
from backend.controller.tipoDispositivo_controller import TipoDispositivoController
from flask import Blueprint, request, render_template, request, url_for, flash, redirect
tipoDispositivo_bp = Blueprint('tipoDispositivo', __name__)

'''@tipoDispositivo_bp.route('/tipoDispositivo', methods=['POST'])
def crear_tipo_dispositivo():
    datos = request.get_json()
    dispositivo = datos.get('dispositivo')
    if TipoDispositivo.get_por_descripcion(dispositivo):
        flash('El tipo de dispositivo ya existe', 'error')
    else:
        TipoDispositivo.crear(dispositivo)
        flash('Tipo de dispositivo creado exitosamente', 'success')
    return redirect(url_for('vistas.gestion_equipos'))'''

@tipoDispositivo_bp.route('/tipoDispositivo', methods=['POST'])
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
    return redirect(url_for('vistas.gestion_equipos'))