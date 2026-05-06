from backend.models.Usuario import Usuario

class AuthController:
    @staticmethod
    def validar_login(username, password):
        # Buscamos al usuario en la base de datos por su username
        usuario = Usuario.query.filter_by(username=username).first()
        # Si el usuario existe y la contraseña es correcta
        if usuario and usuario.verificar_password(password):
            return usuario
        return None
