from backend.models.Notificacion import Notificacion
from database import db

class NotificacionController:
    @staticmethod
    def marcar_como_leida(notif_id, usuario_id):
        notif = Notificacion.query.filter_by(id=notif_id, usuario_id=usuario_id).first()
        if notif:
            notif.leido = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def marcar_todas_leidas(usuario_id):
        Notificacion.query.filter_by(usuario_id=usuario_id, leido=False).update(
            {Notificacion.leido: True}, synchronize_session=False
        )
        db.session.commit()