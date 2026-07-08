import os
from flask import Flask, flash, redirect, url_for, session
from database import db, FALLBACK_DATABASE_URL
from backend.models import Notificacion
from backend.routes.vistas_route import vistas_bp
from backend.routes.usuario_route import usuarios_bp
from backend.routes.cliente_route import cliente_bp
from backend.routes.tipo_dispositivo_route import tipo_dispositivo_bp
from backend.routes.equipo_route import equipo_bp
from backend.routes.orden_servicio_route import orden_servicio_bp
from backend.routes.admin_route import admin_bp
from backend.routes.notificacion_route import notificacion_bp
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    """
    Application Factory Pattern.
    Crea, configura e inicializa de forma rápida la aplicación Flask,
    eliminando comprobaciones redundantes de base de datos en cada arranque.
    """
    app = Flask(
        __name__,
        template_folder='frontend/templates',
        static_folder='frontend/static'
    )

    # 1. Configuración de Seguridad y Base de Datos
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-CAMBIAR-en-produccion')
    
    db_uri = os.environ.get('DATABASE_URL', FALLBACK_DATABASE_URL)
    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
        
    if not db_uri or not db_uri.startswith("postgresql://"):
        raise ValueError("DATABASE_URL inválida. TechFlow requiere PostgreSQL como base de datos.")
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # 2. Inicialización de Extensiones
    db.init_app(app)
    csrf.init_app(app)

    # Inicializar esquema de base de datos y usuarios/roles base
    with app.app_context():
        db.create_all()
        from backend.utils.db_seeder import auto_seed_db
        auto_seed_db()

    # 3. Registro de Blueprints
    app.register_blueprint(vistas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(tipo_dispositivo_bp)
    app.register_blueprint(equipo_bp)
    app.register_blueprint(orden_servicio_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notificacion_bp)

    # 4. Manejo de Errores HTTP Centralizado
    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        if not session.get('usuario_id'):
            return redirect(url_for('vistas.login'))
        flash("La dirección ingresada no existe o no está permitida.", "error")
        return redirect(url_for('vistas.dashboard'))

    @app.errorhandler(403)
    def acceso_prohibido(e):
        flash("No tenés permisos para acceder a esta sección.", "error")
        return redirect(url_for('vistas.dashboard'))

    # 5. Inyección de Notificaciones en las Plantillas
    @app.context_processor
    def inject_notifications():
        usuario_id = session.get('usuario_id')
        if usuario_id:
            notificaciones = (
                Notificacion.query
                .filter_by(usuario_id=usuario_id)
                .order_by(Notificacion.fecha_creacion.desc())
                .limit(15)
                .all()
            )
            cant_no_leidas = Notificacion.query.filter_by(
                usuario_id=usuario_id, leido=False
            ).count()
            return dict(
                global_notifications=notificaciones,
                global_unread_count=cant_no_leidas
            )
        return dict(global_notifications=[], global_unread_count=0)

    return app

# Instancia global para WSGI
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)