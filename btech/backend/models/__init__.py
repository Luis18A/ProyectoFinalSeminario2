from flask_sqlalchemy import SQLAlchemy

# Inicializamos la base de datos
db = SQLAlchemy()

# Importamos los modelos para que SQLAlchemy los registre
from .rol import RolUsuario
from .estado_orden import EstadoOrden
from .usuario import Usuario
from .cliente import Cliente
from .equipo import Equipo
from .orden_servicio import OrdenServicio
from .historial_estado import HistorialEstado

# Le decimos a VS Code explícitamente qué estamos exportando
__all__ = [
    'db',
    'RolUsuario',
    'EstadoOrden',
    'Usuario',
    'Cliente',
    'Equipo',
    'OrdenServicio',
    'HistorialEstado'
]