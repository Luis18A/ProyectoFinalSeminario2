from database import db
from datetime import datetime

class Notificacion(db.Model):
    __tablename__ = 'notificacion'

    id             = db.Column(db.Integer, primary_key=True)
    usuario_id     = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    titulo         = db.Column(db.String(100), nullable=False)
    mensaje        = db.Column(db.String(500), nullable=False)
    leido          = db.Column(db.Boolean, default=False, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now, nullable=False)
    orden_id       = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=True)

    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    orden   = db.relationship('OrdenServicio', foreign_keys=[orden_id])

    def __init__(self, usuario_id, titulo, mensaje, orden_id=None):
        self.usuario_id = usuario_id
        self.titulo     = titulo
        self.mensaje    = mensaje
        self.orden_id   = orden_id

    # ── Queries ────────────────────────────────────────────────────────

    @classmethod
    def get_todas_por_usuario(cls, usuario_id):
        """Devuelve todas las notificaciones de un usuario, ordenadas por fecha."""
        return cls.query.filter_by(usuario_id=usuario_id).order_by(cls.fecha_creacion.desc()).all()

    @classmethod
    def get_no_leidas_por_usuario(cls, usuario_id):
        """Devuelve solo las notificaciones pendientes de lectura."""
        return cls.query.filter_by(usuario_id=usuario_id, leido=False).order_by(cls.fecha_creacion.desc()).all()