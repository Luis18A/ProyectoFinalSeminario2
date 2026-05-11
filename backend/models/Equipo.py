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

    # Relaciones
    cliente = db.relationship('Cliente', back_populates='equipos', foreign_keys=[cliente_id])
    tipo = db.relationship('TipoDispositivo', foreign_keys=[tipo_id])

    def __init__(self, cliente_id, marca, modelo, numero_serie, tipo_id, descripcion=None):
        self.cliente_id = cliente_id
        self.marca = marca
        self.modelo = modelo
        self.numero_serie = numero_serie
        self.tipo_id = tipo_id
        self.descripcion = descripcion

    # Métodos CRUD (Active Record Pattern)

    @staticmethod
    def get_all():
        return Equipo.query.all()

    @staticmethod
    def get_by_id(id):
        return Equipo.query.get(id)

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
    def get_por_cliente(cliente_id):
        return Equipo.query.filter_by(cliente_id=cliente_id).all()

    @staticmethod
    def get_por_numero_serie(numero_serie):
        return Equipo.query.filter_by(numero_serie=numero_serie).first()