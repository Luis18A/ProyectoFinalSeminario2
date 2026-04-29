from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import enum

db = SQLAlchemy()

# 1. Definición de Enums (Para asegurar que no entren datos basura)
class RolUsuario(enum.Enum):
    ADMIN = 'admin'
    TECNICO = 'tecnico'
    SECRETARIA = 'secretaria'

class EstadoOrden(enum.Enum):
    PENDIENTE = 'pendiente'
    DIAGNOSTICO = 'diagnostico'
    PRESUPUESTADO = 'presupuestado'
    REPARACION = 'reparacion'
    LISTO = 'listo'
    ENTREGADO = 'entregado'

# 2. Modelos de la Base de Datos

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.Enum(RolUsuario), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones
    ordenes_creadas = db.relationship('OrdenServicio', backref='creador', lazy=True)
    historiales = db.relationship('HistorialEstado', backref='usuario', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    dni_cuil = db.Column(db.String(20), unique=True, index=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación 1:N con Equipos
    equipos = db.relationship('Equipo', backref='dueño', lazy=True, cascade="all, delete-orphan")

class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tipo_dispositivo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    numero_serie = db.Column(db.String(100), unique=True, index=True, nullable=False)
    descripcion_general = db.Column(db.Text)

    # Relación 1:N con Órdenes
    ordenes = db.relationship('OrdenServicio', backref='equipo', lazy=True)

class OrdenServicio(db.Model):
    __tablename__ = 'ordenes_servicio'
    id = db.Column(db.Integer, primary_key=True)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    falla_reportada = db.Column(db.Text, nullable=False)
    accesorios = db.Column(db.Text)
    estado = db.Column(db.Enum(EstadoOrden), default=EstadoOrden.PENDIENTE, nullable=False)
    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    costo_total = db.Column(db.Float, default=0.0)

    # Relación 1:N con Historial
    historial_estados = db.relationship('HistorialEstado', backref='orden', lazy=True, cascade="all, delete-orphan")

class HistorialEstado(db.Model):
    __tablename__ = 'historial_estados'
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes_servicio.id'), nullable=False)
    estado_anterior = db.Column(db.String(50), nullable=False)
    estado_nuevo = db.Column(db.String(50), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    observacion_tecnica = db.Column(db.Text)