from database import db

class TipoDispositivo(db.Model):
    __tablename__ = 'tipo_dispositivo'

    id          = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, descripcion: str):
        self.descripcion = descripcion

    # ── Queries (solo lectura) ─────────────────────────────────────

    @classmethod
    def obtener_todos(cls):
        return cls.query.all()

    @classmethod
    def obtener_por_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def obtener_por_descripcion(cls, descripcion):
        return cls.query.filter(
            db.func.lower(cls.descripcion) == db.func.lower(descripcion)
        ).first()

    @classmethod
    def get_por_descripcion(cls, termino):
        return cls.query.filter(
            cls.descripcion.ilike(f"%{termino}%")
        ).all()

    def __repr__(self):
        return f"<TipoDispositivo id={self.id} descripcion='{self.descripcion}'>"