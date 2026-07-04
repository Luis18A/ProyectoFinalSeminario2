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

    # ── Lógica de Dominio ──────────────────────────────────────────────

    def marcar_como_leida(self):
        """Marca una notificación individual como leída."""
        self.leido = True

    @classmethod
    def marcar_todas_leidas(cls, usuario_id):
        """
        Optimización masiva: Actualiza todos los registros pendientes de un usuario
        con una sola consulta SQL, sin cargar los objetos en memoria.
        Nota: Debes ejecutar db.session.commit() en tu controlador después de llamar esto.
        """
        cls.query.filter_by(usuario_id=usuario_id, leido=False).update({'leido': True}, synchronize_session=False)

    # ── Queries (Active Record) ────────────────────────────────────────

    @classmethod
    def get_todas_por_usuario(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).order_by(cls.fecha_creacion.desc()).all()

    @classmethod
    def get_no_leidas_por_usuario(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id, leido=False).order_by(cls.fecha_creacion.desc()).all()

    def __repr__(self):
        return f"<Notificacion id={self.id} usuario_id={self.usuario_id} leido={self.leido}>"