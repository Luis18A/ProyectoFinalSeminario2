import os
import queue
from flask import Flask, flash, redirect, url_for, session, Response
from database import db
from backend.utils.sse_service import sse_service

# ─────────────────────────────────────────────
# IMPORTS de modelos (necesarios para create_all)
# ─────────────────────────────────────────────
from backend.models.Usuario import Usuario
from backend.models.Rol import Rol
from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.Notificacion import Notificacion
from backend.models.Repuesto import Repuesto
from backend.models.OrdenRepuesto import OrdenRepuesto



# ─────────────────────────────────────────────
# IMPORTS de Blueprints
# ─────────────────────────────────────────────
from backend.routes.vistas_route import vistas_bp
from backend.routes.usuario_route import usuarios_bp
from backend.routes.cliente_route import cliente_bp
from backend.routes.tipo_dispositivo_route import tipo_dispositivo_bp
from backend.routes.equipo_route import equipo_bp
from backend.routes.orden_servicio_route import orden_servicio_bp
from backend.routes.admin_route import admin_bp
from backend.routes.notificacion_route import notificacion_bp

# Configurar Flask para que busque en la carpeta frontend
app = Flask(__name__, 
            template_folder='frontend/templates', 
            static_folder='frontend/static')


# CONEXIÓN A LA BASE DE DATOS
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:3536@localhost:5432/techflowdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'techflow_secret_key_123' # Necesario para sesiones y flash messages

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


def create_app():
    """
    Application Factory Pattern.
    Permite crear múltiples instancias (producción, testing, etc.)
    """
    app = Flask(
        __name__,
        template_folder='frontend/templates',
        static_folder='frontend/static'
    )

    _configure_app(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context_processors(app)

    with app.app_context():
        db.create_all()
        _auto_seed_db(app)

    return app


def _configure_app(app):
    """Centraliza toda la configuración. En producción, cargar desde .env"""

    # ─── SEGURIDAD CRÍTICA ───────────────────────────────────────────────
    # SECRET_KEY debe venir de variable de entorno, nunca hardcodeada.
    # En desarrollo podés dejar el fallback, pero documentá que en producción
    # DEBE estar definida como variable de entorno.
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-CAMBIAR-en-produccion')

    # ─── BASE DE DATOS ───────────────────────────────────────────────────
    # Igual: la URI debe venir de variable de entorno en producción.
    db_uri = os.environ.get(
        'DATABASE_URL',
        'sqlite:///techflow.db'  # fallback local / sqlite para demo
    )
    if db_uri and db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ─── SEGURIDAD ADICIONAL ─────────────────────────────────────────────
    app.config['SESSION_COOKIE_HTTPONLY'] = True   # JS no puede leer la cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protección extra contra CSRF


def _init_extensions(app):
    """Inicializa las extensiones de Flask."""
    db.init_app(app)
    csrf.init_app(app)


def _register_blueprints(app):
    """Registra todos los Blueprints."""
    app.register_blueprint(vistas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(tipo_dispositivo_bp)
    app.register_blueprint(equipo_bp)
    app.register_blueprint(orden_servicio_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notificacion_bp)


def _register_error_handlers(app):
    """Manejo centralizado de errores HTTP."""

    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        # Si no hay sesión activa, mandarlo a login, no al dashboard
        if not session.get('usuario_id'):
            return redirect(url_for('vistas.login'))
        flash("La dirección ingresada no existe o no está permitida.", "error")
        return redirect(url_for('vistas.dashboard'))

    @app.errorhandler(403)
    def acceso_prohibido(e):
        flash("No tenés permisos para acceder a esta sección.", "error")
        return redirect(url_for('vistas.dashboard'))


def _register_context_processors(app):
    """Variables globales inyectadas en todos los templates."""

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


def _auto_seed_db(app):
    """Siembre datos automáticamente para el portfolio (ej. en Render) si está vacío."""
    from backend.models.Rol import Rol
    from backend.models.Usuario import Usuario
    from backend.models.TipoDispositivo import TipoDispositivo
    
    # Verificamos si ya existen roles
    if Rol.query.count() == 0:
        print("Base de datos vacía detectada. Inicializando roles y usuarios base...")
        try:
            ROLES = ["Administrador", "Técnico", "Secretario"]
            roles_dict = {}
            for r_desc in ROLES:
                rol = Rol(descripcion=r_desc)
                db.session.add(rol)
                roles_dict[r_desc] = rol
            db.session.commit()
            
            USUARIOS = [
                {"username": "admin",      "password": "administrador",     "nombre": "administrador",  "apellido": "administrador", "rol": "Administrador"},
                {"username": "tecnico",    "password": "tecnico",   "nombre": "tecnico",   "apellido": "tecnico",   "rol": "Técnico"},
                {"username": "secretario", "password": "secretario","nombre": "secretario",    "apellido": "secretario","rol": "Secretario"},
            ]
            for u_data in USUARIOS:
                usuario = Usuario(
                    username=u_data['username'],
                    password=Usuario.hashear_password(u_data['password']),
                    nombre=u_data['nombre'],
                    apellido=u_data['apellido'],
                    rol_id=roles_dict[u_data['rol']].id,
                    activo=True
                )
                db.session.add(usuario)
            
            TIPOS_DISPOSITIVO = ["Notebook", "PC Escritorio", "Impresora", "Servidor", "Consola"]
            for t_desc in TIPOS_DISPOSITIVO:
                db.session.add(TipoDispositivo(descripcion=t_desc))
            db.session.commit()
            
            print("Sembrando datos de prueba realistas (clientes, equipos, órdenes, historial)...")
            from datos_prueba import generar_datos
            generar_datos()
            print("Base de datos inicializada y sembrada correctamente para el portfolio!")
        except Exception as e:
            db.session.rollback()
            print(f"Error al sembrar datos de prueba automáticamente: {e}")


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────
app = create_app()

@app.route('/notificaciones/stream')
def stream_notificaciones():
    def event_stream():
        q = sse_service.listen()
        # Enviar ping inicial de apertura de stream
        yield "data: {\"type\": \"ping\"}\n\n"
        while True:
            try:
                # Timeout corto para detectar desconexión del cliente rápidamente y liberar el hilo
                msg = q.get(timeout=0.1)
                yield f"data: {msg}\n\n"
            except queue.Empty:
                yield "data: {\"type\": \"ping\"}\n\n"
            except Exception:
                break
                
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, port=5000)