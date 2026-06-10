from database import db
from backend.models.Usuario import Usuario

class UsuarioController:
    @staticmethod
    def crear_usuario(datos_formulario):
        """
        Recibe los datos del formulario (request.form) y crea el usuario en la BD.
        """
        try:
            username = datos_formulario.get('username')
            if not username:
                return False, "El nombre de usuario es requerido."
            username = username.strip().lower()
            
            if Usuario.obtener_por_username(username):
                return False, "El nombre de usuario ya existe."

            Usuario.crear(
                username=username,
                password=datos_formulario.get('password'),
                nombre=datos_formulario.get('nombre'),
                apellido=datos_formulario.get('apellido'),
                rol_id=int(datos_formulario.get('rol_id')),
                activo=True if datos_formulario.get('activo') else False
            )
            return True, "Usuario creado correctamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al crear el usuario: {str(e)}"

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

    @staticmethod
    def actualizar_usuario(usuario_id, datos_formulario):
        try:
            usuario = Usuario.obtener_por_id(usuario_id)
            if not usuario:
                return False, "Usuario no encontrado."
                
            username = datos_formulario.get('username')
            if not username:
                return False, "El nombre de usuario es requerido."
            username = username.strip().lower()
            
            existente = Usuario.obtener_por_username(username)
            if existente and existente.id != usuario_id:
                return False, "El nombre de usuario ya existe."
                
            usuario.username = username
            usuario.nombre = datos_formulario.get('nombre')
            usuario.apellido = datos_formulario.get('apellido')
            usuario.rol_id = int(datos_formulario.get('rol_id'))
            usuario.activo = True if datos_formulario.get('activo') else False
            
            # Solo actualizar contraseña si no viene vacía
            password = datos_formulario.get('password')
            if password and password.strip():
                from werkzeug.security import generate_password_hash
                usuario.password = generate_password_hash(password)
            
            db.session.commit()
            return True, "Usuario actualizado correctamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar el usuario: {str(e)}"

    @staticmethod
    def obtener_datos_secretaria():
        """
        Retorna clientes, usuarios y ordenes para la vista de secretaria.
        """
        from backend.models.Cliente import Cliente
        from backend.models.OrdenServicio import OrdenServicio
        clientes = Cliente.query.all()
        usuarios = Usuario.obtener_todos()
        ordenes = OrdenServicio.get_all()
        return clientes, usuarios, ordenes


