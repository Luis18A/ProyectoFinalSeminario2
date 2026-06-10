from database import db
from datetime import datetime

class HistorialEstado(db.Model):
    __tablename__ = 'historial_estados'
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=False)
    estado_anterior = db.Column(db.String(50), nullable=False)
    estado_nuevo = db.Column(db.String(50), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    observacion_tecnica = db.Column(db.Text)

    # Relación para poder acceder al nombre del usuario desde el template
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])

    def __init__(self, orden_id: int, estado_anterior: str, estado_nuevo: str, usuario_id: int, observacion_tecnica: str=None):
        self.orden_id = orden_id
        self.estado_anterior = estado_anterior
        self.estado_nuevo = estado_nuevo
        self.usuario_id = usuario_id
        self.observacion_tecnica = observacion_tecnica

    @classmethod
    def add_registro(cls, orden_id, estado_anterior, estado_nuevo, usuario_id, observacion_tecnica=None):
        registro = cls(
            orden_id=orden_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            usuario_id=usuario_id,
            observacion_tecnica=observacion_tecnica
        )
        db.session.add(registro)
        db.session.flush()

    @classmethod
    def get_historial_orden(cls, orden_id):
        return cls.query.filter_by(orden_id=orden_id).all()

    @classmethod
    def get_historial_usuario(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).all()

    @classmethod
    def get_historial_fecha(cls, fecha_cambio):
        """
        Filtra los registros de historial por una fecha determinada (mismo día),
        tolerando diferencias de hora/minuto/segundo.
        """
        from datetime import datetime
        if isinstance(fecha_cambio, str):
            try:
                fecha_cambio = datetime.fromisoformat(fecha_cambio).date()
            except ValueError:
                return []
        elif isinstance(fecha_cambio, datetime):
            fecha_cambio = fecha_cambio.date()
            
        return cls.query.filter(db.func.cast(cls.fecha_cambio, db.Date) == fecha_cambio).all()
    
    @classmethod
    def get_historial_tickets(cls, orden_id):
        return cls.query.filter_by(orden_id=orden_id).order_by(cls.fecha_cambio.desc()).all()