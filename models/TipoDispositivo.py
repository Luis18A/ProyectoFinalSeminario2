from database import db

class TipoDispositivo(db.Model):
    __tablename__ = 'tipo_dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)