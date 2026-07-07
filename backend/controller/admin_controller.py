import logging
from database import db
from backend.utils.backup_service import BackupService
from backend.models.Usuario import Usuario

# Configuración básica del logger para el módulo
logger = logging.getLogger(__name__)

class AdminController:

    @staticmethod
    def generar_backup(usuario_id):
        try:
            usuario = db.session.get(Usuario, usuario_id)
            if not usuario or not usuario.activo:
                logger.warning(f"[ALERTA DE SEGURIDAD] Intento de backup con usuario inexistente o inactivo. ID: {usuario_id}")
                return False, "Acceso denegado o usuario inactivo."

            if not usuario.rol or usuario.rol.descripcion.strip().lower() != 'administrador':
                logger.warning(f"[ALERTA DE SEGURIDAD] Intento no autorizado de backup por usuario ID: {usuario_id} (Rol: {usuario.rol.descripcion if usuario.rol else 'Ninguno'})")
                return False, "Permisos insuficientes para realizar esta acción."

            backup_dict = BackupService.generate_backup_dict()
            logger.info(f"[AUDITORIA] Usuario ID: {usuario_id} ({usuario.username}) ha generado y descargado un backup completo.")
            return True, backup_dict

        except Exception as e:
            logger.error(f"[ERROR CRITICO BACKUP] Fallo al generar backup solicitado por usuario {usuario_id}: {str(e)}", exc_info=True)
            return False, "Error interno del servidor al procesar el backup de seguridad."

    @staticmethod
    def validar_simulacion_rol(usuario_id, nuevo_rol_descripcion):
        usuario = db.session.get(Usuario, usuario_id)
        if not usuario or not usuario.activo:
            return False, "Usuario inexistente o inactivo."

        if not usuario.rol or usuario.rol.descripcion.strip().lower() != 'administrador':
            logger.warning(f"[ALERTA DE SEGURIDAD] Intento de simulación de rol por usuario no administrador. ID: {usuario_id}")
            return False, "Permisos insuficientes para simular roles."

        if not nuevo_rol_descripcion:
            return False, "El rol de destino no fue especificado."

        rol_destino = nuevo_rol_descripcion.strip().lower()

        roles_permitidos = {
            'administrador': 'administrador',
            'técnico': 'tecnico',
            'tecnico': 'tecnico',
            'secretario': 'secretario'
        }

        if rol_destino not in roles_permitidos:
            return False, "El rol solicitado para simulación no es válido."

        return True, roles_permitidos[rol_destino]