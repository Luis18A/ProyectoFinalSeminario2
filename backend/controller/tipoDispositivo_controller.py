from database import db
from backend.models.TipoDispositivo import TipoDispositivo

class TipoDispositivoController:
    @staticmethod
    def crear_tipoDispositivo(datos_formulario):
        try:
            TipoDispositivo.crear(
                descripcion=datos_formulario.get('descripcion'),
                #activo=True if datos_formulario.get('estado') else False
            )
        except Exception as e:
            return False, f"Error al crear el tipo de dispositivo: {str(e)}"

    @staticmethod
    def obtener_todos():
        return TipoDispositivo.obtener_todos()

    @staticmethod
    def toggle_estado(tipo_dispositivo_id):
        tipo_dispositivo = TipoDispositivo.obtener_por_id(tipo_dispositivo_id)
        if tipo_dispositivo:
            tipo_dispositivo.activo = not tipo_dispositivo.activo # Cambia de True a False y viceversa
            db.session.commit()
            return True
        return False

    @staticmethod
    def eliminar_tipo_dispositivo(tipo_dispositivo_id):
        tipo_dispositivo = TipoDispositivo.obtener_por_id(tipo_dispositivo_id)
        if tipo_dispositivo:
            tipo_dispositivo.eliminar()
            return True
        return False

    @staticmethod
    def actualizar_tipoDispositivo(tipoDispositivo_id, datos_formulario):
        tipoDispositivo = TipoDispositivo.obtener_por_id(tipoDispositivo_id)
        if tipoDispositivo:
            tipoDispositivo.nombre = datos_formulario.get('nombre')
            tipoDispositivo.activo = True if datos_formulario.get('activo') else False
            db.session.commit()
            return True
        return False
