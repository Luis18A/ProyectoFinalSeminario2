from database import db
from backend.utils.backup_service import BackupService
from backend.models.Usuario import Usuario

class AdminController:

    @staticmethod
    def generar_backup(usuario_id):
        """Genera el backup y registra el evento a nivel de infraestructura."""
        backup_dict = BackupService.generate_backup_dict()

        # En lugar de ensuciar la tabla de reparaciones de hardware, 
        # registramos el evento de infraestructura en los logs del servidor.
        print(f"[AUDITORIA DE SISTEMA] Usuario ID: {usuario_id} ha generado y descargado un backup completo de la base de datos.")

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