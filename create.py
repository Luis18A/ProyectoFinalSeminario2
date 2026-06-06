from app import app
from backend.models.Usuario import Usuario
from backend.models.Rol import Rol
from database import db

with app.app_context():
    # 1. Crear roles si no existen
    admin_rol = Rol.query.filter_by(descripcion="Administrador").first()
    if not admin_rol:
        admin_rol = Rol(descripcion="Administrador")
        db.session.add(admin_rol)
        db.session.commit()
        print("Rol 'Administrador' creado.")

    tecnico_rol = Rol.query.filter_by(descripcion="Técnico").first()
    if not tecnico_rol:
        tecnico_rol = Rol(descripcion="Técnico")
        db.session.add(tecnico_rol)
        db.session.commit()
        print("Rol 'Técnico' creado.")

    secretario_rol = Rol.query.filter_by(descripcion="Secretario").first()
    if not secretario_rol:
        secretario_rol = Rol(descripcion="Secretario")
        db.session.add(secretario_rol)
        db.session.commit()
        print("Rol 'Secretario' creado.")

    # 2. Crear usuarios por defecto
    admin = Usuario.query.filter_by(username="admin").first()
    if not admin:
        admin = Usuario(
            username="admin",
            password="1234",
            nombre="Brian",
            apellido="Teran",
            rol_id=admin_rol.id,
            activo=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado con éxito.")
    else:
        print("El usuario admin ya existe.")

    tecnico = Usuario.query.filter_by(username="tecnico").first()
    if not tecnico:
        tecnico = Usuario(
            username="tecnico",
            password="1234",
            nombre="Juan",
            apellido="Técnico",
            rol_id=tecnico_rol.id,
            activo=True
        )
        db.session.add(tecnico)
        db.session.commit()
        print("Usuario tecnico creado con éxito.")
    else:
        print("El usuario tecnico ya existe.")

    secretario = Usuario.query.filter_by(username="secretario").first()
    if not secretario:
        secretario = Usuario(
            username="secretario",
            password="1234",
            nombre="Ana",
            apellido="Secretaria",
            rol_id=secretario_rol.id,
            activo=True
        )
        db.session.add(secretario)
        db.session.commit()
        print("Usuario secretario creado con éxito.")
    else:
        print("El usuario secretario ya existe.")

    # 3. Crear tipos de dispositivos por defecto si la tabla está vacía
    from backend.models.TipoDispositivo import TipoDispositivo
    if not TipoDispositivo.query.first():
        tipos_defecto = ["Notebook", "PC Escritorio", "Impresora", "Servidor", "Consola"]
        for desc in tipos_defecto:
            tipo = TipoDispositivo(descripcion=desc)
            db.session.add(tipo)
        db.session.commit()
        print("Tipos de dispositivos por defecto creados.")
    else:
        print("Los tipos de dispositivos ya existen en la base de datos.")