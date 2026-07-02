from backend.models.Usuario import Usuario
from database import db

class AuthController:

    @staticmethod
    def validar_login(username, password):
        """
        Valida credenciales y gestiona el contador de intentos fallidos.
        """
        if not username or len(username) > 80:
            return None, 'Usuario o contraseña incorrectos.'
        if not password or len(password) > 100:
            return None, 'Usuario o contraseña incorrectos.'

        try:
            # 1. Búsqueda con manejo de errores de conexión
            usuario = Usuario.get_por_username(username)
            
            # Simulamos usuario "dummy" si no existe para evitar timing attacks
            # pero para mantenerlo simple y seguro, seguiremos con tu lógica actual:
            if not usuario:
                return None, 'Usuario o contraseña incorrectos.'

            # 2. Verificación de contraseña (el costo computacional es el mismo)
            password_correcto = usuario.verificar_password(password)

            # 3. Estado de la cuenta
            if not usuario.activo:
                if usuario.intentos_fallidos >= Usuario.MAX_INTENTOS_FALLIDOS:
                    return None, 'Cuenta bloqueada por intentos fallidos. Contactá al admin.'
                return None, 'Esta cuenta fue desactivada.'

            if not password_correcto:
                usuario.registrar_intento_fallido()
                db.session.commit()
                return None, 'Usuario o contraseña incorrectos.'

            # 4. Login exitoso
            usuario.resetear_intentos()
            db.session.commit()
            return usuario, 'Login exitoso.'

        except Exception as e:
            # En caso de error de BD, el usuario no debe ver el error técnico
            db.session.rollback()
            return None, 'Error interno del sistema. Intentá más tarde.'

    @staticmethod
    def validar_login_completo(username, password):
        """
        Valida las credenciales completas y retorna la información segura de sesión.
        Retorna: (True, dict_con_datos_usuario) o (False, mensaje_de_error)
        """
        usuario, mensaje = AuthController.validar_login(username, password)
        if not usuario:
            return False, mensaje

        rol_descripcion = ''
        try:
            rol_descripcion = usuario.rol.descripcion
        except Exception:
            pass

        return True, {
            'id': usuario.id,
            'username': usuario.username,
            'rol': rol_descripcion
        }