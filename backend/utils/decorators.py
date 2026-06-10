from functools import wraps
from flask import session, redirect, url_for, flash

def _redirect_por_rol(rol):
    """Auxiliar para redirigir al usuario según su rol de forma normalizada."""
    redirecciones = {
        'técnico': 'usuarios.technician',
        'secretario': 'ordenServicio.listar_ordenes_view',
        'administrador': 'vistas.dashboard'
    }
    dest = redirecciones.get(rol.lower(), 'vistas.login')
    return redirect(url_for(dest))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash("Debes iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for('vistas.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """
    Permite el acceso solo si el usuario en sesión tiene alguno de los roles permitidos.
    Soporta validaciones insensibles a mayúsculas/minúsculas y tildes.
    """
    allowed_roles_lower = [r.lower() for r in allowed_roles]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                flash("Debes iniciar sesión para acceder a esta página.", "error")
                return redirect(url_for('vistas.login'))
            
            user_role = session.get('rol_descripcion', '')
            
            if user_role.lower() not in allowed_roles_lower:
                flash("No tienes permisos suficientes para ver esta página.", "error")
                return _redirect_por_rol(user_role)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
