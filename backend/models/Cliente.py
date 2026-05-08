from database import db

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    dni_cuil = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    domicilio = db.Column(db.String(80), nullable=False)
    localidad = db.Column(db.String(80), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)

    # Relación con Equipo
    equipos = db.relationship('Equipo', back_populates='cliente', lazy=True)

    # Métodos estáticos para CRUD completo

    @staticmethod
    def get_all():
        return Cliente.query.all()

    @staticmethod
    def get_by_id(id):
        return Cliente.query.get(id)

    @staticmethod
    def create(data):
        nuevo = Cliente(**data)
        db.session.add(nuevo)
        db.session.commit()
        return nuevo

    @staticmethod
    def update(cliente, data):
        cliente.update(data)
        db.session.commit()
        return cliente

    @staticmethod
    def delete(cliente):
        db.session.delete(cliente)
        db.session.commit()

    @staticmethod
    def get_por_dni(dni):
        """Obtiene un cliente por DNI o CUIL."""
        return Cliente.query.filter_by(dni_cuil=dni).first()

    @staticmethod
    def get_por_nombre(nombre):
        """Obtiene clientes por nombre."""
        return Cliente.query.filter(Cliente.nombre.like(f"%{nombre}%")).all()

    @staticmethod
    def get_por_apellido(apellido):
        """Obtiene clientes por apellido."""
        return Cliente.query.filter(Cliente.apellido.like(f"%{apellido}%")).all()

    @staticmethod
    def get_por_telefono(telefono):
        """Obtiene clientes por teléfono."""
        return Cliente.query.filter_by(telefono=telefono).all()

    @staticmethod
    def get_por_email(email):
        """Obtiene clientes por email."""
        return Cliente.query.filter_by(email=email).all()

    @staticmethod
    def get_por_domicilio(domicilio):
        """Obtiene clientes por domicilio."""
        return Cliente.query.filter_by(domicilio=domicilio).all()

    @staticmethod
    def get_por_localidad(localidad):
        """Obtiene clientes por localidad."""
        return Cliente.query.filter_by(localidad=localidad).all()

    @staticmethod
    def get_por_fecha_registro(fecha_registro):
        """Obtiene clientes por fecha de registro."""
        return Cliente.query.filter_by(fecha_registro=fecha_registro).all()