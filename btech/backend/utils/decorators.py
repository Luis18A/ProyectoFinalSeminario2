from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """
    Verifica que el usuario actual tenga uno de los roles permitidos.
    Ejemplo de uso: @role_required('Administrador', 'Tecnico')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Verificamos que esté logueado
            if not current_user.is_authenticated:
                abort(401) # No autorizado
            
            # 2. Verificamos el rol. Al ser un Enum en tu models.py, usamos .value
            if current_user.rol.value not in roles:
                abort(403) # Prohibido (no tiene los permisos)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator