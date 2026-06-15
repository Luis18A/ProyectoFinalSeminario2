from functools import wraps
from flask import session, redirect, url_for, flash


def _redirect_por_rol(rol):
    """Redirige al usuario a su vista principal según su rol."""
    destinos = {
        'técnico':       'vistas.technician',
        'secretario':    'orden_servicio.listar_ordenes_view',
        'administrador': 'vistas.dashboard',
    }
    destino = destinos.get(rol.strip().lower(), 'vistas.login')
    return redirect(url_for(destino))


def login_required(f):
    """
    Verifica que haya una sesión activa.
    Si no hay sesión, redirige al login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debés iniciar sesión para acceder.", "error")
            return redirect(url_for('vistas.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles_permitidos):
    """
    Verifica que el usuario en sesión tenga uno de los roles permitidos.

    DECISIÓN ARQUITECTÓNICA:
    El rol se lee desde session['rol_descripcion'], no desde la BD.
    Esto asume que la SECRET_KEY es suficientemente segura (variable de entorno).
    Si se requiere mayor rigor, reemplazar por verificación contra BD:
        usuario = Usuario.obtener_por_id(session['usuario_id'])
        rol_actual = usuario.rol.descripcion
    El costo es una query extra por request protegido.
    """
    roles_lower = {r.lower() for r in roles_permitidos}  # set para O(1) lookup

    def decorator(f):
        # ── CORRECCIÓN: ya no duplica la verificación de sesión.
        # Se asume que role_required siempre se usa DESPUÉS de @login_required.
        @wraps(f)
        def decorated_function(*args, **kwargs):
            rol_actual = session.get('rol_descripcion', '').strip().lower()

            if rol_actual not in roles_lower:
                flash("No tenés permisos para acceder a esta sección.", "error")
                return _redirect_por_rol(rol_actual)

            return f(*args, **kwargs)
        return decorated_function
    return decorator