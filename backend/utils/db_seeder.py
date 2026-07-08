from database import db
from backend.models import Rol, Usuario, TipoDispositivo

def auto_seed_db():
    """Siembre datos automáticamente para el portfolio (ej. en Render) si está vacío."""
    # Verificamos si ya existen roles
    if Rol.query.count() == 0:
        print("Base de datos vacía detectada. Inicializando roles y usuarios base...")
        try:
            ROLES = ["Administrador", "Técnico", "Secretario"]
            roles_dict = {}
            for r_desc in ROLES:
                rol = Rol(descripcion=r_desc)
                db.session.add(rol)
                roles_dict[r_desc] = rol
            db.session.commit()
            
            USUARIOS = [
                {"username": "admin",      "password": "administrador",     "nombre": "administrador",  "apellido": "administrador", "rol": "Administrador"},
                {"username": "tecnico",    "password": "tecnico",   "nombre": "tecnico",   "apellido": "tecnico",   "rol": "Técnico"},
                {"username": "secretario", "password": "secretario","nombre": "secretario",    "apellido": "secretario","rol": "Secretario"},
            ]
            for u_data in USUARIOS:
                usuario = Usuario(
                    username=u_data['username'],
                    password=Usuario.hashear_password(u_data['password']),
                    nombre=u_data['nombre'],
                    apellido=u_data['apellido'],
                    rol=roles_dict[u_data['rol']],
                    activo=True
                )
                db.session.add(usuario)
            
            TIPOS_DISPOSITIVO = ["Notebook", "PC Escritorio", "Impresora", "Servidor", "Consola"]
            for t_desc in TIPOS_DISPOSITIVO:
                db.session.add(TipoDispositivo(descripcion=t_desc))
            db.session.commit()
            
            print("Roles, usuarios base y tipos de dispositivo inicializados correctamente.")
            
            # Sembrar datos de prueba realistas sólo si se pide explícitamente por variable de entorno
            import os
            if os.environ.get('SEED_DB', '').lower() in ('true', '1'):
                print("Sembrando datos de prueba realistas (clientes, equipos, órdenes, historial)...")
                from datos_prueba import generar_datos
                generar_datos()
                print("Base de datos inicializada y sembrada correctamente para el portfolio!")
        except Exception as e:
            db.session.rollback()
            print(f"Error al sembrar datos de prueba automáticamente: {e}")
