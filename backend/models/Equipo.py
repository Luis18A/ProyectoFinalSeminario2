from database import db

class Equipo(db.Model):
    __tablename__ = 'equipo'

    id           = db.Column(db.Integer, primary_key=True)
    cliente_id   = db.Column(db.ForeignKey('cliente.id'), nullable=False)
    marca        = db.Column(db.String(80), nullable=False)
    modelo       = db.Column(db.String(80), nullable=False)
    numero_serie = db.Column(db.String(80), unique=True, nullable=False)
    tipo_id      = db.Column(db.ForeignKey('tipo_dispositivo.id'), nullable=False)
    descripcion  = db.Column(db.String(500), nullable=True)

    cliente = db.relationship('Cliente', back_populates='equipos', foreign_keys=[cliente_id])
    tipo    = db.relationship('TipoDispositivo', foreign_keys=[tipo_id])

    def __init__(self, cliente_id, marca, modelo, numero_serie, tipo_id, descripcion=None):
        self.cliente_id   = cliente_id
        self.marca        = marca
        self.modelo       = modelo
        self.numero_serie = numero_serie
        self.tipo_id      = tipo_id
        self.descripcion  = descripcion

    @property
    def estado_actual(self):
        # Se importa aquí adentro para evitar la Importación Circular con OrdenServicio.py
        from backend.models.OrdenServicio import OrdenServicio
        
        ultima = (OrdenServicio.query
                  .filter_by(equipo_id=self.id)
                  .order_by(OrdenServicio.id.desc())
                  .first())
        return ultima.estado.value if ultima else "Disponible"

    # ── Queries ────────────────────────────────────────────────────

    @staticmethod
    def get_all():
        return Equipo.query.all()

    @staticmethod
    def get_by_id(id):
        return db.session.get(Equipo, id)

    @staticmethod
    def get_por_cliente(cliente_id):
        return Equipo.query.filter_by(cliente_id=cliente_id).all()

    @staticmethod
    def get_por_numero_serie(numero_serie):
        return Equipo.query.filter_by(numero_serie=numero_serie).first()

    def __repr__(self):
        return f"<Equipo id={self.id} serie='{self.numero_serie}' marca='{self.marca}'>"