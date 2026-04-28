from database import db

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.ForeignKey('usuario.id'), nullable=False)
    equipo_id = db.Column(db.ForeignKey('equipo.id'), nullable=False)
    falla_reportada = db.Column(db.String(100), nullable=False)
    accesorios = db.Column(db.String(100), nullable=False)
    estado_diagnostico = db.Column(db.String(100), nullable=True)
    fecha_recepcion = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(80), nullable=False)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    costo = db.Column(db.Float, nullable=True)
    observaciones = db.Column(db.String(500), nullable=True)
