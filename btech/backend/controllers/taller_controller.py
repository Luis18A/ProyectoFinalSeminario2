from backend.models import db, OrdenServicio, EstadoOrden, HistorialEstado, Equipo

def obtener_todos_los_tickets():
    return OrdenServicio.query.order_by(OrdenServicio.fecha_ingreso.desc()).all()

def obtener_estados_disponibles():
    # En vez de consultar a la base de datos, armamos la lista desde el Enum de Python.
    # 'name' es la clave (ej: REPARACION) y 'value' es el texto bonito (ej: En Reparación).
    return [{'id': estado.name, 'nombre': estado.value} for estado in EstadoOrden]

def obtener_equipo_por_id(equipo_id):
    # Actualizado a SQLAlchemy 2.0 (Evita el Legacy Warning)
    return db.get_or_404(Equipo, equipo_id)

def obtener_ticket_por_id(orden_id):
    # Actualizado a SQLAlchemy 2.0
    return db.get_or_404(OrdenServicio, orden_id)

def crear_ticket(equipo_id, usuario_id, falla, accesorios):
    # ¡Mucho más fácil! No necesitamos buscar en la base, usamos el Enum directo.
    estado_inicial = EstadoOrden.PENDIENTE
    
    # 1. Creamos la orden principal
    nueva_orden = OrdenServicio(
        equipo_id=equipo_id,
        usuario_id=usuario_id,
        estado=estado_inicial, # Usamos 'estado' en vez de 'estado_id'
        falla_reportada=falla,
        accesorios=accesorios
    )
    db.session.add(nueva_orden)
    db.session.flush() # Obtenemos el ID

    # 2. Registramos el movimiento en la auditoría
    historial = HistorialEstado(
        orden_id=nueva_orden.id,
        usuario_id=usuario_id,
        estado_anterior='Ingreso',
        estado_nuevo=estado_inicial.value, # Guardamos el texto (ej: "Pendiente")
        observacion_tecnica='Ingreso del equipo al taller.'
    )
    db.session.add(historial)
    db.session.commit()
    
    return True, nueva_orden.id

def actualizar_ticket(orden_id, usuario_id, nuevo_estado_id, observacion, costo):
    orden = db.get_or_404(OrdenServicio, orden_id)
    
    # Ahora la orden tiene '.estado' directo (el Enum), sacamos su valor en texto
    estado_anterior_nombre = orden.estado.value if orden.estado else "Desconocido"
    estado_nuevo_nombre = estado_anterior_nombre
    hubo_cambios = False
    
    # 1. Si cambió de estado, actualizamos
    # nuevo_estado_id ahora será un texto como "REPARACION" o "LISTO" (viene del formulario HTML)
    if nuevo_estado_id and nuevo_estado_id != orden.estado.name:
        # Asignamos el nuevo Enum basándonos en el nombre
        orden.estado = EstadoOrden[nuevo_estado_id]
        estado_nuevo_nombre = orden.estado.value
        hubo_cambios = True
            
    # 2. Si hay un costo nuevo, lo actualizamos
    if costo:
        orden.costo_total = float(costo)
        hubo_cambios = True
        
    # 3. Si hubo algún cambio físico o el técnico dejó una nota, grabamos el historial
    if hubo_cambios or observacion:
        historial = HistorialEstado(
            orden_id=orden.id,
            usuario_id=usuario_id,
            estado_anterior=estado_anterior_nombre,
            estado_nuevo=estado_nuevo_nombre,
            observacion_tecnica=observacion
        )
        db.session.add(historial)
        
    db.session.commit()
    return True, 'Ticket actualizado correctamente.'

def obtener_historial_ticket(orden_id):
    return HistorialEstado.query.filter_by(orden_id=orden_id).order_by(HistorialEstado.fecha_cambio.desc()).all()