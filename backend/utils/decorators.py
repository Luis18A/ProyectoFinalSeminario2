from functools import wraps
from flask import session, redirect, url_for, flash

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
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario_id' not in session:
                flash("Debes iniciar sesión para acceder a esta página.", "error")
                return redirect(url_for('vistas.login'))
            
            # El rol se guarda en la sesión al hacer login
            user_role = session.get('rol_descripcion', '')
            
            if user_role not in allowed_roles:
                flash("No tienes permisos suficientes para ver esta página.", "error")
                # Redirigir al dashboard genérico u otra página segura
                return redirect(url_for('vistas.dashboard'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
