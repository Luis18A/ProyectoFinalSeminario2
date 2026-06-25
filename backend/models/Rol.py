from database import db

class Rol(db.Model):
    __tablename__ = 'rol'
    id          = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)

    # Relación con Usuario
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __init__(self, descripcion: str):
        self.descripcion = descripcion

    # ── Queries (Estandarizadas) ───────────────────────────────────

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def get_por_descripcion(cls, descripcion):
        return cls.query.filter(
            db.func.lower(cls.descripcion) == db.func.lower(descripcion)
        ).first()