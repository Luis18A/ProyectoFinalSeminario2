from datetime import datetime
from database import db

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    dni_cuil = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    telefono = db.Column(db.String(20), nullable=False) # Cambiado a String para mejor manejo de prefijos
    email = db.Column(db.String(80), nullable=False)
    domicilio = db.Column(db.String(80), nullable=False)
    localidad = db.Column(db.String(80), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Equipo
    equipos = db.relationship('Equipo', back_populates='cliente', lazy=True)

    def __init__(self, dni_cuil, nombre, apellido, telefono, email, domicilio, localidad):
        self.dni_cuil = dni_cuil
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email
        self.domicilio = domicilio
        self.localidad = localidad

    # Métodos CRUD (Active Record Pattern)

    @staticmethod
    def get_all():
        return Cliente.query.all()

    @staticmethod
    def get_by_id(id):
        return Cliente.query.get(id)

    @classmethod
    def create(cls, **data):
        nuevo = cls(**data)
        db.session.add(nuevo)
        db.session.commit()
        return nuevo

    def update_data(self, **data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_por_dni(dni):
        return Cliente.query.filter_by(dni_cuil=dni).first()

    @staticmethod
    def get_por_nombre_apellido(termino):
        """Busca clientes por nombre o apellido."""
        return Cliente.query.filter(
            (Cliente.nombre.like(f"%{termino}%")) | 
            (Cliente.apellido.like(f"%{termino}%"))
        ).all()

    @staticmethod
    def get_por_email(email):
        return Cliente.query.filter_by(email=email).first()