from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from backend.models.EstadoOrden import EstadoOrden
from collections import Counter

class PredictorService:

    @staticmethod
    def _normalizar_falla(falla):
        """Normaliza semánticamente la descripción de una falla."""
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
        if any(w in f for w in ["sistema", "windows", "virus", "lento", "lentitud", "formatear", "actualiza", "software", "programa", "antivirus", "malware", "tilda", "cuelga", "pantalla azul"]):
            return "Problema de Software / Sistema Operativo"
        if any(w in f for w in ["wifi", "wi-fi", "internet", "red", "bluetooth", "ethernet", "señal", "conectar"]):
            return "Falla de Conectividad / Red"
        if any(w in f for w in ["puerto", "usb", "hdmi", "jack", "conector", "audio", "parlante", "auricular", "microfono", "teclado", "mouse", "touchpad", "botones"]):
            return "Falla de Puertos / Periféricos"
        if any(w in f for w in ["limpieza", "mantenimiento", "sucio", "polvo", "limpiar", "pasta térmica"]):
            return "Mantenimiento y Limpieza Preventiva"
        if any(w in f for w in ["consola", "playstation", "xbox", "nintendo", "switch", "joystick", "control", "mando", "lector", "laser"]):
            return "Falla de Consola / Mandos"
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

        predictions.sort(key=lambda x: x["probabilidad"], reverse=True)
        return predictions