from database import db
from datetime import datetime

class Notificacion(db.Model):
    __tablename__ = 'notificacion'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.String(500), nullable=False)
    leido = db.Column(db.Boolean, default=False, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now, nullable=False)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=True)

    # Relaciones
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    orden = db.relationship('OrdenServicio', foreign_keys=[orden_id])

    def __init__(self, usuario_id, titulo, mensaje, orden_id=None):
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.mensaje = mensaje
        self.orden_id = orden_id

    @classmethod
    def crear_notificacion(cls, usuario_id, titulo, mensaje, orden_id=None):
        nueva = cls(usuario_id=usuario_id, titulo=titulo, mensaje=mensaje, orden_id=orden_id)
        db.session.add(nueva)
        db.session.commit()
        return nueva
