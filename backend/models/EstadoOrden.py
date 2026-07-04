import enum
from typing import List, Union

class EstadoOrden(enum.Enum):
    PENDIENTE     = 'Pendiente'
    DIAGNOSTICO   = 'Diagnostico'
    PRESUPUESTADO = 'Presupuestado'
    REPARACION    = 'Reparacion'
    LISTO         = 'Listo'
    ENTREGADO     = 'Entregado'

    @classmethod
    def list(cls) -> List[str]:
        return [e.value for e in cls]

    @classmethod
    def transiciones_permitidas(cls, estado_actual: Union['EstadoOrden', str]) -> List['EstadoOrden']:
        # Aseguramos que el estado de entrada sea siempre un Enum válido
        if isinstance(estado_actual, str):
            try:
                estado_actual = cls(estado_actual)
            except ValueError:
                return []

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
    def es_transicion_valida(cls, desde: Union['EstadoOrden', str], hacia: Union['EstadoOrden', str]) -> bool:
        try:
            # Casteamos AMBOS parámetros de manera segura
            estado_desde = cls(desde) if isinstance(desde, str) else desde
            estado_hacia = cls(hacia) if isinstance(hacia, str) else hacia
            
            return estado_hacia in cls.transiciones_permitidas(estado_desde)
        except ValueError:
            return False