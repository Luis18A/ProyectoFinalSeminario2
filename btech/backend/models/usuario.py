from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .rol import RolUsuario

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.Enum(RolUsuario), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    ordenes_creadas = db.relationship('OrdenServicio', backref='creador', lazy=True)
    historiales = db.relationship('HistorialEstado', backref='usuario', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)