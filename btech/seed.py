from app import app
from database import db
from backend.models import Rol, TipoDispositivo, EstadoOrden, Usuario

def inyectar_datos_semilla():
    with app.app_context():
        # 1. Crear los Roles
        roles_basicos = ['Administrador', 'Técnico', 'Recepción']
        for nombre_rol in roles_basicos:
            if not Rol.query.filter_by(nombre=nombre_rol).first():
                nuevo_rol = Rol(nombre=nombre_rol)
                db.session.add(nuevo_rol)
                print(f"Rol '{nombre_rol}' creado.")

        # 2. Crear los Tipos de Dispositivos
        tipos_basicos = ['Notebook', 'PC Escritorio', 'Impresora', 'Celular', 'Tablet']
        for nombre_tipo in tipos_basicos:
            if not TipoDispositivo.query.filter_by(nombre=nombre_tipo).first():
                nuevo_tipo = TipoDispositivo(nombre=nombre_tipo)
                db.session.add(nuevo_tipo)
                print(f"Tipo de dispositivo '{nombre_tipo}' creado.")

        # 3. Crear los Estados de la Orden (Kanban)
        estados_basicos = [
            {'nombre': 'Pendiente', 'color': 'secondary'},
            {'nombre': 'En Diagnóstico', 'color': 'info'},
            {'nombre': 'Esperando Aprobación', 'color': 'warning'},
            {'nombre': 'En Reparación', 'color': 'primary'},
            {'nombre': 'Esperando Repuesto', 'color': 'warning'},
            {'nombre': 'Finalizado', 'color': 'success'},
            {'nombre': 'Entregado a Cliente', 'color': 'dark'},
            {'nombre': 'Cancelado', 'color': 'danger'}
        ]
        for estado in estados_basicos:
            if not EstadoOrden.query.filter_by(nombre=estado['nombre']).first():
                nuevo_estado = EstadoOrden(nombre=estado['nombre'], color_badge=estado['color'])
                db.session.add(nuevo_estado)
                print(f"Estado '{estado['nombre']}' creado.")
        
        db.session.commit() # Guardamos todo esto primero para poder usar el ID del rol Administrador

        # 4. Crear el Usuario Administrador Inicial
        rol_admin = Rol.query.filter_by(nombre='Administrador').first()
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                nombre='Administrador BTech',
                rol_id=rol_admin.id,
                activo=True
            )
            admin.set_password('admin123') # Contraseña por defecto
            db.session.add(admin)
            print("Usuario 'admin' creado con contraseña 'admin123'.")
            
        db.session.commit()
        print("¡Datos semilla inyectados con éxito!")

if __name__ == '__main__':
    inyectar_datos_semilla()