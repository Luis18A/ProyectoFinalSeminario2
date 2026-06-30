from backend.models.OrdenServicio import OrdenServicio
from backend.models.EstadoOrden import EstadoOrden
from database import db
from sqlalchemy.orm.attributes import flag_modified

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
        repuestos = orden.repuestos or []
        total_repuestos = sum(float(r.get('precio', 0.0)) for r in repuestos)
        orden.costo = max(0.0, mano_obra + total_repuestos)

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

            actuales = list(orden.repuestos or [])
            
            # Calcular mano de obra previa para preservarla
            old_sum = sum(float(r.get('precio', 0.0)) for r in actuales)
            mano_obra = max(0.0, float(orden.costo or 0.0) - old_sum)

            actuales.append(result)
            orden.repuestos = actuales
            flag_modified(orden, 'repuestos')
            
            # Recalcular costo consolidado
            OrdenPresupuestoController._recalcular_costo(orden, mano_obra)
            
            db.session.commit()
            return True, "Repuesto agregado correctamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al agregar repuesto: {str(e)}"

    @staticmethod
    def editar_repuesto(orden_id, idx, **datos_formulario):
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

            actuales = list(orden.repuestos or [])
            if 0 <= idx < len(actuales):
                # Calcular mano de obra previa para preservarla
                old_sum = sum(float(r.get('precio', 0.0)) for r in actuales)
                mano_obra = max(0.0, float(orden.costo or 0.0) - old_sum)

                repuesto_data = dict(actuales[idx])
                repuesto_data.update(result)
                actuales[idx] = repuesto_data
                orden.repuestos = actuales
                flag_modified(orden, 'repuestos')

                # Recalcular costo consolidado
                OrdenPresupuestoController._recalcular_costo(orden, mano_obra)
                
                db.session.commit()
                return True, "Repuesto editado correctamente."
            return False, "Índice de repuesto inválido."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al editar repuesto: {str(e)}"

    @staticmethod
    def eliminar_repuesto(orden_id, idx):
        """Elimina un repuesto del presupuesto del ticket y decrementa el costo total."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden de servicio no encontrada."
            
            if orden.estado not in (EstadoOrden.DIAGNOSTICO, EstadoOrden.REPARACION):
                return False, "No se pueden modificar repuestos en este estado del ticket."
            
            actuales = list(orden.repuestos or [])
            if 0 <= idx < len(actuales):
                # Calcular mano de obra previa para preservarla
                old_sum = sum(float(r.get('precio', 0.0)) for r in actuales)
                mano_obra = max(0.0, float(orden.costo or 0.0) - old_sum)

                actuales.pop(idx)
                orden.repuestos = actuales
                flag_modified(orden, 'repuestos')

                # Recalcular costo consolidado
                OrdenPresupuestoController._recalcular_costo(orden, mano_obra)
                
                db.session.commit()
                return True, "Repuesto removido correctamente del presupuesto."
            return False, "Índice de repuesto inválido."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al eliminar repuesto: {str(e)}"

    @staticmethod
    def iniciar_busqueda_repuestos(q):
        """Inicia la tarea asíncrona en Celery y retorna el ID de la tarea."""
        from backend.tasks import buscar_repuestos_async
        q = (q or '').strip()
        if not q:
            return False, 'El término de búsqueda está vacío'
        try:
            task = buscar_repuestos_async.delay(q)
            return True, {'task_id': task.id, 'status': 'pending'}
        except Exception as e:
            print(f"[Controller] Error al iniciar tarea Celery: {e}")
            return False, str(e)

    @staticmethod
    def obtener_estado_busqueda_repuestos(task_id):
        """Consulta el estado de una tarea Celery y retorna su resultado o estado."""
        from backend.tasks import celery
        try:
            res = celery.AsyncResult(task_id)
            if res.state == 'SUCCESS':
                return True, {'status': 'completed', 'results': res.result}
            elif res.state in ('PENDING', 'STARTED', 'PROGRESS', 'RETRY'):
                return True, {'status': 'running'}
            else:
                error_msg = str(res.info) if res.info else 'Error en la ejecución de la tarea'
                return False, error_msg
        except Exception as e:
            print(f"[Controller] Error al consultar estado Celery: {e}")
            return False, str(e)