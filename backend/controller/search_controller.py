from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from database import db
from flask import url_for
from sqlalchemy.orm import joinedload

class SearchController:
    @staticmethod
    def buscar_global(q):
        """Orquesta la búsqueda en múltiples dominios y formatea la salida."""
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
        resultados = Equipo.query.options(
            joinedload(Equipo.cliente)
        ).filter(
            (Equipo.marca.ilike(f"%{q}%")) | (Equipo.modelo.ilike(f"%{q}%")) | (Equipo.numero_serie.ilike(f"%{q}%"))
        ).limit(5).all()
        return [{'id': e.id, 'label': f"{e.marca} {e.modelo} (S/N: {e.numero_serie})", 'cliente_nombre': f"{e.cliente.nombre} {e.cliente.apellido}" if e.cliente else 'Sin cliente', 'url': url_for('equipo.gestion_equipos', cliente_id=e.cliente_id) if e.cliente_id else '#'} for e in resultados]

    @staticmethod
    def _buscar_ordenes(q):
        ordenes_raw = []
        tk_id = q.upper().replace("TK-", "").strip()
        if tk_id.isdigit():
            orden = OrdenServicio.query.options(
                joinedload(OrdenServicio.equipo).joinedload(Equipo.cliente)
            ).filter(OrdenServicio.id == int(tk_id)).first()
            if orden:
                ordenes_raw.append(orden)

        resultados = OrdenServicio.query.options(
            joinedload(OrdenServicio.equipo).joinedload(Equipo.cliente)
        ).join(Equipo).join(Cliente).filter(
            (OrdenServicio.falla_reportada.ilike(f"%{q}%")) | (Cliente.nombre.ilike(f"%{q}%")) | (Cliente.apellido.ilike(f"%{q}%")) | (Equipo.marca.ilike(f"%{q}%")) | (Equipo.modelo.ilike(f"%{q}%"))
        ).limit(5).all()

        ids_ya_agregados = {o.id for o in ordenes_raw}
        for orden in resultados:
            if orden.id not in ids_ya_agregados:
                ordenes_raw.append(orden)

        ordenes_res = []
        for orden in ordenes_raw[:5]:
            cliente_nombre = "Sin cliente"
            equipo_desc = "Sin equipo"
            if orden.equipo:
                equipo_desc = f"{orden.equipo.marca} {orden.equipo.modelo}"
                if orden.equipo.cliente:
                    cliente_nombre = f"{orden.equipo.cliente.nombre} {orden.equipo.cliente.apellido}"
            
            ordenes_res.append({
                'id': orden.id,
                'codigo': f"TK-{orden.id:04d}",
                'cliente': cliente_nombre,
                'equipo': equipo_desc,
                'falla': orden.falla_reportada or 'Sin falla',
                'estado': orden.estado.value if orden.estado else 'Desconocido',
                'url': url_for('orden_servicio.gestionar_ticket', orden_id=orden.id)
            })

        return ordenes_res
