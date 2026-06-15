from backend.models.OrdenServicio import OrdenServicio
from backend.models.EstadoOrden import EstadoOrden
from database import db
from sqlalchemy.orm.attributes import flag_modified

class OrdenPresupuestoController:
    @staticmethod
    def _recalcular_costo(orden, mano_obra):
        """Calcula el costo total sumando todos los repuestos y la mano de obra para evitar errores de redondeo."""
        repuestos = orden.repuestos or []
        total_repuestos = sum(float(r.get('precio', 0.0)) for r in repuestos)
        orden.costo = max(0.0, mano_obra + total_repuestos)

    @staticmethod
    def agregar_repuesto(orden_id, titulo, precio, link, tienda):
        """Agrega un repuesto al presupuesto del ticket de forma asíncrona y recalcula costo."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden de servicio no encontrada."
            
            if orden.estado not in (EstadoOrden.DIAGNOSTICO, EstadoOrden.REPARACION):
                return False, "No se pueden modificar repuestos en este estado del ticket."
            
            actuales = list(orden.repuestos or [])
            
            # Calcular mano de obra previa para preservarla
            old_sum = sum(float(r.get('precio', 0.0)) for r in actuales)
            mano_obra = max(0.0, float(orden.costo or 0.0) - old_sum)

            repuesto_data = {
                'titulo': titulo,
                'precio': float(precio),
                'link': link,
                'tienda': tienda
            }
            actuales.append(repuesto_data)
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
    def editar_repuesto(orden_id, idx, titulo, precio):
        """Modifica un repuesto del presupuesto del ticket y actualiza el costo total."""
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

                repuesto_data = dict(actuales[idx])
                repuesto_data['titulo'] = titulo
                repuesto_data['precio'] = float(precio)
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