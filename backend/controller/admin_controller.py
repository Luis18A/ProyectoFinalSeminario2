from backend.utils.backup_service import BackupService
from backend.models.HistorialEstado import HistorialEstado
from backend.models.OrdenServicio import OrdenServicio

class AdminController:
    @staticmethod
    def generar_backup(usuario_id):
        """Dispara la exportación de respaldo y registra auditoría en el historial."""
        backup_dict = BackupService.generate_backup_dict()
        
        # Registrar auditoría en historial si hay una orden vinculable
        first_orden = OrdenServicio.query.first()
        if first_orden:
            HistorialEstado.add_registro(
                orden_id=first_orden.id,
                estado_anterior="System Backup",
                estado_nuevo="System Backup",
                usuario_id=usuario_id,
                observacion_tecnica="Exportación de respaldo de base de datos completa descargado por Administrador."
            )
        return backup_dict
