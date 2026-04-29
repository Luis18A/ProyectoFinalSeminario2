from database import db
from backend.models.Usuario import Usuario

class UsuarioController:
    @staticmethod
    def crear_usuario(datos_formulario):
        """
        Recibe los datos del formulario (request.form) y crea el usuario en la BD.
        """
        # La lógica de base de datos se queda aquí
        Usuario.crear(
            username=datos_formulario.get('username'),
            password=datos_formulario.get('password'),
            nombre=datos_formulario.get('nombre'),
            apellido=datos_formulario.get('apellido'),
            rol_id=datos_formulario.get('rol_id'),
            activo=True if datos_formulario.get('activo') else False
        )

    @staticmethod
    def obtener_todos():
        """
        Retorna la lista de todos los usuarios de la base de datos.
        """
        return Usuario.obtener_todos()

    @staticmethod
    def toggle_estado(usuario_id):
        usuario = Usuario.obtener_por_id(usuario_id)
        if usuario:
            usuario.activo = not usuario.activo # Cambia de True a False y viceversa
            db.session.commit()
            return True
        return False

    @staticmethod
    def eliminar_usuario(usuario_id):
        usuario = Usuario.obtener_por_id(usuario_id)
        if usuario:
            usuario.eliminar()
            return True
        return False
