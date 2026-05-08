import enum
from . import db

class RolUsuario(enum.Enum):
    ADMIN = 'Administrador'
    TECNICO = 'Tecnico'
    SECRETARIA = 'Secretaria'