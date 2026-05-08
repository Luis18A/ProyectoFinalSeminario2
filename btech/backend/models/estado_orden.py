import enum
from . import db

class EstadoOrden(enum.Enum):
    PENDIENTE = 'Pendiente'
    DIAGNOSTICO = 'Diagnostico'
    PRESUPUESTADO = 'Presupuestado'
    REPARACION = 'Reparacion'
    LISTO = 'Listo'
    ENTREGADO = 'Entregado'