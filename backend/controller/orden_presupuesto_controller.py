import logging
import uuid
from database import db
from backend.models import OrdenServicio, EstadoOrden, Repuesto, OrdenRepuesto

logger = logging.getLogger(__name__)

class OrdenPresupuestoController:
    @staticmethod
    def procesar_datos(datos_formulario, es_edicion=False):
        """
        Centraliza la validación y sanitización de datos de un repuesto.
        Retorna: (True, dict_con_datos_limpios) o (False, mensaje_de_error)
        """
        titulo = (datos_formulario.get('titulo') or '').strip()
        precio_raw = datos_formulario.get('precio')
        
        if not titulo:
            return False, "La descripción del repuesto es obligatoria."
        if len(titulo) < 3 or len(titulo) > 200:
            return False, "La descripción del repuesto debe tener entre 3 y 200 caracteres."
            
        try:
            if isinstance(precio_raw, str):
                precio_raw = precio_raw.replace(',', '.')
            precio = float(precio_raw) if precio_raw is not None else 0.0
            if precio < 0:
                return False, "El precio no puede ser negativo."
        except (TypeError, ValueError):
            return False, "El precio debe ser un número válido."

        datos = {
            'titulo': titulo,
            'precio': precio
        }

        if not es_edicion:
            datos['link'] = (datos_formulario.get('link') or '').strip() or '#'
            datos['tienda'] = (datos_formulario.get('tienda') or 'Manual').strip() or 'Manual'

        return True, datos

    @staticmethod
    def _recalcular_costo(orden, mano_obra):
        """Calcula el costo total sumando todos los repuestos y la mano de obra para evitar errores de redondeo."""
        orden.costo = max(0.0, mano_obra + orden.total_repuestos)

    @staticmethod
    def _obtener_mano_obra(orden):
        """Calcula la mano de obra actual restando el costo total de los repuestos al costo global."""
        return orden.mano_obra

    @staticmethod
    def agregar_repuesto(orden_id, **datos_formulario):
        """Agrega un repuesto al presupuesto del ticket de forma asíncrona y recalcula costo."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden de servicio no encontrada."
            
            if orden.estado not in (EstadoOrden.DIAGNOSTICO, EstadoOrden.REPARACION):
                return False, "No se pueden modificar repuestos en este estado del ticket."
            
            success, result = OrdenPresupuestoController.procesar_datos(datos_formulario, es_edicion=False)
            if not success:
                return False, result

            # Calcular mano de obra previa para preservarla
            mano_obra = OrdenPresupuestoController._obtener_mano_obra(orden)

            # Buscar o crear Repuesto en el catálogo (Insensible a mayúsculas)
            titulo = result['titulo']
            precio = result['precio']
            tienda = result.get('tienda', 'Manual')
            
            # Optimización: Evita duplicados por diferencias de tipeo
            rep_db = Repuesto.query.filter(Repuesto.descripcion.ilike(titulo)).first()
            if not rep_db:
                # Generar código único para el catálogo
                codigo = f"REP-{uuid.uuid4().hex[:12].upper()}"
                rep_db = Repuesto(
                    codigo=codigo,
                    descripcion=titulo,
                    categoria="Hardware",
                    precio_promedio=precio,
                    proveedor=tienda,
                    activo=True
                )
                db.session.add(rep_db)
                db.session.flush()

            # Verificar si ya existe este repuesto asociado en la orden
            orden_rep = OrdenRepuesto.query.filter_by(orden_id=orden_id, repuesto_id=rep_db.id).first()
            if orden_rep:
                orden_rep.cantidad += 1
                orden_rep.precio_unitario = precio
            else:
                orden_rep = OrdenRepuesto(
                    orden_id=orden.id,
                    repuesto_id=rep_db.id,
                    cantidad=1,
                    precio_unitario=precio
                )
                db.session.add(orden_rep)
            
            db.session.flush()

            # Recalcular costo consolidado
            OrdenPresupuestoController._recalcular_costo(orden, mano_obra)
            
            db.session.commit()

            # Devolver el repuesto insertado/actualizado para que el frontend actualice su array
            rep_json = {
                'id': orden_rep.id,
                'repuesto_id': rep_db.id,
                'codigo': rep_db.codigo,
                'titulo': rep_db.descripcion,
                'precio': float(orden_rep.precio_unitario),
                'cantidad': orden_rep.cantidad,
                'link': result.get('link', '#'),
                'tienda': rep_db.proveedor or 'Manual'
            }
            return True, rep_json
        except Exception as e:
            db.session.rollback()
            return False, f"Error al agregar repuesto: {str(e)}"

    @staticmethod
    def editar_repuesto(orden_id, orden_repuesto_id, **datos_formulario):
        """Modifica un repuesto del presupuesto del ticket y actualiza el costo total."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden de servicio no encontrada."
            
            if orden.estado not in (EstadoOrden.DIAGNOSTICO, EstadoOrden.REPARACION):
                return False, "No se pueden modificar repuestos en este estado del ticket."
            
            success, result = OrdenPresupuestoController.procesar_datos(datos_formulario, es_edicion=True)
            if not success:
                return False, result

            orden_rep = OrdenRepuesto.query.filter_by(id=orden_repuesto_id, orden_id=orden_id).first()
            if not orden_rep:
                return False, "Relación de repuesto no encontrada."

            # Calcular mano de obra previa para preservarla
            mano_obra = OrdenPresupuestoController._obtener_mano_obra(orden)

            # Actualizar
            orden_rep.precio_unitario = result['precio']
            orden_rep.repuesto.descripcion = result['titulo']
            orden_rep.repuesto.precio_promedio = result['precio']

            # Recalcular costo consolidado
            OrdenPresupuestoController._recalcular_costo(orden, mano_obra)
            
            db.session.commit()
            return True, "Repuesto editado correctamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al editar repuesto: {str(e)}"

    @staticmethod
    def eliminar_repuesto(orden_id, orden_repuesto_id):
        """Elimina un repuesto del presupuesto del ticket y decrementa el costo total."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden de servicio no encontrada."
            
            if orden.estado not in (EstadoOrden.DIAGNOSTICO, EstadoOrden.REPARACION):
                return False, "No se pueden modificar repuestos en este estado del ticket."

            orden_rep = OrdenRepuesto.query.filter_by(id=orden_repuesto_id, orden_id=orden_id).first()
            if not orden_rep:
                return False, "Relación de repuesto no encontrada."

            # Calcular mano de obra previa para preservarla
            mano_obra = OrdenPresupuestoController._obtener_mano_obra(orden)

            # Eliminar relacion
            db.session.delete(orden_rep)
            db.session.flush()

            # Recalcular costo consolidado
            OrdenPresupuestoController._recalcular_costo(orden, mano_obra)
            
            db.session.commit()
            return True, "Repuesto removido correctamente del presupuesto."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al eliminar repuesto: {str(e)}"

    @staticmethod
    def iniciar_busqueda_repuestos(q):
        """Inicia la búsqueda de repuestos en segundo plano utilizando Hilos locales."""
        q = (q or '').strip()
        if not q:
            return False, 'El término de búsqueda está vacío'
        
        from backend.utils.tasks import iniciar_busqueda_hilos
        task_id = iniciar_busqueda_hilos(q)
        return True, {'task_id': task_id, 'status': 'pending'}

    @staticmethod
    def obtener_estado_busqueda_repuestos(task_id):
        """Consulta el estado de la tarea de búsqueda asíncrona en Hilos locales."""
        if str(task_id).startswith('thread-'):
            from backend.utils.tasks import obtener_estado_busqueda_hilos
            return obtener_estado_busqueda_hilos(task_id)
        return False, "ID de tarea inválido para hilos locales"