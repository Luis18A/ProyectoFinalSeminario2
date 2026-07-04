from database import db
from sqlalchemy.sql import func
from datetime import datetime, timedelta

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

    # ── Queries ────────────────────────────────────────────────────────

    @classmethod
    def get_historial_orden(cls, orden_id):
        """Devuelve el historial de una orden, del más reciente al más antiguo."""
        return cls.query.filter_by(orden_id=orden_id).order_by(cls.fecha_cambio.desc()).all()

    @classmethod
    def get_historial_usuario(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).order_by(cls.fecha_cambio.desc()).all()

    @classmethod
    def get_historial_fecha(cls, fecha_consulta):
        """
        NOTA ARQUITECTÓNICA: Optimización SARGable.
        En lugar de transformar la columna en SQL (lo que anula los índices),
        buscamos por un rango de tiempo.
        """
        if isinstance(fecha_consulta, str):
            try:
                fecha_consulta = datetime.fromisoformat(fecha_consulta).date()
            except ValueError:
                return []
        elif isinstance(fecha_consulta, datetime):
            fecha_consulta = fecha_consulta.date()
            
        # Generamos el rango: desde el inicio del día hasta el inicio del día siguiente
        inicio_dia = datetime.combine(fecha_consulta, datetime.min.time())
        fin_dia = inicio_dia + timedelta(days=1)
        
        return cls.query.filter(
            cls.fecha_cambio >= inicio_dia,
            cls.fecha_cambio < fin_dia
        ).order_by(cls.fecha_cambio.desc()).all()