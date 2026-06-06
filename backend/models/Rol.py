from database import db

class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)

    # Relación con Usuario
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __init__(self, descripcion:str):
        self.descripcion = descripcion