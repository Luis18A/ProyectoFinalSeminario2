from backend.models import db, Usuario

def validar_login(username, password):
    # Forma moderna (SQLAlchemy 2.0) de buscar un registro
    usuario = db.session.scalar(db.select(Usuario).filter_by(username=username))
    
    # Regla 1: El usuario debe existir
    if not usuario:
        # Nota de seguridad: Siempre damos el mismo mensaje para no dar pistas a los hackers
        return None, 'Usuario o contraseña incorrectos.'
        
    # Regla 2: La contraseña debe coincidir (el modelo hace el hash)
    if not usuario.check_password(password):
        return None, 'Usuario o contraseña incorrectos.'
        
    # Regla 3: La cuenta debe estar activa
    if not usuario.activo:
        return None, 'Esta cuenta ha sido desactivada por un Administrador.'
        
    return usuario, 'Login exitoso.'