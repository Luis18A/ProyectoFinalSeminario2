from database import db

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.ForeignKey('usuario.id'), nullable=False)
    equipo_id = db.Column(db.ForeignKey('equipo.id'), nullable=False)
    falla_reportada = db.Column(db.String(100), nullable=False)
    accesorios = db.Column(db.String(100), nullable=False)
    estado_diagnostico = db.Column(db.String(100), nullable=True)
    fecha_recepcion = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(80), nullable=False)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    costo = db.Column(db.Float, nullable=True)
    observaciones = db.Column(db.String(500), nullable=True)

    # Definimos las relaciones explícitas
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    equipo = db.relationship('Equipo', foreign_keys=[equipo_id])

    def __init__(self, usuario_id, equipo_id, falla_reportada, accesorios, fecha_recepcion, estado='Abierto', estado_diagnostico=None, fecha_entrega=None, costo=None, observaciones=None):
        self.usuario_id = usuario_id
        self.equipo_id = equipo_id
        self.falla_reportada = falla_reportada
        self.accesorios = accesorios
        self.fecha_recepcion = fecha_recepcion
        self.estado = estado
        self.estado_diagnostico = estado_diagnostico
        self.fecha_entrega = fecha_entrega
        self.costo = costo
        self.observaciones = observaciones
        
    # Métodos estáticos para CRUD completo

    @staticmethod
    def get_all():
        return OrdenServicio.query.all()

    @staticmethod
    def get_by_id(id):
        return OrdenServicio.query.get(id)

    @staticmethod
    def create(data):
        nueva = OrdenServicio(**data)
        db.session.add(nueva)
        db.session.commit()
        return nueva

    @staticmethod
    def update(orden, data):
        orden.update(data)
        db.session.commit()
        return orden

    @staticmethod
    def delete(orden):
        db.session.delete(orden)
        db.session.commit()

    @staticmethod
    def get_por_usuario(usuario_id):
        """Obtiene todas las órdenes de un usuario específico."""
        return OrdenServicio.query.filter_by(usuario_id=usuario_id).all()
    
    def finalizar_orden(self, costo_final, observaciones, fecha_entrega):
        """Método para cerrar la orden y registrar costo/observaciones."""
        self.costo = costo_final
        self.observaciones = observaciones
        self.fecha_entrega = fecha_entrega
        self.estado = 'Entregado'
        db.session.commit()

    def actualizar_estado_diagnostico(self, nuevo_estado):
        """Método para actualizar solo el estado del diagnóstico."""
        self.estado_diagnostico = nuevo_estado
        db.session.commit()

    def actualizar_estado(self, nuevo_estado):
        """Método para actualizar solo el estado general de la orden."""
        self.estado = nuevo_estado
        db.session.commit()