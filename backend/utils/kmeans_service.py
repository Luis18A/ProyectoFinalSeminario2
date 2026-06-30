import numpy as np
from datetime import datetime, timedelta, timezone
from sklearn.cluster import KMeans

from backend.models.Cliente import Cliente
from backend.models.OrdenServicio import OrdenServicio
from backend.models.EstadoOrden import EstadoOrden
from backend.models.Equipo import Equipo
from database import db
from sqlalchemy import func


class KMeansService:
    _cached_result = None
    _last_update = None

    @classmethod
    def invalidate_cache(cls):
        """Invalida la caché del K-Means."""
        cls._cached_result = None
        cls._last_update = None

    @classmethod
    def get_client_segments(cls):
        """
        Ejecuta minería de datos (K-Means) en pure Python para segmentar clientes.
        Retorna la lista de clientes segmentados y estadísticas generales de cada clúster.

        K se adapta dinámicamente a la cantidad de clientes disponibles (mínimo 1, máximo 3).
        No se agregan datos sintéticos — si hay pocos clientes, se segmenta con K reducido.
        Eje X: Ordenes de servico, Eje Y: Gasto total de ordenes de servico
        """
        # Caché con TTL de 5 minutos
        # CORRECCIÓN: datetime.now(timezone.utc) reemplaza utcnow() deprecado en Python 3.12+
        ahora = datetime.now(timezone.utc)
        if (cls._cached_result and cls._last_update and
                (ahora - cls._last_update) < timedelta(minutes=5)):
            return cls._cached_result[0], cls._cached_result[1]

        stats_vacias = {
            "Platinum": {"count": 0, "total_gasto": 0.0, "avg_frecuencia": 0.0},
            "Activo":   {"count": 0, "total_gasto": 0.0, "avg_frecuencia": 0.0},
            "Casual":   {"count": 0, "total_gasto": 0.0, "avg_frecuencia": 0.0},
        }

        # ── Query optimizada: frecuencia y gasto en una sola consulta ────────
        db_stats = (
            db.session.query(
                Cliente.id,
                Cliente.nombre,
                Cliente.apellido,
                Cliente.dni_cuil,
                func.count(OrdenServicio.id).label('frecuencia'),
                func.sum(
                    db.case(
                        (OrdenServicio.estado.in_([EstadoOrden.LISTO, EstadoOrden.ENTREGADO]),
                         OrdenServicio.costo),
                        else_=0.0
                    )
                ).label('gasto')
            )
            .select_from(Cliente)
            .outerjoin(Equipo, Cliente.id == Equipo.cliente_id)
            .outerjoin(OrdenServicio, Equipo.id == OrdenServicio.equipo_id)
            .group_by(Cliente.id, Cliente.nombre, Cliente.apellido, Cliente.dni_cuil)
            .all()
        )

        if not db_stats:
            return [], stats_vacias

        # ── 1. Mapear a estructura interna ────────────────────────────────────
        raw_data = [
            {
                "cliente_id":     row[0],
                "nombre_completo": f"{row[2]}, {row[1]}",
                "dni_cuil":        row[3],
                "frecuencia":      row[4],
                "gasto":           float(row[5]) if row[5] is not None else 0.0,
            }
            for row in db_stats
        ]

        # ── CORRECCIÓN: K se adapta a los datos reales, sin datos sintéticos ─
        # Con 1 cliente → K=1 (todos en un cluster), con 2 → K=2, con 3+ → K=3
        K = min(3, len(raw_data))

        # ── 2. Min-Max Scaling ────────────────────────────────────────────────
        max_f = max(d["frecuencia"] for d in raw_data) or 1
        min_f = min(d["frecuencia"] for d in raw_data)
        max_g = max(d["gasto"] for d in raw_data) or 1
        min_g = min(d["gasto"] for d in raw_data)

        range_f = (max_f - min_f) if (max_f - min_f) > 0 else 1
        range_g = (max_g - min_g) if (max_g - min_g) > 0 else 1

        scaled_points = [
            (
                (d["frecuencia"] - min_f) / range_f,
                (d["gasto"]      - min_g) / range_g,
            )
            for d in raw_data
        ]

        # ── 3. Ajuste de K-Means con scikit-learn ──────────────────────────────
        X = np.array(scaled_points)
        
        # random_state=42 para reproducibilidad en la asignación de clústeres
        kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
        kmeans.fit(X)
        assignments = kmeans.labels_.tolist()

        # ── 5. Mapear clústeres a etiquetas según gasto promedio ──────────────
        cluster_gasto_sum = [0.0] * K
        cluster_counts    = [0]   * K
        for i, c_idx in enumerate(assignments):
            cluster_gasto_sum[c_idx] += raw_data[i]["gasto"]
            cluster_counts[c_idx]    += 1

        cluster_averages = sorted([
            (cluster_gasto_sum[c] / cluster_counts[c] if cluster_counts[c] > 0 else 0.0, c)
            for c in range(K)
        ])

        # Etiquetas disponibles según K
        etiquetas_disponibles = [
            {"label": "Casual / Nuevo",      "color": "bg-zinc-100 text-zinc-600 border-zinc-200"},
            {"label": "Activo / Frecuente",  "color": "bg-blue-50 text-blue-600 border-blue-100"},
            {"label": "Cliente Platinum",    "color": "bg-emerald-50 text-emerald-600 border-emerald-100"},
        ]
        # Con K < 3 usamos solo las últimas etiquetas (las más altas)
        etiquetas_activas = etiquetas_disponibles[3 - K:]

        label_mapping = {
            cluster_averages[i][1]: etiquetas_activas[i]
            for i in range(K)
        }

        # ── 6. Resultados finales ─────────────────────────────────────────────
        segmented_clients = []
        stats = {
            "Platinum": {"count": 0, "total_gasto": 0.0, "avg_frecuencia": 0.0},
            "Activo":   {"count": 0, "total_gasto": 0.0, "avg_frecuencia": 0.0},
            "Casual":   {"count": 0, "total_gasto": 0.0, "avg_frecuencia": 0.0},
        }

        for i, d in enumerate(raw_data):
            mapping = label_mapping[assignments[i]]
            d["cluster_label"] = mapping["label"]
            d["cluster_color"] = mapping["color"]
            segmented_clients.append(d)

            stat_key = "Casual"
            if mapping["label"] == "Cliente Platinum":
                stat_key = "Platinum"
            elif mapping["label"] == "Activo / Frecuente":
                stat_key = "Activo"

            stats[stat_key]["count"]          += 1
            stats[stat_key]["total_gasto"]    += d["gasto"]
            stats[stat_key]["avg_frecuencia"] += d["frecuencia"]

        for key in stats:
            if stats[key]["count"] > 0:
                stats[key]["avg_frecuencia"] = round(
                    stats[key]["avg_frecuencia"] / stats[key]["count"], 1
                )

        segmented_clients.sort(key=lambda x: x["gasto"], reverse=True)

        cls._cached_result = (segmented_clients, stats)
        cls._last_update   = datetime.now(timezone.utc)

        return segmented_clients, stats