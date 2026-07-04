import logging
from database import db
from backend.utils.backup_service import BackupService
from backend.models.Usuario import Usuario

# Configuración básica del logger para el módulo
logger = logging.getLogger(__name__)

class AdminController:

    @staticmethod
    def generar_backup(usuario_id):
        """Genera el backup y registra el evento a nivel de infraestructura."""
        try:
            backup_dict = BackupService.generate_backup_dict()
            # Uso de logging profesional en lugar de print
            logger.info(f"[AUDITORIA] Usuario ID: {usuario_id} ha generado y descargado un backup completo.")
            return True, backup_dict
        except Exception as e:
            logger.error(f"[ERROR BACKUP] Fallo al generar backup por usuario {usuario_id}: {str(e)}")
            return False, "Error interno al generar el backup de seguridad."

    @staticmethod
    def validar_simulacion_rol(usuario_id, nuevo_rol_descripcion):
        """
        Valida si el usuario tiene permisos de Administrador y si el rol destino es válido.
        Retorna: (bool_exito, nombre_del_rol_normalizado_o_mensaje_error)
        """
        usuario = db.session.get(Usuario, usuario_id)
        
        # Validamos que el usuario exista y sea Administrador
        if not usuario or not usuario.rol or usuario.rol.descripcion.strip().lower() != 'administrador':
            return False, "Permisos insuficientes para simular roles."

        # Normalizamos la entrada para evitar problemas de tildes o mayúsculas
        rol_destino = nuevo_rol_descripcion.strip().lower()
        
        # Diccionario de roles permitidos y sus versiones normalizadas
        roles_permitidos = {
            'administrador': 'administrador',
            'técnico': 'tecnico',
            'tecnico': 'tecnico',
            'secretario': 'secretario'
        }

        if rol_destino not in roles_permitidos:
            return False, "El rol solicitado para simulación no es válido."

        # El controlador solo devuelve la validación lógica. 
        # El Blueprint que llame a este método será el encargado de decidir a qué ruta hacer el redirect.
        return True, roles_permitidos[rol_destino]