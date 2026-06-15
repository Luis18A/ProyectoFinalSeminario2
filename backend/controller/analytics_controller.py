from database import db
from backend.models.OrdenServicio import OrdenServicio
from backend.models.Equipo import Equipo
from backend.models.Usuario import Usuario
from backend.models.HistorialEstado import HistorialEstado
from backend.models.EstadoOrden import EstadoOrden
from backend.utils.kmeans_service import KMeansService
from collections import Counter


class AnalyticsController:

    @staticmethod
    def obtener_datos_analytics():
        # ── OPTIMIZACIÓN: Eager loading para evitar N+1 queries ──
        # DEUDA TÉCNICA: Se resuelve el N+1 para equipo.tipo, pero si más adelante o en los
        # templates se accede a equipo.cliente, puede haber un N+1 residual. Aceptable para la entrega.
        from sqlalchemy.orm import joinedload
        ordenes = OrdenServicio.query.options(
            joinedload(OrdenServicio.equipo).joinedload(Equipo.tipo)
        ).all()
        total    = len(ordenes)

        # ── 1. Critical Failures ──────────────────────────────────────
        estados_activos = (
            EstadoOrden.PENDIENTE, EstadoOrden.DIAGNOSTICO,
            EstadoOrden.REPARACION, EstadoOrden.PRESUPUESTADO
        )
        critical_failures = sum(1 for o in ordenes if o.estado in estados_activos)

        # ── 2. Active Technicians ─────────────────────────────────────
        # CORRECCIÓN: sin fallback que distorsione la métrica
        active_tecnicos_count = sum(
            1 for u in Usuario.query.filter_by(activo=True).all()
            if u.rol and u.rol.descripcion == 'Técnico'
        )

        # ── 3. MTTR ───────────────────────────────────────────────────
        resueltas = [
            o for o in ordenes
            if o.estado in (EstadoOrden.LISTO, EstadoOrden.ENTREGADO)
            and o.fecha_entrega and o.fecha_recepcion
        ]
        if resueltas:
            avg_segundos = sum(
                (o.fecha_entrega - o.fecha_recepcion).total_seconds()
                for o in resueltas
            ) / len(resueltas)
            mttr = f"{avg_segundos / 3600:.1f}h"
        else:
            # CORRECCIÓN: sin inventar un número, mostrar estado real
            mttr = "Sin datos aún"

        # ── 4. System Integrity ───────────────────────────────────────
        if total > 0:
            historiales = HistorialEstado.query.all()
            tickets_con_retroceso = {
                h.orden_id for h in historiales
                if (h.estado_anterior == "Presupuestado" and h.estado_nuevo == "Diagnostico") or
                   (h.estado_anterior == "Reparacion"    and h.estado_nuevo == "Presupuestado")
            }
            integrity_val = ((total - len(tickets_con_retroceso)) / total) * 100
            system_integrity = f"{max(0.0, min(100.0, integrity_val)):.1f}%"
        else:
            system_integrity = "Sin datos aún"

        # ── 5. Incident Velocity (distribución por día de semana) ─────
        weekday_counts = [0] * 7
        for o in ordenes:
            if o.fecha_recepcion:
                weekday_counts[o.fecha_recepcion.weekday()] += 1

        max_c = max(weekday_counts) if any(weekday_counts) else 1
        weekday_percentages = [int((c / max_c) * 100) for c in weekday_counts]
        # CORRECCIÓN: sin datos inventados — si no hay órdenes, todo en cero
        # El template debe manejar el caso de lista en ceros

        # ── 6. Fault Logic (por tipo de dispositivo) ──────────────────
        tipos = [
            o.equipo.tipo.descripcion
            for o in ordenes
            if o.equipo and o.equipo.tipo
        ]
        tipo_counts  = Counter(tipos)
        total_equipos = sum(tipo_counts.values()) or 1

        fault_logic = sorted([
            {'nombre': t, 'porcentaje': int((c / total_equipos) * 100)}
            for t, c in tipo_counts.items()
        ], key=lambda x: x['porcentaje'], reverse=True)
        # CORRECCIÓN: lista vacía si no hay datos — el template mostrará "Sin datos"

        # ── 7. Recent Audit Logs ──────────────────────────────────────
        recent_history = (
            HistorialEstado.query
            .order_by(HistorialEstado.fecha_cambio.desc())
            .limit(10).all()
        )

        # ── 8. Financial ──────────────────────────────────────────────
        # CORRECCIÓN: sin fallback inventado ni gastos hardcodeados
        total_revenue = db.session.query(
            db.func.sum(OrdenServicio.costo)
        ).filter(
            OrdenServicio.estado.in_([EstadoOrden.LISTO, EstadoOrden.ENTREGADO])
        ).scalar() or 0.0
        total_revenue = float(total_revenue)

        total_expenses = 0.0
        for o in ordenes:
            if o.estado in (EstadoOrden.LISTO, EstadoOrden.ENTREGADO) and o.repuestos:
                for r in o.repuestos:
                    total_expenses += float(r.get('precio', 0.0))

        net_profit = total_revenue - total_expenses
        expense_percentage = (total_expenses / total_revenue * 100) if total_revenue > 0 else 0.0

        # ── 9. Active Tickets ─────────────────────────────────────────
        estados_todos_activos = (
            EstadoOrden.PENDIENTE, EstadoOrden.DIAGNOSTICO,
            EstadoOrden.REPARACION, EstadoOrden.PRESUPUESTADO,
            EstadoOrden.LISTO
        )
        active_tickets_count = sum(
            1 for o in ordenes if o.estado in estados_todos_activos
        )

        # ── 10. K-Means segmentation ──────────────────────────────────
        segmented_clients, kmeans_stats = KMeansService.get_client_segments()

        return {
            'critical_failures':      critical_failures,
            'active_tecnicos_count':  active_tecnicos_count,
            'mttr':                   mttr,
            'system_integrity':       system_integrity,
            'weekday_percentages':    weekday_percentages,
            'fault_logic':            fault_logic,
            'recent_history':         recent_history,
            'total_revenue':          total_revenue,
            'total_expenses':         total_expenses,
            'net_profit':             net_profit,
            'expense_percentage':     expense_percentage,
            'active_tickets_count':   active_tickets_count,
            'segmented_clients':      segmented_clients,
            'kmeans_stats':           kmeans_stats,
        }