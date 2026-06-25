from database import db
from backend.utils.backup_service import BackupService
from backend.models.HistorialEstado import HistorialEstado
from backend.models.Usuario import Usuario

class AdminController:

    @staticmethod
    def generar_backup(usuario_id):
        """Genera el backup y registra la auditoría como evento de sistema."""
        backup_dict = BackupService.generate_backup_dict()

        try:
            # 1. Crear el registro de auditoría
            # Nota: orden_id=None es aceptado por el modelo actual (nullable=True)
            registro = HistorialEstado(
                orden_id=None,
                estado_anterior="Sistema",
                estado_nuevo="Backup generado",
                usuario_id=usuario_id,
                observacion_tecnica="Exportación de respaldo completa descargada por Administrador."
            )
            
            # 2. Persistir en base de datos
            db.session.add(registro)
            db.session.commit()
            
        except Exception as e:
            # Si falla la auditoría, no queremos que falle la descarga del backup.
            # Solo logueamos el error y permitimos que el backup se entregue.
            db.session.rollback()
            print(f"Error registrando auditoría de backup: {str(e)}")

        return backup_dict

    @staticmethod
    def simular_rol(usuario_id, nuevo_rol):
        """Permite a un Administrador simular el entorno de otro rol."""
        usuario = db.session.get(Usuario, usuario_id)
        if not usuario or not usuario.rol or usuario.rol.descripcion != 'Administrador':
            return False, None

        if nuevo_rol not in ('Administrador', 'Técnico', 'Secretario'):
            return False, None

        if nuevo_rol == 'Administrador':
            return True, 'vistas.dashboard'
        elif nuevo_rol == 'Técnico':
            return True, 'vistas.technician'
        elif nuevo_rol == 'Secretario':
            return True, 'vistas.secretary'

        return False, None