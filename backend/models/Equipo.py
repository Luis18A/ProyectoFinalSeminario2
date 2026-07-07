from database import db

class Equipo(db.Model):
    __tablename__ = 'equipo'

    id               = db.Column(db.Integer, primary_key=True)
    cliente_id       = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False, index=True)
    marca            = db.Column(db.String(80), nullable=False)
    modelo           = db.Column(db.String(80), nullable=False)
    numero_serie     = db.Column(db.String(80), unique=True, nullable=False)
    tipo_id          = db.Column(db.Integer, db.ForeignKey('tipo_dispositivo.id'), nullable=False, index=True)
    descripcion      = db.Column(db.String(500), nullable=True)

    cliente          = db.relationship('Cliente', back_populates='equipos')
    tipo             = db.relationship('TipoDispositivo')
    ordenes          = db.relationship('OrdenServicio', back_populates='equipo', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def estado_actual(self):
        from backend.models.OrdenServicio import OrdenServicio
        ultima_orden = self.ordenes.order_by(OrdenServicio.id.desc()).first()
        return ultima_orden.estado.value if ultima_orden else "Disponible"

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def get_por_cliente(cls, cliente_id):
        return cls.query.filter_by(cliente_id=cliente_id).all()

    @classmethod
    def get_por_numero_serie(cls, numero_serie):
        return cls.query.filter_by(numero_serie=numero_serie).first()

    def __repr__(self):
        return f"<Equipo id={self.id} serie='{self.numero_serie}' marca='{self.marca}'>"
