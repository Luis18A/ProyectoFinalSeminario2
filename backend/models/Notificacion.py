from database import db
from sqlalchemy.sql import func

class Notificacion(db.Model):
    __tablename__ = 'notificacion'

    id             = db.Column(db.Integer, primary_key=True)
    usuario_id     = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    orden_id       = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=True, index=True) 
    titulo         = db.Column(db.String(100), nullable=False)
    mensaje        = db.Column(db.String(500), nullable=False)
    leido          = db.Column(db.Boolean, default=False, server_default=db.text('false'), nullable=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    orden   = db.relationship('OrdenServicio', foreign_keys=[orden_id])

    def marcar_como_leida(self):
        self.leido = True

    @classmethod
    def marcar_todas_leidas(cls, usuario_id):
        cls.query.filter_by(usuario_id=usuario_id, leido=False).update({'leido': True}, synchronize_session=False)


    def __repr__(self):
        return f"<Notificacion id={self.id} usuario_id={self.usuario_id} leido={self.leido}>"