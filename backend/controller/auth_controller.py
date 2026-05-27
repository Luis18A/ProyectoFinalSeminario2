from backend.models.Usuario import Usuario
from database import db

class AuthController:
    @staticmethod
    def validar_login(username, password):
        # Buscamos al usuario en la base de datos por su username
        usuario = Usuario.obtener_por_username(username)
        
        if not usuario:
            return None, 'Usuario o contraseña incorrectos.'
            
        if not usuario.activo:
            if usuario.intentos_fallidos >= 5:
                return None, 'Esta cuenta ha sido bloqueada tras 5 intentos fallidos de inicio de sesión. Contacte al Administrador.'
            return None, 'Esta cuenta ha sido desactivada por un Administrador.'
            
        if not usuario.verificar_password(password):
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= 5:
                usuario.activo = False
                db.session.commit()
                return None, 'Esta cuenta ha sido bloqueada tras 5 intentos fallidos de inicio de sesión. Contacte al Administrador.'
            db.session.commit()
            intentos_restantes = 5 - usuario.intentos_fallidos
            return None, f'Usuario o contraseña incorrectos. Le quedan {intentos_restantes} intentos antes de bloquear la cuenta.'
            
        # Login exitoso
        usuario.intentos_fallidos = 0
        db.session.commit()
        return usuario, 'Usuario logueado correctamente.'
