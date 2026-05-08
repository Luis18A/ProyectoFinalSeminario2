from database import db
from backend.models.Equipo import Equipo
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.Usuario import Usuario

class EquipoController:
    @staticmethod
    def crear_equipo(datos_formulario):
        try:
            Equipo.crear(
                nombre=datos_formulario.get('nombre'),
                tipo_dispositivo_id=int(datos_formulario.get('tipo_dispositivo_id')),
                usuario_id=int(datos_formulario.get('usuario_id')),
                activo=True if datos_formulario.get('activo') else False
            )
        except Exception as e:
            return False, f"Error al crear el equipo: {str(e)}"

    @staticmethod
    def obtener_todos():
        return Equipo.obtener_todos()

    @staticmethod
    def toggle_estado(equipo_id):
        equipo = Equipo.obtener_por_id(equipo_id)
        if equipo:
            equipo.activo = not equipo.activo # Cambia de True a False y viceversa
            db.session.commit()
            return True
        return False

    @staticmethod
    def eliminar_equipo(equipo_id):
        equipo = Equipo.obtener_por_id(equipo_id)
        if equipo:
            equipo.eliminar()
            return True
        return False

    @staticmethod
    def actualizar_equipo(equipo_id, datos_formulario):
        equipo = Equipo.obtener_por_id(equipo_id)
        if equipo:
            equipo.nombre = datos_formulario.get('nombre')
            equipo.tipo_dispositivo_id = int(datos_formulario.get('tipo_dispositivo_id'))
            equipo.usuario_id = int(datos_formulario.get('usuario_id'))
            equipo.activo = True if datos_formulario.get('activo') else False
            db.session.commit()
            return True
        return False

    @staticmethod
    def obtener_por_id(equipo_id):
        return Equipo.obtener_por_id(equipo_id)

    @staticmethod
    def obtener_por_usuario(usuario_id):
        return Equipo.obtener_por_usuario(usuario_id)