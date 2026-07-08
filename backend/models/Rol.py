from database import db

class Rol(db.Model):
    __tablename__ = 'rol'
    
    id          = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(80), unique=True, nullable=False)

    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __init__(self, descripcion):
        self.descripcion = descripcion

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.id.asc()).all()
        
    def __repr__(self):
        return f"<Rol id={self.id} descripcion='{self.descripcion}'>"