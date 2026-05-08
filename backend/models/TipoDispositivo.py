from database import db

class TipoDispositivo(db.Model):
    __tablename__ = 'tipo_dispositivo'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)

    @classmethod
    def obtener_todos(cls):
        return cls.query.all()

    @classmethod
    def crear(cls, descripcion):
        nuevo_tipo = cls(descripcion=descripcion)
        db.session.add(nuevo_tipo)
        db.session.commit()
        return nuevo_tipo

    @classmethod
    def obtener_por_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def actualizar(cls, id, descripcion):
        tipo = cls.obtener_por_id(id)
        if tipo:
            tipo.descripcion = descripcion
            db.session.commit()
            return tipo
        return None

    @classmethod
    def eliminar(cls, id):
        tipo = cls.obtener_por_id(id)
        if tipo:
            db.session.delete(tipo)
            db.session.commit()
            return True
        return False