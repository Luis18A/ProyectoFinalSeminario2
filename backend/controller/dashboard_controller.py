from backend.controller.cliente_controller import ClienteController
from backend.controller.usuario_controller import UsuarioController
from backend.controller.orden_servicio_controller import OrdenServicioController
from backend.controller.tipo_dispositivo_controller import TipoDispositivoController
from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from database import db

class DashboardController:

    @staticmethod
    def obtener_datos_secretaria():
        """Consolida la vista general usando los controladores dedicados."""
        return (
            ClienteController.obtener_todos(),
            UsuarioController.obtener_todos(),
            OrdenServicioController.obtener_todos()
        )

    @staticmethod
    def obtener_datos_gestion_cliente(cliente_id):
        """Unifica las consultas para el panel de gestión mediante delegación."""
        tipo_dispositivos = TipoDispositivoController.obtener_todos()
        # Mantenemos el acceso a Cliente/Equipo aquí o delegamos a ClienteController
        cliente = db.session.get(Cliente, cliente_id) if cliente_id else None
        equipos = Equipo.get_por_cliente(cliente_id) if cliente else []
        
        return tipo_dispositivos, cliente, equipos