from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from database import db
# DEUDA TÉCNICA: url_for requiere un contexto de aplicación Flask activo.
# Si este controller se llama fuera de un request context (tests, scripts) va a fallar.
# Se permite para la entrega actual de Seminario II, pero se debe documentar/refactorizar.
from flask import url_for # Permitido en controllers de presentación

class SearchController:
    @staticmethod
    def buscar_global(q):
        """Orquesta la búsqueda en múltiples dominios y formatea la salida."""
        # La regla de negocio de longitud se mudó aquí
        if not q or len(q) < 2 or len(q) > 100:
            return {'clientes': [], 'equipos': [], 'ordenes': []}

        return {
            'clientes': SearchController._buscar_clientes(q),
            'equipos':  SearchController._buscar_equipos(q),
            'ordenes':  SearchController._buscar_ordenes(q),
        }

    @staticmethod
    def _buscar_clientes(q):
        resultados = Cliente.query.filter(
            (Cliente.nombre.ilike(f"%{q}%")) | (Cliente.apellido.ilike(f"%{q}%")) | (Cliente.dni_cuil.ilike(f"%{q}%"))
        ).limit(5).all()
        return [{'id': c.id, 'nombre': f"{c.nombre} {c.apellido}", 'dni_cuil': c.dni_cuil, 'url': url_for('clientes.gestion_cliente', q=c.dni_cuil)} for c in resultados]

    @staticmethod
    def _buscar_equipos(q):
        resultados = Equipo.query.filter(
            (Equipo.marca.ilike(f"%{q}%")) | (Equipo.modelo.ilike(f"%{q}%")) | (Equipo.numero_serie.ilike(f"%{q}%"))
        ).limit(5).all()
        return [{'id': e.id, 'label': f"{e.marca} {e.modelo} (S/N: {e.numero_serie})", 'cliente_nombre': f"{e.cliente.nombre} {e.cliente.apellido}" if e.cliente else 'Sin cliente', 'url': url_for('equipo.gestion_equipos', cliente_id=e.cliente_id) if e.cliente_id else '#'} for e in resultados]

    @staticmethod
    def _buscar_ordenes(q):
        ordenes_res = []
        tk_id = q.upper().replace("TK-", "").strip()
        if tk_id.isdigit():
            orden = db.session.get(OrdenServicio, int(tk_id))
            if orden:
                ordenes_res.append(SearchController._formatear_orden(orden))

        resultados = OrdenServicio.query.join(Equipo).join(Cliente).filter(
            (OrdenServicio.falla_reportada.ilike(f"%{q}%")) | (Cliente.nombre.ilike(f"%{q}%")) | (Cliente.apellido.ilike(f"%{q}%")) | (Equipo.marca.ilike(f"%{q}%")) | (Equipo.modelo.ilike(f"%{q}%"))
        ).limit(5).all()

        ids_ya_agregados = {o['id'] for o in ordenes_res}
        for orden in resultados:
            if orden.id not in ids_ya_agregados:
                ordenes_res.append(SearchController._formatear_orden(orden))

        return ordenes_res[:5]

    @staticmethod
    def _formatear_orden(orden):
        return {'id': orden.id, 'codigo': f"TK-{orden.id:04d}", 'falla': orden.falla_reportada or 'Sin falla', 'estado': orden.estado.value if orden.estado else 'Desconocido', 'url': url_for('orden_servicio.gestionar_ticket', orden_id=orden.id)}
