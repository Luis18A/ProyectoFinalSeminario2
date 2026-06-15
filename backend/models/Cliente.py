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

    def __init__(self, dni_cuil, nombre, apellido, telefono,
                 email, domicilio, localidad):
        self.dni_cuil  = dni_cuil
        self.nombre    = nombre
        self.apellido  = apellido
        self.telefono  = telefono
        self.email     = email
        self.domicilio = domicilio
        self.localidad = localidad

    # Métodos CRUD (Active Record Pattern)

    # ── Queries (solo lectura, nunca hacen commit) ─────────────────

    @staticmethod
    def get_all():
        return Cliente.query.all()

    @staticmethod
    def get_by_id(id):
        return db.session.get(Cliente, id)

    @staticmethod
    def get_por_dni(dni):
        return Cliente.query.filter_by(dni_cuil=dni).first()

    @staticmethod
    def get_por_email(email):
        return Cliente.query.filter_by(email=email).first()

    @staticmethod
    def get_por_nombre_apellido(termino):
        return Cliente.query.filter(
            (Cliente.nombre.ilike(f"%{termino}%")) |
            (Cliente.apellido.ilike(f"%{termino}%"))
        ).all()

    def __repr__(self):
        return f"<Cliente id={self.id} dni='{self.dni_cuil}' nombre='{self.nombre} {self.apellido}'>"
