from functools import wraps
from flask import session, redirect, url_for, flash


def _redirect_por_rol(rol):
    """Redirige al usuario a su vista principal según su rol."""
    destinos = {
        'técnico':       'vistas.technician',
        'secretario':    'vistas.secretary',
        'administrador': 'vistas.dashboard',
    }
    destino = destinos.get(rol.strip().lower(), 'vistas.login')
    return redirect(url_for(destino))


def login_required(f):
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debés iniciar sesión para acceder.", "error")
            return redirect(url_for('vistas.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles_permitidos):

    roles_lower = {r.lower() for r in roles_permitidos}

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            rol_actual = session.get('rol_descripcion', '').strip().lower()

            if rol_actual not in roles_lower:
                flash("No tenés permisos para acceder a esta sección.", "error")
                return _redirect_por_rol(rol_actual)

            return f(*args, **kwargs)
        return decorated_function
    return decorator