from database import db

class Rol(db.Model):
    __tablename__ = 'rol'
    
    id          = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)

    # Relación con Usuario
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    # ── Queries (Estandarizadas) ───────────────────────────────────

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def get_por_descripcion(cls, descripcion):
        # Optimización SARGable: usamos ilike en lugar de aplicar funciones SQL a la columna
        return cls.query.filter(cls.descripcion.ilike(descripcion)).first()
        
    def __repr__(self):
        return f"<Rol id={self.id} descripcion='{self.descripcion}'>"