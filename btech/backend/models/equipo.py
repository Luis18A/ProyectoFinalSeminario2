from . import db

class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tipo_dispositivo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    numero_serie = db.Column(db.String(100), unique=True, index=True, nullable=False)
    descripcion_general = db.Column(db.Text)

    ordenes = db.relationship('OrdenServicio', backref='equipo', lazy=True)