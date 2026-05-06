from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # Aumentado para el hash
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    rol_id = db.Column(db.ForeignKey('rol.id'), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    @classmethod
    def crear(cls, username, password, nombre, apellido, rol_id, activo=True):
        nuevo_usuario = cls(
            username=username,
            password=generate_password_hash(password), # Hasheamos al crear
            nombre=nombre,
            apellido=apellido,
            rol_id=rol_id,
            activo=activo
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario

    @classmethod
    def obtener_todos(cls):
        return cls.query.all()

    @classmethod
    def obtener_por_id(cls, id):
        return cls.query.get(id)

    def actualizar(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'password' and value:
                    # Si el campo es password, lo hasheamos
                    setattr(self, key, generate_password_hash(value))
                else:
                    setattr(self, key, value)
        db.session.commit()

    def verificar_password(self, password):
        """Compara una contraseña en texto plano con el hash guardado."""
        return check_password_hash(self.password, password)

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()
