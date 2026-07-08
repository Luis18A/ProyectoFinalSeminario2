from .EstadoOrden import EstadoOrden
from .HistorialEstado import HistorialEstado
from database import db
from sqlalchemy.sql import func

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'

    id                 = db.Column(db.Integer, primary_key=True)
    usuario_id         = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    equipo_id          = db.Column(db.Integer, db.ForeignKey('equipo.id'), nullable=False, index=True)
    falla_reportada    = db.Column(db.String(500), nullable=False)
    accesorios         = db.Column(db.String(500), nullable=False)
    estado             = db.Column(db.Enum(EstadoOrden), nullable=False, default=EstadoOrden.PENDIENTE)
    estado_diagnostico = db.Column(db.String(255), nullable=True)
    fecha_recepcion    = db.Column(db.DateTime(timezone=True), server_default=func.now())
    fecha_entrega      = db.Column(db.DateTime(timezone=True), nullable=True)
    costo              = db.Column(db.Numeric(10, 2), nullable=True)
    observaciones      = db.Column(db.String(500), nullable=True)

    orden_repuestos    = db.relationship('OrdenRepuesto', back_populates='orden', cascade='all, delete-orphan')
    usuario            = db.relationship('Usuario', foreign_keys=[usuario_id])
    equipo             = db.relationship('Equipo', back_populates='ordenes', foreign_keys=[equipo_id])
    historial          = db.relationship('HistorialEstado', backref='orden', lazy=True, cascade='all, delete-orphan')

    def __init__(self, usuario_id, equipo_id, falla_reportada, accesorios, estado=EstadoOrden.PENDIENTE, estado_diagnostico=None, fecha_recepcion=None, fecha_entrega=None, costo=None, observaciones=None):
        self.usuario_id = usuario_id
        self.equipo_id = equipo_id
        self.falla_reportada = falla_reportada
        self.accesorios = accesorios
        self.estado = estado
        self.estado_diagnostico = estado_diagnostico
        if fecha_recepcion:
            self.fecha_recepcion = fecha_recepcion
        self.fecha_entrega = fecha_entrega
        self.costo = costo
        self.observaciones = observaciones
            
    @property
    def repuestos(self):
        return [
            {
                'id': orp.id,
                'repuesto_id': orp.repuesto_id,
                'codigo': orp.repuesto.codigo,
                'titulo': orp.repuesto.descripcion,
                'precio': float(orp.precio_unitario),
                'cantidad': orp.cantidad,
                'link': '#',
                'tienda': orp.repuesto.proveedor or 'Manual'
            }
            for orp in self.orden_repuestos
        ]

    @property
    def total_repuestos(self) -> float:
        return sum(float(orp.precio_unitario) * orp.cantidad for orp in self.orden_repuestos)

    @property
    def mano_obra(self) -> float:
        costo_total = float(self.costo or 0.0)
        return max(0.0, costo_total - self.total_repuestos)


    def preparar_cambio_estado(self, nuevo_estado, usuario_id, observacion=None):
        if not EstadoOrden.es_transicion_valida(self.estado, nuevo_estado):
            raise ValueError(
                f"Transición inválida: {self.estado.value} → {nuevo_estado.value}"
            )

        estado_anterior = self.estado.value
        self.estado = nuevo_estado

        nuevo_historial = HistorialEstado(
            orden_id=self.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado.value,
            usuario_id=usuario_id,
            observacion_tecnica=observacion,
        )
        return nuevo_historial


    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.fecha_recepcion.desc(), cls.id.desc()).all()

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls, id)

    @classmethod
    def get_por_usuario(cls, usuario_id):
        return cls.query.filter_by(usuario_id=usuario_id).all()


    def __repr__(self):
        return f"<OrdenServicio id={self.id} estado='{self.estado.value}'>"
