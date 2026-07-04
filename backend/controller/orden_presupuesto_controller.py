import logging
from backend.models.OrdenServicio import OrdenServicio
from backend.models.EstadoOrden import EstadoOrden
from backend.models.Repuesto import Repuesto
from backend.models.OrdenRepuesto import OrdenRepuesto
from database import db
from sqlalchemy.orm.attributes import flag_modified
import uuid
import threading
import asyncio
from backend.utils.tasks import _ejecutar_scrapers

import time

logger = logging.getLogger(__name__)

# Almacén de tareas de búsqueda en memoria para simular Celery localmente
_tareas_busqueda = {}
_tareas_lock = threading.Lock()

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
        total_repuestos = sum(float(orp.precio_unitario) * orp.cantidad for orp in orden.orden_repuestos)
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

            # Calcular mano de obra previa para preservarla
            old_sum = sum(float(orp.precio_unitario) * orp.cantidad for orp in orden.orden_repuestos)
            mano_obra = max(0.0, float(orden.costo or 0.0) - old_sum)

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
            old_sum = sum(float(orp.precio_unitario) * orp.cantidad for orp in orden.orden_repuestos)
            mano_obra = max(0.0, float(orden.costo or 0.0) - old_sum)

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
            old_sum = sum(float(orp.precio_unitario) * orp.cantidad for orp in orden.orden_repuestos)
            mano_obra = max(0.0, float(orden.costo or 0.0) - old_sum)

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
        """Inicia la búsqueda en un hilo de fondo simulando Celery localmente con prevención de memory leaks."""
        q = (q or '').strip()
        if not q:
            return False, 'El término de búsqueda está vacío'
        
        task_id = str(uuid.uuid4())
        ahora = time.time()

        with _tareas_lock:
            # Purgar búsquedas de más de 15 minutos (900 segundos) para evitar memory leaks
            for tid in list(_tareas_busqueda.keys()):
                if ahora - _tareas_busqueda[tid].get('timestamp', 0) > 900:
                    _tareas_busqueda.pop(tid, None)
                    
            _tareas_busqueda[task_id] = {
                'status': 'running', 
                'results': [],
                'timestamp': ahora
            }

        # Ejecutamos la búsqueda en un hilo separado
        def run_search():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(_ejecutar_scrapers(q))
                loop.close()
                
                with _tareas_lock:
                    if task_id in _tareas_busqueda:
                        _tareas_busqueda[task_id]['status'] = 'completed'
                        _tareas_busqueda[task_id]['results'] = results
            except Exception as e:
                # INFRAESTRUCTURA: Uso de logger en hilos de fondo
                logger.error(f"[Scraper Thread] Error al ejecutar búsqueda asíncrona: {e}")
                with _tareas_lock:
                    if task_id in _tareas_busqueda:
                        _tareas_busqueda[task_id]['status'] = 'failed'
                        _tareas_busqueda[task_id]['error'] = str(e)

        threading.Thread(target=run_search, daemon=True).start()
        return True, {'task_id': task_id, 'status': 'pending'}

    @staticmethod
    def obtener_estado_busqueda_repuestos(task_id):
        """Consulta el estado de la tarea en memoria de forma segura."""
        with _tareas_lock:
            task = _tareas_busqueda.get(task_id)
            
        if not task:
            return False, 'Tarea no encontrada o expirada de memoria.'
        
        if task['status'] == 'completed':
            return True, {'status': 'completed', 'results': task['results']}
        elif task['status'] == 'failed':
            return False, task.get('error', 'Error en la búsqueda del repuesto')
        else:
            return True, {'status': 'running'}