from database import db

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    dni_cuil = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    domicilio = db.Column(db.String(80), nullable=False)
    localidad = db.Column(db.String(80), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)
