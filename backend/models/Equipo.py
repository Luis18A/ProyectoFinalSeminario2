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

    # Definimos las relaciones explícitas
    cliente = db.relationship('Cliente', back_populates='equipos', foreign_keys=[cliente_id])
    tipo = db.relationship('TipoDispositivo', foreign_keys=[tipo_id])

    def __init__(self, cliente_id, marca, modelo, numero_serie, tipo_id, descripcion=None):
        self.cliente_id = cliente_id
        self.marca = marca
        self.modelo = modelo
        self.numero_serie = numero_serie
        self.tipo_id = tipo_id
        self.descripcion = descripcion

    # Métodos estáticos para CRUD completo

    @staticmethod
    def get_all():
        return Equipo.query.all()

    @staticmethod
    def get_by_id(id):
        return Equipo.query.get(id)

    @staticmethod
    def create(data):
        nueva = Equipo(**data)
        db.session.add(nueva)
        db.session.commit()
        return nueva

    @staticmethod
    def update(equipo, data):
        equipo.update(data)
        db.session.commit()
        return equipo

    @staticmethod
    def delete(equipo):
        db.session.delete(equipo)
        db.session.commit()

    @staticmethod
    def get_por_cliente(cliente_id):
        """Obtiene todos los equipos de un cliente específico."""
        return Equipo.query.filter_by(cliente_id=cliente_id).all()

    @staticmethod
    def get_por_tipo(tipo_id):
        """Obtiene todos los equipos de un tipo específico."""
        return Equipo.query.filter_by(tipo_id=tipo_id).all()

    @staticmethod
    def get_por_marca(marca):
        """Obtiene todos los equipos de una marca específica."""
        return Equipo.query.filter_by(marca=marca).all()

    @staticmethod
    def get_por_modelo(modelo):
        """Obtiene todos los equipos de un modelo específico."""
        return Equipo.query.filter_by(modelo=modelo).all()

    @staticmethod
    def get_por_numero_serie(numero_serie):
        """Obtiene todos los equipos con un número de serie específico."""
        return Equipo.query.filter_by(numero_serie=numero_serie).all()

    