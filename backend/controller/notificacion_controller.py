import logging
from backend.models.Notificacion import Notificacion
from database import db

logger = logging.getLogger(__name__)

class NotificacionController:
    @staticmethod
    def marcar_como_leida(notif_id, usuario_id):
        try:
            notif = Notificacion.query.filter_by(id=notif_id, usuario_id=usuario_id).first()
            if notif:
                notif.marcar_como_leida()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            logger.error(f"[NOTIFICACIONES] Error al marcar leída {notif_id}: {str(e)}")
            return False

    @staticmethod
    def marcar_todas_leidas(usuario_id):
        try:
            Notificacion.marcar_todas_leidas(usuario_id)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"[NOTIFICACIONES] Error al marcar todas leídas para usuario {usuario_id}: {str(e)}")
            return False