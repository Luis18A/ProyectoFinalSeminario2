from flask import Blueprint, jsonify, session
from backend.controller.notificacion_controller import NotificacionController
from backend.utils.decorators import login_required

notificacion_bp = Blueprint('notificaciones', __name__)

@notificacion_bp.post('/notificaciones/<int:id>/leer')
@login_required
def leer_notificacion(id):
    success = NotificacionController.marcar_como_leida(id, session.get('usuario_id'))
    return jsonify({'success': success}), (200 if success else 404)

@notificacion_bp.post('/notificaciones/leer-todas')
@login_required
def leer_todas_notificaciones():
    NotificacionController.marcar_todas_leidas(session.get('usuario_id'))
    return jsonify({'success': True})
