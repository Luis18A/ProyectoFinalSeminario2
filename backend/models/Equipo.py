from database import db

class Equipo(db.Model):
    __tablename__ = 'equipo'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.ForeignKey('cliente.id'), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    modelo = db.Column(db.String(80), nullable=False)
    numero_serie = db.Column(db.String(80), unique=True, nullable=False)
    tipo_id = db.Column(db.ForeignKey('tipo_dispositivo.id'), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)