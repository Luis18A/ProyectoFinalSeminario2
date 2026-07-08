from database import db
from sqlalchemy.sql import func

class HistorialEstado(db.Model):
    __tablename__ = 'historial_estados'

    id                  = db.Column(db.Integer, primary_key=True)
    orden_id            = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=False, index=True)
    estado_anterior     = db.Column(db.String(50), nullable=False)
    estado_nuevo        = db.Column(db.String(50), nullable=False)
    fecha_cambio        = db.Column(db.DateTime(timezone=True), server_default=func.now(), index=True) 
    usuario_id          = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    observacion_tecnica = db.Column(db.Text)

    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])

    def __init__(self, orden_id, estado_anterior, estado_nuevo, usuario_id, observacion_tecnica=None, fecha_cambio=None):
        self.orden_id = orden_id
        self.estado_anterior = estado_anterior
        self.estado_nuevo = estado_nuevo
        self.usuario_id = usuario_id
        self.observacion_tecnica = observacion_tecnica
        if fecha_cambio:
            self.fecha_cambio = fecha_cambio

    @classmethod
    def get_historial_orden(cls, orden_id):
        return cls.query.filter_by(orden_id=orden_id).order_by(cls.fecha_cambio.desc()).all()
