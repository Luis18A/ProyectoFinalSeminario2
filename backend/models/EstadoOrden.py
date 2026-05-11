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