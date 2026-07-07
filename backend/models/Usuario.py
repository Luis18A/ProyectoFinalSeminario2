from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from sqlalchemy.orm import validates

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id                = db.Column(db.Integer, primary_key=True)
    username          = db.Column(db.String(80), unique=True, nullable=False)
    password          = db.Column(db.String(255), nullable=False)
    nombre            = db.Column(db.String(80), nullable=False)
    apellido          = db.Column(db.String(80), nullable=False)
    rol_id            = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False, index=True)
    activo            = db.Column(db.Boolean, nullable=False, default=True, server_default=db.text('true'))
    intentos_fallidos = db.Column(db.Integer, nullable=False, default=0, server_default=db.text('0'))

    MAX_INTENTOS_FALLIDOS = 5

    # ── Validaciones de Atributos (ORM Level) ──────────────────────

    @validates('username')
    def validate_username(self, key, username):
        if not username or not str(username).strip():
            raise ValueError("El username no puede estar vacío.")
        return str(username).strip().lower()

    @validates('password')
    def validate_password(self, key, password):
        if not password or not str(password).strip():
            raise ValueError("El password no puede estar vacío.")
        return password

    @validates('nombre', 'apellido')
    def validate_cadenas_texto(self, key, valor):
        if valor is not None:
            return str(valor).strip()
        return valor

    # ─────────────────────────────────────────────────────────────────
    # Métodos de contraseña
    # ─────────────────────────────────────────────────────────────────

    @staticmethod
    def hashear_password(password_plano):
        if not password_plano or len(password_plano) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        return generate_password_hash(password_plano)

    def verificar_password(self, password_plano):
        return check_password_hash(self.password, password_plano)

    # ─────────────────────────────────────────────────────────────────
    # Lógica de intentos fallidos
    # ─────────────────────────────────────────────────────────────────

    def registrar_intento_fallido(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= self.MAX_INTENTOS_FALLIDOS:
            self.activo = False

    def resetear_intentos(self):
        self.intentos_fallidos = 0

    # ─────────────────────────────────────────────────────────────────
    # Queries (Active Record)
    # ─────────────────────────────────────────────────────────────────

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def get_por_username(cls, username):
        if not username:
            return None
        # Optimización SARGable: Como la DB ya guarda en minúscula, 
        # pasamos a minúscula el término y buscamos con igualdad exacta.
        termino_busqueda = username.strip().lower()
        return cls.query.filter(cls.username == termino_busqueda).first()

    def __repr__(self):
        return f"<Usuario id={self.id} username='{self.username}' rol_id={self.rol_id}>"