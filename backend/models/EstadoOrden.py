import enum

class EstadoOrden(enum.Enum):
    PENDIENTE = 'Pendiente'
    DIAGNOSTICO = 'Diagnostico'
    PRESUPUESTADO = 'Presupuestado'
    REPARACION = 'Reparacion'
    LISTO = 'Listo'
    ENTREGADO = 'Entregado'

    @classmethod
    def list(cls):
        return [e.value for e in cls]

    @classmethod
    def transiciones_permitidas(cls, estado_actual):
        """Define las transiciones permitidas a partir del estado actual."""
        transiciones = {
            cls.PENDIENTE: [cls.DIAGNOSTICO],
            cls.DIAGNOSTICO: [cls.PRESUPUESTADO],
            cls.PRESUPUESTADO: [cls.REPARACION, cls.DIAGNOSTICO],
            cls.REPARACION: [cls.LISTO, cls.PRESUPUESTADO],
            cls.LISTO: [cls.ENTREGADO],
            cls.ENTREGADO: []
        }
        res = [estado_actual] + transiciones.get(estado_actual, [])
        return list(dict.fromkeys(res))