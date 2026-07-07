from database import db

class TipoDispositivo(db.Model):
    __tablename__ = 'tipo_dispositivo'

    id          = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, descripcion: str):
        self.descripcion = descripcion

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def get_por_descripcion_exacta(cls, descripcion):
        return cls.query.filter(
            db.func.lower(cls.descripcion) == db.func.lower(descripcion)
        ).first()

    @classmethod
    def get_por_descripcion_parcial(cls, termino):
        return cls.query.filter(
            cls.descripcion.ilike(f"%{termino}%")
        ).all()

    def __repr__(self):
        return f"<TipoDispositivo id={self.id} descripcion='{self.descripcion}'>"