from . import db

class TipoDispositivo(db.Model):
    __tablename__ = 'tipos_dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False) # Ej: 'Impresora Laser', 'Notebook', 'PC Escritorio'
    
    # Relación para saber qué equipos pertenecen a este tipo
    equipos = db.relationship('Equipo', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<TipoDispositivo {self.nombre}>'