from datetime import datetime
from database import db

class Cliente(db.Model):
    __tablename__ = 'cliente'

    id             = db.Column(db.Integer, primary_key=True)
    dni_cuil       = db.Column(db.String(20), unique=True, nullable=False)
    nombre         = db.Column(db.String(50), nullable=False)
    apellido       = db.Column(db.String(50), nullable=False)
    telefono       = db.Column(db.String(20), nullable=False)
    email          = db.Column(db.String(254), unique=True, nullable=True)
    domicilio      = db.Column(db.String(150), nullable=False)
    localidad      = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)

    # Relación con Equipo
    equipos = db.relationship('Equipo', back_populates='cliente', lazy=True)

    def __init__(self, dni_cuil, nombre, apellido, telefono, domicilio, localidad, email=None, fecha_registro=None):
        self.dni_cuil = dni_cuil
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.domicilio = domicilio
        self.localidad = localidad
        self.email = email
        if fecha_registro:
            self.fecha_registro = fecha_registro

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.fecha_registro.desc()).all()

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def get_por_dni(cls, dni):
        return cls.query.filter_by(dni_cuil=dni).first()

    @classmethod
    def buscar(cls, termino, limite=20):
        return cls.query.filter(
            (cls.nombre.ilike(f"%{termino}%")) |
            (cls.apellido.ilike(f"%{termino}%")) |
            (cls.dni_cuil.ilike(f"%{termino}%"))
        ).order_by(cls.fecha_registro.desc()).limit(limite).all()

    def __repr__(self):
        return f"<Cliente id={self.id} dni='{self.dni_cuil}' nombre='{self.nombre} {self.apellido}'>"
