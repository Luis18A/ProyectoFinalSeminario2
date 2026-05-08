from database import db
from backend.models.OrdenServicio import OrdenServicio
from backend.models.Equipo import Equipo
from backend.models.Usuario import Usuario

class OrdenServicioController:
    @staticmethod
    def crear_ordenServicio(datos_formulario):
        try:
            OrdenServicio.crear(
                equipo_id=int(datos_formulario.get('equipo_id')),
                usuario_id=int(datos_formulario.get('usuario_id')),
                activo=True if datos_formulario.get('activo') else False
            )
        except Exception as e:
            return False, f"Error al crear la orden de servicio: {str(e)}"

    @staticmethod
    def obtener_todos():
        return OrdenServicio.obtener_todos()

    @staticmethod
    def toggle_estado(orden_servicio_id):
        orden_servicio = OrdenServicio.obtener_por_id(orden_servicio_id)
        if orden_servicio:
            orden_servicio.activo = not orden_servicio.activo # Cambia de True a False y viceversa
            db.session.commit()
            return True
        return False

    @staticmethod
    def eliminar_orden_servicio(orden_servicio_id):
        orden_servicio = OrdenServicio.obtener_por_id(orden_servicio_id)
        if orden_servicio:
            orden_servicio.eliminar()
            return True
        return False

    @staticmethod
    def actualizar_ordenServicio(ordenServicio_id, datos_formulario):
        ordenServicio = OrdenServicio.obtener_por_id(ordenServicio_id)
        if ordenServicio:
            ordenServicio.equipo_id = int(datos_formulario.get('equipo_id'))
            ordenServicio.usuario_id = int(datos_formulario.get('usuario_id'))
            ordenServicio.activo = True if datos_formulario.get('activo') else False
            db.session.commit()
            return True
        return False

    @staticmethod
    def obtener_por_id(orden_servicio_id):
        return OrdenServicio.obtener_por_id(orden_servicio_id)

    @staticmethod
    def obtener_por_equipo(equipo_id):
        return OrdenServicio.obtener_por_equipo(equipo_id)

    @staticmethod
    def obtener_por_usuario(usuario_id):
        return OrdenServicio.obtener_por_usuario(usuario_id)