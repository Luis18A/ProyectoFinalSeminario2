from database import db

class Repuesto(db.Model):
    __tablename__ = 'repuesto'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo          = db.Column(db.String(50), unique=True, nullable=False)
    descripcion     = db.Column(db.String(200), nullable=False)
    categoria       = db.Column(db.String(50), nullable=True)
    precio_promedio = db.Column(db.Numeric(10, 2), nullable=True)
    proveedor       = db.Column(db.String(100), nullable=True)
    activo          = db.Column(db.Boolean, default=True)

    def __init__(self, codigo, descripcion, categoria=None, precio_promedio=None, proveedor=None, activo=True):
        self.codigo          = codigo
        self.descripcion     = descripcion
        self.categoria       = categoria
        self.precio_promedio = precio_promedio
        self.proveedor       = proveedor
        self.activo          = activo

    def __repr__(self):
        return f"<Repuesto id={self.id} codigo='{self.codigo}' descripcion='{self.descripcion}'>"
