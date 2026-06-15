import enum

class EstadoOrden(enum.Enum):
    PENDIENTE     = 'Pendiente'
    DIAGNOSTICO   = 'Diagnostico'
    PRESUPUESTADO = 'Presupuestado'
    REPARACION    = 'Reparacion'
    LISTO         = 'Listo'
    ENTREGADO     = 'Entregado'

    @classmethod
    def list(cls):
        return [e.value for e in cls]

    @classmethod
    def transiciones_permitidas(cls, estado_actual):
        transiciones = {
            cls.PENDIENTE:     [cls.DIAGNOSTICO],
            cls.DIAGNOSTICO:   [cls.PRESUPUESTADO],
            cls.PRESUPUESTADO: [cls.REPARACION, cls.DIAGNOSTICO],
            cls.REPARACION:    [cls.LISTO, cls.PRESUPUESTADO],
            cls.LISTO:         [cls.ENTREGADO],
            cls.ENTREGADO:     [],
        }
        permitidos = [estado_actual] + transiciones.get(estado_actual, [])
        return list(dict.fromkeys(permitidos))

    @classmethod
    def es_transicion_valida(cls, desde, hacia):
        """
        NUEVO: verifica si una transición específica es válida.
        Llamar desde el controller antes de cambiar estado.

        Ejemplo:
            EstadoOrden.es_transicion_valida(EstadoOrden.PENDIENTE, EstadoOrden.REPARACION)
            → False
        """
        try:
            estado_hacia = cls(hacia) if isinstance(hacia, str) else hacia
            return estado_hacia in cls.transiciones_permitidas(desde)
        except ValueError:
            return False