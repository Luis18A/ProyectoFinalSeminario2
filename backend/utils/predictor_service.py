from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from backend.models.EstadoOrden import EstadoOrden
from collections import Counter

# Constante de fallbacks probabilísticos por tipo de dispositivo
FALLBACK_PREDICTIONS = {
    "impresora": [
        {
            "falla": "Atasco de papel recurrente en unidad de fusión",
            "probabilidad": 45,
            "tasa_exito": 92
        },
        {
            "falla": "Obstrucción de inyectores / Desgaste de cabezal térmico",
            "probabilidad": 35,
            "tasa_exito": 85
        },
        {
            "falla": "Error de comunicación / Suciedad en sensores ópticos",
            "probabilidad": 20,
            "tasa_exito": 97
        }
    ],
    "computadora": [
        {
            "falla": "Sobrecalentamiento por disipador obstruido y pasta térmica reseca",
            "probabilidad": 50,
            "tasa_exito": 98
        },
        {
            "falla": "Falla de sectores en disco / Degradación de memoria SSD",
            "probabilidad": 30,
            "tasa_exito": 94
        },
        {
            "falla": "Cortocircuito en línea principal de carga (MOSFET / Fusible quemado)",
            "probabilidad": 20,
            "tasa_exito": 78
        }
    ],
    "general": [
        {
            "falla": "Degradación de batería o circuito de alimentación integrado",
            "probabilidad": 40,
            "tasa_exito": 88
        },
        {
            "falla": "Falla de soldadura BGA por fatiga térmica en chip gráfico",
            "probabilidad": 35,
            "tasa_exito": 70
        },
        {
            "falla": "Corrupción de Firmware / Necesidad de reprogramación EEPROM",
            "probabilidad": 25,
            "tasa_exito": 90
        }
    ]
}

class PredictorService:

    @staticmethod
    def _normalizar_falla(falla):
        """
        CORRECCIÓN: movido dentro de la clase como método privado estático.
        Normaliza semánticamente la descripción de una falla.
        """
        f = falla.lower()
        if any(w in f for w in ["calienta", "temperatura", "sobrecalentamiento", "ventilador", "cooler", "calor"]):
            return "Sobrecalentamiento y refrigeración"
        if any(w in f for w in ["pantalla", "display", "imagen", "video", "bga", "grafic", "gpu"]):
            return "Falla de video / Pantalla"
        if any(w in f for w in ["disco", "ssd", "hdd", "almacenamiento", "no arranca", "bootea"]):
            return "Falla de arranque / Almacenamiento"
        if any(w in f for w in ["encend", "prende", "carg", "alimenta", "fusible", "corto", "bateria", "batería"]):
            return "Falla de alimentación / Carga"
        if any(w in f for w in ["atasco", "papel", "rodillo", "tinta", "cabezal", "impres"]):
            return "Falla mecánica de impresión"
        return falla.strip().capitalize()

    @staticmethod
    def predict_failures(equipo_id):
        equipo = Equipo.get_by_id(equipo_id)
        if not equipo:
            return []

        tipo_nombre = (
            equipo.tipo.descripcion
            if equipo.tipo and hasattr(equipo.tipo, 'descripcion')
            else "Dispositivo"
        )

        historicos = OrdenServicio.query.join(Equipo).filter(
            Equipo.tipo_id == equipo.tipo_id
        ).all()

        valid_orders = [
            o for o in historicos
            if o.falla_reportada and len(o.falla_reportada.strip()) > 3
        ]

        predictions = []

        if len(valid_orders) >= 2:
            # CORRECCIÓN: usar el método de clase en lugar de la función suelta
            falla_counts = Counter([
                PredictorService._normalizar_falla(o.falla_reportada)
                for o in valid_orders
            ])
            total_valid = len(valid_orders)

            for falla_txt, count in falla_counts.most_common(3):
                falla_orders = [
                    o for o in valid_orders
                    if PredictorService._normalizar_falla(o.falla_reportada) == falla_txt
                ]
                exitosas = sum(
                    1 for o in falla_orders
                    if o.estado in (EstadoOrden.LISTO, EstadoOrden.ENTREGADO)
                )
                tasa_exito  = int((exitosas / len(falla_orders)) * 100) if falla_orders else 80
                probabilidad = int((count / total_valid) * 100)

                predictions.append({
                    "falla":        falla_txt,
                    "probabilidad": max(probabilidad, 10),
                    "tasa_exito":   max(tasa_exito, 50),
                    "fuente":       "historico"  # ← nuevo campo para diferenciar en el template
                })

        if not predictions:
            tipo_lower = tipo_nombre.lower()
            if "impresora" in tipo_lower or "fotocopiadora" in tipo_lower:
                base = FALLBACK_PREDICTIONS["impresora"]
            elif any(w in tipo_lower for w in ["notebook", "computadora", "pc", "escritorio"]):
                base = FALLBACK_PREDICTIONS["computadora"]
            else:
                base = FALLBACK_PREDICTIONS["general"]

            # CORRECCIÓN: marcar como estimación base para que el template lo indique
            predictions = [{**p, "fuente": "estimacion"} for p in base]

        predictions.sort(key=lambda x: x["probabilidad"], reverse=True)
        return predictions