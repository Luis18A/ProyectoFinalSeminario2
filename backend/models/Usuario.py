from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id                = db.Column(db.Integer, primary_key=True)
    username          = db.Column(db.String(80), unique=True, nullable=False)
    password          = db.Column(db.String(255), nullable=False)
    nombre            = db.Column(db.String(80), nullable=False)
    apellido          = db.Column(db.String(80), nullable=False)
    rol_id            = db.Column(db.ForeignKey('rol.id'), nullable=False)
    activo            = db.Column(db.Boolean, nullable=False, default=True)
    intentos_fallidos = db.Column(db.Integer, nullable=False, default=0)

    MAX_INTENTOS_FALLIDOS = 5  # constante de negocio, configurable

    def __init__(self, username, password, nombre, apellido, rol_id,
                 activo=True, intentos_fallidos=0):
        # ── CORRECCIÓN: el __init__ NO hashea.
        # Quien llame al constructor es responsable de pasar el hash ya generado.
        # Esto hace el comportamiento explícito y predecible.
        if not username:
            raise ValueError("El username no puede estar vacío.")
        if not password:
            raise ValueError("El password no puede estar vacío.")

        self.username          = username.strip().lower()
        self.password          = password  # debe ser el hash, generado por el llamador
        self.nombre            = nombre.strip() if nombre else nombre
        self.apellido          = apellido.strip() if apellido else apellido
        self.rol_id            = rol_id
        self.activo            = activo
        self.intentos_fallidos = intentos_fallidos

    # ─────────────────────────────────────────────────────────────────
    # Métodos de contraseña
    # ─────────────────────────────────────────────────────────────────

    @staticmethod
    def hashear_password(password_plano):
        """
        Genera el hash de una contraseña en texto plano.
        Llamar SIEMPRE antes de crear o actualizar un usuario.
        """
        if not password_plano or len(password_plano) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        return generate_password_hash(password_plano)

    def verificar_password(self, password_plano):
        """Compara contraseña en texto plano con el hash almacenado."""
        return check_password_hash(self.password, password_plano)

    # ─────────────────────────────────────────────────────────────────
    # Lógica de intentos fallidos (ahora funcional)
    # ─────────────────────────────────────────────────────────────────

    def registrar_intento_fallido(self):
        """Incrementa el contador y bloquea la cuenta si supera el límite."""
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= self.MAX_INTENTOS_FALLIDOS:
            self.activo = False  # bloqueo automático

    def resetear_intentos(self):
        """Resetea el contador al hacer login exitoso."""
        self.intentos_fallidos = 0

    # ─────────────────────────────────────────────────────────────────
    # Queries (solo lectura — nunca hacen commit)
    # ─────────────────────────────────────────────────────────────────

    @classmethod
    def obtener_todos(cls):
        return cls.query.all()

    @classmethod
    def obtener_por_id(cls, id):
        return db.session.get(cls, id)

    @staticmethod
    def obtener_por_username(username):
        if not username:
            return None
        return Usuario.query.filter(
            db.func.lower(Usuario.username) == username.strip().lower()
        ).first()

    @staticmethod
    def obtener_por_nombre(nombre):
        return Usuario.query.filter(Usuario.nombre.ilike(f"%{nombre}%")).all()

    @staticmethod
    def obtener_por_apellido(apellido):
        return Usuario.query.filter(Usuario.apellido.ilike(f"%{apellido}%")).all()

    @staticmethod
    def obtener_por_rol(rol_id):
        return Usuario.query.filter_by(rol_id=rol_id).all()

    @staticmethod
    def obtener_por_activo(activo):
        return Usuario.query.filter_by(activo=activo).all()

    def __repr__(self):
        return f"<Usuario id={self.id} username='{self.username}' rol_id={self.rol_id}>"