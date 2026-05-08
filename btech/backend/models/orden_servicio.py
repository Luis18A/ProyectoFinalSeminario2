from . import db
from datetime import datetime
from .estado_orden import EstadoOrden

class OrdenServicio(db.Model):
    __tablename__ = 'ordenes_servicio'
    id = db.Column(db.Integer, primary_key=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    falla_reportada = db.Column(db.Text, nullable=False)
    accesorios = db.Column(db.Text)
    estado = db.Column(db.Enum(EstadoOrden), default=EstadoOrden.PENDIENTE, nullable=False)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    costo_total = db.Column(db.Float, default=0.0)

    historial_estados = db.relationship('HistorialEstado', backref='orden', lazy=True, cascade="all, delete-orphan")