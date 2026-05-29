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
                # Redirigir al panel correspondiente según el rol del usuario
                if user_role in ('Técnico', 'Tecnico'):
                    return redirect(url_for('usuarios.technician'))
                elif user_role in ('Secretario', 'Secretaria'):
                    return redirect(url_for('usuarios.secretary'))
                elif user_role in ('Administrador', 'Administrdor'):
                    return redirect(url_for('vistas.dashboard'))
                else:
                    return redirect(url_for('vistas.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
