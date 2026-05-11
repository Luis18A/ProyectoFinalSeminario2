from backend.models.HistorialEstado import HistorialEstado
from backend.models.EstadoOrden import EstadoOrden
from backend.models.OrdenServicio import OrdenServicio
from database import db

class OrdenServicioController:
    @staticmethod
    def crear_ordenServicio(datos_formulario):
        """Crea una nueva orden y registra el ingreso en el historial."""
        try:
            # 1. Creamos la orden usando el método del modelo
            # El estado por defecto ya es PENDIENTE según el modelo
            nueva_orden = OrdenServicio.create(
                equipo_id=int(datos_formulario.get('equipo_id')),
                usuario_id=int(datos_formulario.get('usuario_id')),
                falla_reportada=datos_formulario.get('falla_reportada'),
                accesorios=datos_formulario.get('accesorios'),
                costo=float(datos_formulario.get('costo', 0))
            )

            # 2. Registramos el ingreso en el historial
            HistorialEstado.add_registro(
                orden_id=nueva_orden.id,
                estado_anterior="Ingreso",
                estado_nuevo=EstadoOrden.PENDIENTE.value,
                usuario_id=nueva_orden.usuario_id,
                observacion_tecnica="Ingreso del equipo al taller."
            )
            
            return True, "Orden de servicio creada exitosamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al crear la orden de servicio: {str(e)}"

    @staticmethod
    def actualizar_ordenServicio(orden_id, datos_formulario):
        """Actualiza la orden y maneja el cambio de estado con historial."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden no encontrada."

            # Capturamos datos del formulario
            nuevo_estado_id = datos_formulario.get('estado')
            usuario_id = int(datos_formulario.get('usuario_id'))
            observacion = datos_formulario.get('observaciones')
            costo = datos_formulario.get('costo')

            estado_anterior_nombre = orden.estado.value
            estado_nuevo_nombre = orden.estado.value
            hubo_cambios = False

            # 1. Si el estado cambió
            if nuevo_estado_id and nuevo_estado_id != orden.estado.name:
                try:
                    # Asignamos el nuevo Enum basándonos en el nombre
                    orden.estado = EstadoOrden[nuevo_estado_id]
                    estado_nuevo_nombre = orden.estado.value
                    hubo_cambios = True
                except KeyError:
                    return False, f"Estado '{nuevo_estado_id}' no es válido."
                    
            # 2. Si hay un costo nuevo, lo actualizamos
            if costo:
                orden.costo = float(costo)
                hubo_cambios = True
                
            # Actualizamos otros campos técnicos
            orden.estado_diagnostico = datos_formulario.get('estado_diagnostico')
            orden.falla_reportada = datos_formulario.get('falla_reportada')
            orden.accesorios = datos_formulario.get('accesorios')

            # 3. Si hubo algún cambio físico o el técnico dejó una nota, grabamos el historial
            if hubo_cambios or observacion:
                historial = HistorialEstado(
                    orden_id=orden.id,
                    usuario_id=usuario_id,
                    estado_anterior=estado_anterior_nombre,
                    estado_nuevo=estado_nuevo_nombre,
                    observacion_tecnica=observacion
                )
                db.session.add(historial)
                
            db.session.commit()
            return True, 'Ticket actualizado correctamente.'
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar la orden: {str(e)}"

    @staticmethod
    def obtener_todos():
        """Obtiene todas las órdenes de servicio."""
        return OrdenServicio.get_all()

    @staticmethod
    def obtener_por_id(orden_id):
        """Obtiene una orden específica por su ID."""
        return OrdenServicio.get_by_id(orden_id)

    @staticmethod
    def obtener_historial(orden_id):
        """Obtiene el historial cronológico de un ticket."""
        return HistorialEstado.get_historial_tickets(orden_id)

    @staticmethod
    def eliminar_orden_servicio(orden_id):
        """Elimina una orden de servicio."""
        orden = OrdenServicio.get_by_id(orden_id)
        if orden:
            orden.delete()
            return True
        return False

    @staticmethod
    def obtener_por_usuario(usuario_id):
        """Obtiene órdenes asignadas a un usuario."""
        return OrdenServicio.get_por_usuario(usuario_id)

    @staticmethod
    def obtener_por_estado(estado_name):
        """Obtiene órdenes filtradas por su estado (Enum name)."""
        try:
            estado_enum = EstadoOrden[estado_name]
            return OrdenServicio.query.filter_by(estado=estado_enum).all()
        except KeyError:
            return []