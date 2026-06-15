from sqlalchemy.ext.mutable import MutableList
from .EstadoOrden import EstadoOrden
from .HistorialEstado import HistorialEstado
from database import db
from datetime import datetime

class OrdenServicio(db.Model):
    __tablename__ = 'orden_servicio'

    id                 = db.Column(db.Integer, primary_key=True)
    usuario_id         = db.Column(db.ForeignKey('usuario.id'), nullable=False)
    equipo_id          = db.Column(db.ForeignKey('equipo.id'), nullable=False)
    falla_reportada    = db.Column(db.String(500), nullable=False)
    accesorios         = db.Column(db.String(500), nullable=False)
    estado             = db.Column(db.Enum(EstadoOrden), nullable=False, default=EstadoOrden.PENDIENTE)
    estado_diagnostico = db.Column(db.String(255), nullable=True)
    fecha_recepcion    = db.Column(db.DateTime, default=datetime.now)
    fecha_entrega      = db.Column(db.DateTime, nullable=True)
    costo              = db.Column(db.Numeric(10, 2), nullable=True)
    observaciones      = db.Column(db.String(500), nullable=True)

    # ── CORRECCIÓN 1: MutableList para rastreo automático de cambios en JSON ──
    repuestos          = db.Column(MutableList.as_mutable(db.JSON), nullable=True, default=list)

    usuario   = db.relationship('Usuario', foreign_keys=[usuario_id])
    equipo    = db.relationship('Equipo', foreign_keys=[equipo_id])
    historial = db.relationship('HistorialEstado', backref='orden', lazy=True)

    def __init__(self, usuario_id, equipo_id, falla_reportada, accesorios,
                 fecha_recepcion=None, estado=EstadoOrden.PENDIENTE,
                 estado_diagnostico=None, fecha_entrega=None,
                 costo=None, observaciones=None, repuestos=None):
        self.usuario_id         = usuario_id
        self.equipo_id          = equipo_id
        self.falla_reportada    = falla_reportada
        self.accesorios         = accesorios
        self.fecha_recepcion    = fecha_recepcion or datetime.now()
        self.estado             = estado
        self.estado_diagnostico = estado_diagnostico
        self.fecha_entrega      = fecha_entrega
        self.costo              = costo
        self.observaciones      = observaciones
        self.repuestos          = repuestos if repuestos is not None else []

    # ── Lógica de dominio ──────────────────────────────────────────

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

    def preparar_finalizacion(self, costo_final, observaciones, usuario_id):
        self.costo         = costo_final
        self.observaciones = observaciones
        self.fecha_entrega = datetime.now()
        
        return self.preparar_cambio_estado(
            EstadoOrden.ENTREGADO, usuario_id,
            "Orden finalizada y entregada al cliente."
        )

    def actualizar_diagnostico(self, diagnostico):
        self.estado_diagnostico = diagnostico

    # ── Queries ────────────────────────────────────────────────────

    @staticmethod
    def get_all():
        return (OrdenServicio.query
                .order_by(OrdenServicio.fecha_recepcion.desc(),
                          OrdenServicio.id.desc())
                .all())

    @staticmethod
    def get_by_id(id):
        return db.session.get(OrdenServicio, id)

    @staticmethod
    def get_por_usuario(usuario_id):
        return OrdenServicio.query.filter_by(usuario_id=usuario_id).all()

    @staticmethod
    def get_por_estado(estado):
        return OrdenServicio.query.filter_by(estado=estado).all()

    def __repr__(self):
        return f"<OrdenServicio id={self.id} estado='{self.estado.value}'>"
