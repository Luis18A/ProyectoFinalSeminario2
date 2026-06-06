from backend.models.Cliente import Cliente
from backend.models.OrdenServicio import OrdenServicio

class VistaController:
    @staticmethod
    def obtener_datos_secretaria():
        """Obtiene de forma unificada clientes y ordenes para la vista de secretaria."""
        clientes = Cliente.query.all()
        ordenes  = OrdenServicio.get_all()
        return clientes, ordenes
