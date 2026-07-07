from database import db
from backend.models.OrdenServicio import OrdenServicio
from backend.models.Equipo import Equipo
from backend.models.Usuario import Usuario
from backend.models.HistorialEstado import HistorialEstado
from backend.models.EstadoOrden import EstadoOrden
from backend.models.Rol import Rol
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.OrdenRepuesto import OrdenRepuesto
from backend.utils.kmeans_service import KMeansService
from sqlalchemy import func

class AnalyticsController:

    @staticmethod
    def obtener_datos_analytics():

        # ── 1. Total & Critical Failures ──────────────────────────────
        total = OrdenServicio.query.count()
        
        estados_activos = (
            EstadoOrden.PENDIENTE, EstadoOrden.DIAGNOSTICO,
            EstadoOrden.REPARACION, EstadoOrden.PRESUPUESTADO
        )
        critical_failures = db.session.query(OrdenServicio).filter(
            OrdenServicio.estado.in_(estados_activos)
        ).count()

        # ── 2. Active Technicians ─────────────────────────────────────
        active_tecnicos_count = db.session.query(Usuario).join(Rol).filter(
            Usuario.activo == True,
            func.lower(Rol.descripcion).in_(['técnico', 'tecnico'])
        ).count()

        # ── 3. MTTR ───────────────────────────────────────────────────
        # Optimización: Cálculo directo en base de datos para evitar cargar todas las filas en memoria.
        dialect_name = db.engine.dialect.name
        if dialect_name == 'postgresql':
            avg_seconds_query = db.session.query(
                func.avg(func.extract('epoch', OrdenServicio.fecha_entrega - OrdenServicio.fecha_recepcion))
            )
        else:
            # SQLite fallback: Cálculo mediante julianday
            avg_seconds_query = db.session.query(
                func.avg((func.julianday(OrdenServicio.fecha_entrega) - func.julianday(OrdenServicio.fecha_recepcion)) * 86400)
            )

        avg_segundos = avg_seconds_query.filter(
            OrdenServicio.estado.in_([EstadoOrden.LISTO, EstadoOrden.ENTREGADO]),
            OrdenServicio.fecha_entrega.isnot(None),
            OrdenServicio.fecha_recepcion.isnot(None)
        ).scalar()

        if avg_segundos is not None:
            dias = float(avg_segundos) / 86400
            if round(dias, 1) == 1.0:
                mttr = "1.0 día"
            else:
                mttr = f"{dias:.1f} días"
        else:
            mttr = "Sin datos aún"

        # ── 4. System Integrity ───────────────────────────────────────
        if total > 0:
            tickets_con_retroceso_count = db.session.query(HistorialEstado.orden_id).filter(
                db.or_(
                    db.and_(HistorialEstado.estado_anterior == "Presupuestado", HistorialEstado.estado_nuevo == "Diagnostico"),
                    db.and_(HistorialEstado.estado_anterior == "Reparacion", HistorialEstado.estado_nuevo == "Presupuestado")
                )
            ).distinct().count()
            integrity_val = ((total - tickets_con_retroceso_count) / total) * 100
            system_integrity = f"{max(0.0, min(100.0, integrity_val)):.1f}%"
        else:
            system_integrity = "Sin datos aún"

        # ── 5. Incident Velocity (distribución por día de semana - Estilo Pareto) ─────
        # Optimización: Agrupamiento directo en base de datos (GROUP BY) en lugar de en memoria.
        dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        weekday_counts = [0] * 7

        dialect_name = db.engine.dialect.name
        if dialect_name == 'postgresql':
            # dow: 0 para Domingo, 1 para Lunes, ..., 6 para Sábado
            day_expr = func.extract('dow', OrdenServicio.fecha_recepcion)
        else:
            # SQLite: %w (0 para Domingo, 1 para Lunes, ..., 6 para Sábado)
            day_expr = func.strftime('%w', OrdenServicio.fecha_recepcion)

        counts_query = db.session.query(
            day_expr.label('day'),
            func.count(OrdenServicio.id)
        ).filter(
            OrdenServicio.fecha_recepcion.isnot(None)
        ).group_by(day_expr).all()

        for day, count in counts_query:
            if day is not None:
                day_int = int(day)
                # Mapear Domingo (0) al índice 6 y Lunes (1) al índice 0, etc.
                idx = (day_int - 1) % 7
                weekday_counts[idx] = count

        total_incidentes = sum(weekday_counts)
        pareto_data = []
        for i, count in enumerate(weekday_counts):
            pct = (count / total_incidentes * 100) if total_incidentes > 0 else 0.0
            pareto_data.append({
                'dia': dias_semana[i],
                'cantidad': count,
                'porcentaje': round(pct, 1)
            })

        # Ordenar de mayor a menor por cantidad
        pareto_data = sorted(pareto_data, key=lambda x: x['cantidad'], reverse=True)

        # Calcular porcentaje acumulado basado en conteos acumulados
        running_count = 0
        for item in pareto_data:
            if total_incidentes > 0:
                running_count += item['cantidad']
                item['acumulado'] = round((running_count / total_incidentes) * 100, 1)
            else:
                item['acumulado'] = 0.0

        # ── 6. Fault Logic (por tipo de dispositivo) ──────────────────
        resultados_dispositivos = db.session.query(
            TipoDispositivo.descripcion,
            db.func.count(OrdenServicio.id)
        ).join(OrdenServicio.equipo)\
         .join(Equipo.tipo)\
         .group_by(TipoDispositivo.descripcion).all()

        total_equipos = sum(count for _, count in resultados_dispositivos) or 1

        fault_logic = sorted([
            {'nombre': desc, 'porcentaje': int((count / total_equipos) * 100)}
            for desc, count in resultados_dispositivos
        ], key=lambda x: x['porcentaje'], reverse=True)

        # ── 7. Recent Audit Logs ──────────────────────────────────────
        recent_history = (
            HistorialEstado.query
            .order_by(HistorialEstado.fecha_cambio.desc())
            .limit(10).all()
        )

        # ── 8. Financial ──────────────────────────────────────────────
        total_revenue = db.session.query(
            db.func.sum(OrdenServicio.costo)
        ).filter(
            OrdenServicio.estado.in_([EstadoOrden.LISTO, EstadoOrden.ENTREGADO])
        ).scalar() or 0.0
        total_revenue = float(total_revenue)

        total_expenses = db.session.query(
            db.func.sum(OrdenRepuesto.precio_unitario * OrdenRepuesto.cantidad)
        ).join(OrdenServicio).filter(
            OrdenServicio.estado.in_([EstadoOrden.LISTO, EstadoOrden.ENTREGADO])
        ).scalar() or 0.0
        total_expenses = float(total_expenses)

        net_profit = total_revenue - total_expenses
        expense_percentage = (total_expenses / total_revenue * 100) if total_revenue > 0 else 0.0

        # ── 9. Active Tickets ─────────────────────────────────────────
        estados_todos_activos = (
            EstadoOrden.PENDIENTE, EstadoOrden.DIAGNOSTICO,
            EstadoOrden.REPARACION, EstadoOrden.PRESUPUESTADO,
            EstadoOrden.LISTO
        )
        active_tickets_count = db.session.query(OrdenServicio).filter(
            OrdenServicio.estado.in_(estados_todos_activos)
        ).count()

        # ── 10. K-Means segmentation ──────────────────────────────────
        segmented_clients, kmeans_stats = KMeansService.get_client_segments()

        return {
            'critical_failures':      critical_failures,
            'active_tecnicos_count':  active_tecnicos_count,
            'mttr':                   mttr,
            'system_integrity':       system_integrity,
            'pareto_data':            pareto_data,
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