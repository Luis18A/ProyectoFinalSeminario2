from database import db
from datetime import datetime

class OrdenRepuesto(db.Model):
    __tablename__ = 'orden_repuesto'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orden_id        = db.Column(db.Integer, db.ForeignKey('orden_servicio.id', ondelete='CASCADE'), nullable=False)
    repuesto_id     = db.Column(db.Integer, db.ForeignKey('repuesto.id', ondelete='CASCADE'), nullable=False)
    cantidad        = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_agregado  = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint('orden_id', 'repuesto_id', name='uq_orden_repuesto'),
    )

    orden    = db.relationship('OrdenServicio', back_populates='orden_repuestos')
    repuesto = db.relationship('Repuesto')

    def __init__(self, orden_id, repuesto_id, cantidad=1, precio_unitario=0.0, fecha_agregado=None):
        self.orden_id        = orden_id
        self.repuesto_id     = repuesto_id
        self.cantidad        = cantidad
        self.precio_unitario = precio_unitario
        self.fecha_agregado  = fecha_agregado or datetime.now()

    def __repr__(self):
        return f"<OrdenRepuesto id={self.id} orden_id={self.orden_id} repuesto_id={self.repuesto_id} cantidad={self.cantidad}>"
