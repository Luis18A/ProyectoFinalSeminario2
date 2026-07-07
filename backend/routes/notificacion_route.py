import queue
from flask import Blueprint, jsonify, session, Response, current_app
from database import db
from backend.controller import notificacion_controller
from backend.utils.decorators import login_required
from backend.utils.sse_service import sse_service

notificacion_bp = Blueprint('notificaciones', __name__)

@notificacion_bp.post('/notificaciones/<int:id>/leer')
@login_required
def leer_notificacion(id):
    success = notificacion_controller.marcar_como_leida(id, session.get('usuario_id'))
    return jsonify({'success': success}), (200 if success else 404)

@notificacion_bp.post('/notificaciones/leer-todas')
@login_required
def leer_todas_notificaciones():
    success = notificacion_controller.marcar_todas_leidas(session.get('usuario_id'))
    return jsonify({'success': success}), (200 if success else 500)

@notificacion_bp.route('/notificaciones/stream')
def stream_notificaciones():
    # Capturamos la instancia real de la app para usar su contexto en el generador SSE
    app = current_app._get_current_object()
    
    def event_stream():
        # Liberamos la sesión de la base de datos de este hilo para evitar
        # ocupar conexiones del pool durante la conexión SSE persistente.
        with app.app_context():
            db.session.close()
        
        q = sse_service.listen()
        # Enviar ping inicial de apertura de stream
        yield "data: {\"type\": \"ping\"}\n\n"
        try:
            while True:
                try:
                    # Timeout de 3 segundos para responder y verificar rápidamente si
                    # el cliente sigue conectado (evita acumulación de hilos zombis).
                    msg = q.get(timeout=3.0)
                    yield f"data: {msg}\n\n"
                except queue.Empty:
                    yield "data: {\"type\": \"ping\"}\n\n"
        except GeneratorExit:
            pass
        finally:
            # Limpieza garantizada del listener al desconectarse el cliente
            sse_service.remove_listener(q)
            with app.app_context():
                db.session.close()
                
    return Response(event_stream(), mimetype="text/event-stream")

