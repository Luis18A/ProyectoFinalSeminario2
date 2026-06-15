# create.py — versión corregida

from app import app
from backend.models.Usuario import Usuario
from backend.models.Rol import Rol
from backend.models.TipoDispositivo import TipoDispositivo  # import al inicio
from database import db
from werkzeug.security import generate_password_hash  # ← CRÍTICO


def crear_roles(roles_data):
    """Crea roles si no existen. Retorna dict {descripcion: rol}."""
    roles = {}
    for descripcion in roles_data:
        rol = Rol.query.filter_by(descripcion=descripcion).first()
        if not rol:
            rol = Rol(descripcion=descripcion)
            db.session.add(rol)
            print(f"Rol '{descripcion}' agregado.")
        roles[descripcion] = rol
    return roles


def crear_usuarios(usuarios_data, roles):
    """Crea usuarios por defecto con contraseñas hasheadas."""
    for data in usuarios_data:
        existe = Usuario.query.filter_by(username=data['username']).first()
        if not existe:
            usuario = Usuario(
                username=data['username'],
                password=Usuario.hashear_password(data['password']),  # hash explícito
                nombre=data['nombre'],
                apellido=data['apellido'],
                rol_id=roles[data['rol']].id,
                activo=True
            )
            db.session.add(usuario)
            print(f"Usuario '{data['username']}' agregado.")
        else:
            print(f"Usuario '{data['username']}' ya existe.")


def crear_tipos_dispositivo(tipos):
    """Crea tipos de dispositivo si la tabla está vacía."""
    if not TipoDispositivo.query.first():
        for desc in tipos:
            db.session.add(TipoDispositivo(descripcion=desc))
        print("Tipos de dispositivos creados.")
    else:
        print("Los tipos de dispositivos ya existen.")


with app.app_context():
    # ── Configuración de datos iniciales ────────────────────────────────
    ROLES = ["Administrador", "Técnico", "Secretario"]

    USUARIOS = [
        {"username": "admin",      "password": "Admin1234!",     "nombre": "Brian",  "apellido": "Teran",     "rol": "Administrador"},
        {"username": "tecnico",    "password": "Tecnico1234!",   "nombre": "Juan",   "apellido": "Técnico",   "rol": "Técnico"},
        {"username": "secretario", "password": "Secretario1234!","nombre": "Ana",    "apellido": "Secretaria","rol": "Secretario"},
    ]

    TIPOS_DISPOSITIVO = ["Notebook", "PC Escritorio", "Impresora", "Servidor", "Consola"]

    # ── Ejecución en una sola transacción ────────────────────────────────
    try:
        roles = crear_roles(ROLES)
        db.session.flush()  # asigna IDs sin hacer commit todavía

        crear_usuarios(USUARIOS, roles)
        crear_tipos_dispositivo(TIPOS_DISPOSITIVO)

        db.session.commit()  # UN SOLO commit para todo
        print("\n[OK] Base de datos inicializada correctamente.")
    except Exception as e:
        db.session.rollback()
        print(f"\n[ERROR] Error al inicializar la BD: {e}")
        raise