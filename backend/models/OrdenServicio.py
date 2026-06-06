from .EstadoOrden import EstadoOrden
from .HistorialEstado import HistorialEstado
from database import db
from datetime import datetime

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.ForeignKey('usuario.id'), nullable=False)
    equipo_id = db.Column(db.ForeignKey('equipo.id'), nullable=False)
    falla_reportada = db.Column(db.String(100), nullable=False)
    accesorios = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum(EstadoOrden), nullable=False, default=EstadoOrden.PENDIENTE)
    estado_diagnostico = db.Column(db.String(255), nullable=True)
    fecha_recepcion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    costo = db.Column(db.Float, nullable=True)
    observaciones = db.Column(db.String(500), nullable=True)
    repuestos = db.Column(db.JSON, nullable=True, default=list)

    # Definimos las relaciones explícitas
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id])
    equipo = db.relationship('Equipo', foreign_keys=[equipo_id])
    historial = db.relationship('HistorialEstado', backref='orden', lazy=True)

    def __init__(self, usuario_id, equipo_id, falla_reportada, accesorios, fecha_recepcion=None, estado=EstadoOrden.PENDIENTE, estado_diagnostico=None, fecha_entrega=None, costo=None, observaciones=None, repuestos=None):
        self.usuario_id = usuario_id
        self.equipo_id = equipo_id
        self.falla_reportada = falla_reportada
        self.accesorios = accesorios
        self.fecha_recepcion = fecha_recepcion or datetime.utcnow()
        self.estado = estado
        self.estado_diagnostico = estado_diagnostico
        self.fecha_entrega = fecha_entrega
        self.costo = costo
        self.observaciones = observaciones
        self.repuestos = repuestos or []
        
    # Métodos de negocio (Domain Logic)

    def actualizar_estado(self, nuevo_estado, usuario_id, observacion=None):
        """Cambia el estado de la orden y registra el movimiento en el historial."""
        estado_anterior = self.estado.value
        self.estado = nuevo_estado
        
        # Registrar en el historial
        HistorialEstado.add_registro(
            orden_id=self.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado.value,
            usuario_id=usuario_id,
            observacion_tecnica=observacion
        )
        db.session.commit()

    def finalizar_orden(self, costo_final, observaciones, usuario_id):
        """Cierra la orden, registra el costo final y actualiza el estado a ENTREGADO."""
        self.costo = costo_final
        self.observaciones = observaciones
        self.fecha_entrega = datetime.utcnow()
        self.actualizar_estado(EstadoOrden.ENTREGADO, usuario_id, "Orden finalizada y entregada al cliente.")

    def actualizar_diagnostico(self, diagnostico, usuario_id):
        """Actualiza el detalle del diagnóstico y lo registra en el historial."""
        self.estado_diagnostico = diagnostico
        # Si el diagnóstico implica un cambio de estado, podrías llamarlo aquí.
        db.session.commit()

    # Métodos estáticos para CRUD (Active Record Pattern)

    @staticmethod
    def get_all():
        return OrdenServicio.query.all()

    @staticmethod
    def get_by_id(id):
        return OrdenServicio.query.get(id)

    @classmethod
    def create(cls, **data):
        nueva = cls(**data)
        db.session.add(nueva)
        db.session.commit()
        return nueva

    def update_data(self, **data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_por_usuario(usuario_id):
        return OrdenServicio.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def get_por_estado(estado):
        return OrdenServicio.query.filter_by(estado=estado).all()