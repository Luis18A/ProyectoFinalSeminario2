from backend.models import db, Cliente, Equipo

def registrar_cliente(dni_cuil, nombre, apellido, telefono, email, direccion):
    # Regla de negocio: Verificar si ya existe por DNI/CUIL
    cliente_existente = Cliente.query.filter_by(dni_cuil=dni_cuil).first()
    if cliente_existente:
        return False, f'El DNI/CUIL {dni_cuil} ya está registrado.'
    
    nuevo_cliente = Cliente(
        dni_cuil=dni_cuil,
        nombre=nombre,
        apellido=apellido,
        telefono=telefono,
        email=email,
        direccion=direccion
    )
    db.session.add(nuevo_cliente)
    db.session.commit()
    return True, 'Cliente registrado exitosamente.'

def obtener_todos_los_clientes():
    return Cliente.query.order_by(Cliente.fecha_registro.desc()).all()

def obtener_cliente_por_id(cliente_id):
    return db.get_or_404(Cliente, cliente_id)

def registrar_equipo(cliente_id, tipo, marca, modelo, nro_serie, descripcion):
    # Regla de negocio: Verificar número de serie único
    equipo_existente = Equipo.query.filter_by(numero_serie=nro_serie).first()
    if equipo_existente:
        return False, f'El número de serie {nro_serie} ya está registrado.'
    
    nuevo_equipo = Equipo(
        cliente_id=cliente_id,
        tipo_dispositivo=tipo, # Usamos el campo String que definimos en models/equipo.py
        marca=marca,
        modelo=modelo,
        numero_serie=nro_serie,
        descripcion_general=descripcion
    )
    db.session.add(nuevo_equipo)
    db.session.commit()
    return True, 'Equipo registrado exitosamente.'

def obtener_equipos_de_cliente(cliente_id):
    return Equipo.query.filter_by(cliente_id=cliente_id).all()

def obtener_tipos_dispositivo():
    # Como eliminamos la tabla TipoDispositivo para simplificar, 
    # devolvemos una lista de opciones para tu formulario HTML.
    return [
        {'id': 'Notebook', 'nombre': 'Notebook'},
        {'id': 'PC Escritorio', 'nombre': 'PC de Escritorio'},
        {'id': 'Impresora', 'nombre': 'Impresora'},
        {'id': 'Monitor', 'nombre': 'Monitor'},
        {'id': 'Otro', 'nombre': 'Otro'}
    ]