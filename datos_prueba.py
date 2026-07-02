# datos_prueba.py — script para generar datos de prueba realistas sin crear nuevos usuarios

import random
from datetime import datetime, timedelta
from app import app
from database import db
from backend.models.Usuario import Usuario
from backend.models.Rol import Rol
from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.OrdenServicio import OrdenServicio
from backend.models.EstadoOrden import EstadoOrden
from backend.models.HistorialEstado import HistorialEstado
from backend.models.Notificacion import Notificacion
from backend.models.Repuesto import Repuesto
from backend.models.OrdenRepuesto import OrdenRepuesto



# Datos semilla de ejemplo
NOMBRES = ["Juan", "María", "Carlos", "Ana", "Luis", "Sofía", "Diego", "Lucía", "Javier", "Elena", 
           "Andrés", "Laura", "Mateo", "Camila", "Nicolás", "Valentina", "Facundo", "Martina", "Santiago", "Florencia"]

APELLIDOS = ["Gómez", "Rodríguez", "Fernández", "López", "González", "Pérez", "Martínez", "Sánchez", "Romero", "Álvarez", 
             "Díaz", "Ruiz", "Castro", "Ortiz", "Silva", "Medina", "García", "Herrera", "Ríos", "Muñoz"]

LOCALIDADES = ["Córdoba", "Villa María", "Carlos Paz", "Alta Gracia", "Río Cuarto", "San Francisco", "Bell Ville", "Jesús María"]

CALLES = ["Av. Colón", "Bv. San Juan", "9 de Julio", "Belgrano", "San Martín", "Entre Ríos", "Vélez Sarsfield", "Santa Fe", "Caseros", "Deán Funes"]

MODELOS_DISPOSITIVOS = {
    "Notebook": [
        ("Dell", "Inspiron 15"), ("Dell", "Latitude 3420"), ("Lenovo", "ThinkPad T14"), 
        ("Lenovo", "IdeaPad 3"), ("HP", "Pavilion 15"), ("HP", "ProBook 440"), 
        ("Apple", "MacBook Air M1"), ("Apple", "MacBook Pro 14"), ("ASUS", "ZenBook 14")
    ],
    "PC Escritorio": [
        ("Sentey", "Gamer Core i5"), ("Exo", "Ready D1"), ("Lenovo", "ThinkCentre M70q"), 
        ("ASUS", "ROG Strix"), ("HP", "ProDesk 400"), ("Custom", "AMD Ryzen 5")
    ],
    "Impresora": [
        ("Epson", "EcoTank L3210"), ("Epson", "EcoTank L4260"), ("HP", "LaserJet M111w"), 
        ("HP", "DeskJet 2775"), ("Brother", "HL-L2370DW"), ("Brother", "DCP-T720DW")
    ],
    "Servidor": [
        ("Dell", "PowerEdge T150"), ("Dell", "PowerEdge R750"), ("HP", "ProLiant ML30"), ("HP", "ProLiant DL360")
    ],
    "Consola": [
        ("Sony", "PlayStation 4 Pro"), ("Sony", "PlayStation 5"), ("Microsoft", "Xbox One S"), 
        ("Microsoft", "Xbox Series S"), ("Microsoft", "Xbox Series X"), ("Nintendo", "Switch OLED")
    ]
}

FALLAS = [
    "No enciende, sin luces ni sonidos.",
    "Pantalla rota / parpadea al moverse.",
    "Sobrecalentamiento extremo y se apaga a los 10 minutos.",
    "Lentitud extrema al abrir cualquier aplicación.",
    "Fallo de disco duro (pantalla azul o boot error).",
    "Limpieza física completa y cambio de pasta térmica.",
    "No reconoce cartuchos de tinta / atasco de papel.",
    "Bisagra rota, carcasa semiabierta.",
    "No da video por puerto HDMI ni pantalla integrada.",
    "Actualización de sistema operativo e instalación de antivirus.",
    "Fallo en pin de carga, carga intermitente.",
    "Teclado no funciona / teclas pegadas.",
    "No se conecta a redes Wi-Fi.",
    "Derrame de líquido sobre la placa."
]

ACCESORIOS = [
    "Cargador original", "Funda protectora", "Ninguno", "Cable de alimentación", 
    "Caja original y manuales", "Mochila porta notebook", "Batería externa", "Adaptador USB-C"
]

DIAGNOSTICOS = [
    "Se detectó falla en módulo de memoria RAM. Se requiere reemplazo.",
    "Pantalla con panel LCD quebrado. Requiere repuesto original.",
    "Cooler obstruido por tierra y pasta térmica totalmente seca. Requiere mantenimiento preventivo.",
    "Disco rígido mecánico con sectores dañados. Se recomienda migrar a SSD.",
    "Cortocircuito en la etapa de entrada de la placa madre cerca del conector DC-jack.",
    "Cabezal de impresión obstruido y almohadillas saturadas de tinta.",
    "Bisagra izquierda rota, requiere soldadura o cambio de soportes.",
    "Chip de video desoldado. Requiere reballing o reemplazo de placa.",
    "Conflictos de drivers y malware detectado en inicio de Windows.",
    "Pin de carga desoldado en la placa madre.",
    "Membrana de teclado sulfatada debido a humedad.",
    "Placa Wi-Fi dañada por pico de tensión.",
    "Placa con sulfato avanzado por derrame de café. Requiere limpieza por ultrasonido y micro-soldadura."
]

REPUESTOS_LISTA = [
    {"nombre": "Disco SSD 480GB Kingston", "precio": 32000},
    {"nombre": "Memoria RAM 8GB DDR4 Crucial", "precio": 18500},
    {"nombre": "Pantalla LED 15.6 slim de 30 pines", "precio": 85000},
    {"nombre": "Pasta térmica Artic MX-4", "precio": 4500},
    {"nombre": "Pin de carga DC-Jack universal", "precio": 6200},
    {"nombre": "Cooler notebook Dell Inspiron", "precio": 11000},
    {"nombre": "Módulo Wi-Fi Intel Dual Band", "precio": 8900},
    {"nombre": "Teclado compatible Lenovo ThinkPad", "precio": 22000},
    {"nombre": "Fuente de alimentación certificada 600W", "precio": 45000}
]

def limpiar_tablas():
    """Elimina datos de prueba anteriores en orden para evitar violaciones de clave foránea."""
    print("Limpiando tablas de prueba anteriores...")
    db.session.query(HistorialEstado).delete()
    db.session.query(Notificacion).delete()
    db.session.query(OrdenRepuesto).delete()
    db.session.query(Repuesto).delete()
    db.session.query(OrdenServicio).delete()
    db.session.query(Equipo).delete()
    db.session.query(Cliente).delete()
    db.session.commit()
    print("Limpieza completada.")

def generar_datos():
    # 1. Obtener usuarios y tipos de dispositivos existentes
    admin_user = Usuario.query.filter_by(username='admin').first()
    tecnico_user = Usuario.query.filter_by(username='tecnico').first()
    secretario_user = Usuario.query.filter_by(username='secretario').first()

    if not admin_user or not tecnico_user or not secretario_user:
        print("[ERROR] Los usuarios base no existen en la BD. Ejecuta primero 'python create.py'.")
        return

    tipos_db = TipoDispositivo.query.all()
    if not tipos_db:
        print("[ERROR] Los tipos de dispositivos no existen en la BD. Ejecuta primero 'python create.py'.")
        return
    
    tipos_dict = {t.descripcion: t.id for t in tipos_db}

    # Sembrar catálogo de repuestos
    repuestos_db = []
    for r in REPUESTOS_LISTA:
        codigo = r["nombre"].replace(" ", "-").upper()[:50]
        rep_db = Repuesto.query.filter_by(codigo=codigo).first()
        if not rep_db:
            rep_db = Repuesto(
                codigo=codigo,
                descripcion=r["nombre"],
                categoria="Hardware",
                precio_promedio=r["precio"],
                proveedor="Manual",
                activo=True
            )
            db.session.add(rep_db)
            db.session.flush()
        repuestos_db.append(rep_db)
    db.session.commit()

    # 2. Generar Clientes (generaremos 25 clientes)
    clientes = []
    print("Generando clientes...")
    for i in range(25):
        dni = f"{random.randint(15, 45):02d}{random.randint(100, 999):03d}{random.randint(100, 999):03d}"
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        telefono = f"351{random.randint(2, 9)}{random.randint(100000, 999999)}"
        email = f"{nombre.lower()}.{apellido.lower()}{random.randint(1, 99)}@gmail.com"
        domicilio = f"{random.choice(CALLES)} {random.randint(10, 4500)}"
        localidad = random.choice(LOCALIDADES)

        cliente = Cliente(
            dni_cuil=dni,
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            email=email,
            domicilio=domicilio,
            localidad=localidad
        )
        db.session.add(cliente)
        clientes.append(cliente)

    db.session.flush() # Asignar IDs de clientes

    # 3. Generar Equipos (generaremos 45 equipos para esos 25 clientes)
    equipos = []
    print("Generando equipos...")
    for _ in range(45):
        cliente = random.choice(clientes)
        tipo_desc = random.choice(list(MODELOS_DISPOSITIVOS.keys()))
        tipo_id = tipos_dict[tipo_desc]
        marca, modelo = random.choice(MODELOS_DISPOSITIVOS[tipo_desc])
        
        # Generar número de serie único
        serie = f"{marca[:3].upper()}{random.randint(100000, 999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        descripcion = f"Color {random.choice(['negro', 'gris plata', 'azul', 'blanco'])}. Buen estado exterior."

        equipo = Equipo(
            cliente_id=cliente.id,
            marca=marca,
            modelo=modelo,
            numero_serie=serie,
            tipo_id=tipo_id,
            descripcion=descripcion
        )
        db.session.add(equipo)
        equipos.append(equipo)

    db.session.flush() # Asignar IDs de equipos

    # 4. Generar Órdenes de Servicio (generaremos 75 órdenes)
    print("Generando órdenes de servicio con historiales...")
    
    for i in range(75):
        equipo = random.choice(equipos)
        falla = random.choice(FALLAS)
        accs = random.choice(ACCESORIOS)
        
        # Fecha de recepción aleatoria en los últimos 45 días
        dias_atras = random.randint(0, 45)
        fecha_recepcion = datetime.now() - timedelta(days=dias_atras, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        # Distribución de estados realista
        rand_val = random.random()
        if rand_val < 0.15:
            estado = EstadoOrden.PENDIENTE
        elif rand_val < 0.30:
            estado = EstadoOrden.DIAGNOSTICO
        elif rand_val < 0.45:
            estado = EstadoOrden.PRESUPUESTADO
        elif rand_val < 0.60:
            estado = EstadoOrden.REPARACION
        elif rand_val < 0.75:
            estado = EstadoOrden.LISTO
        else:
            estado = EstadoOrden.ENTREGADO

        # Datos dependientes del estado
        diagnostico = None
        costo = None
        observaciones = None
        fecha_entrega = None
        rep_a_asociar_list = []

        if estado != EstadoOrden.PENDIENTE:
            diagnostico = random.choice(DIAGNOSTICOS)
            
            if estado in [EstadoOrden.PRESUPUESTADO, EstadoOrden.REPARACION, EstadoOrden.LISTO, EstadoOrden.ENTREGADO]:
                costo = random.randint(15, 120) * 1000  # Entre $15.000 y $120.000
                
                # Siempre agregar 1 o 2 repuestos para pruebas
                rep_a_asociar_list = random.sample(repuestos_db, k=random.randint(1, 2))
                for rep in rep_a_asociar_list:
                    costo += int(rep.precio_promedio)

            if estado in [EstadoOrden.LISTO, EstadoOrden.ENTREGADO]:
                observaciones = "Equipo testeado y funcionando correctamente."
            
            if estado == EstadoOrden.ENTREGADO:
                observaciones = "Retirado conforme por el cliente. Garantía de 30 días."
                # Fecha de entrega posterior a la recepción
                fecha_entrega = fecha_recepcion + timedelta(days=random.randint(1, 5), hours=random.randint(1, 10))

        # Crear la Orden de Servicio
        orden = OrdenServicio(
            usuario_id=secretario_user.id if random.random() < 0.7 else admin_user.id,
            equipo_id=equipo.id,
            falla_reportada=falla,
            accesorios=accs,
            fecha_recepcion=fecha_recepcion,
            estado=estado,
            estado_diagnostico=diagnostico,
            fecha_entrega=fecha_entrega,
            costo=costo,
            observaciones=observaciones
        )
        db.session.add(orden)
        db.session.flush() # Para tener el id de la orden y poder hacer el historial

        if rep_a_asociar_list:
            for rep in rep_a_asociar_list:
                orden_rep = OrdenRepuesto(
                    orden_id=orden.id,
                    repuesto_id=rep.id,
                    cantidad=1,
                    precio_unitario=rep.precio_promedio
                )
                db.session.add(orden_rep)

        # 5. Generar Historial de Transiciones de Estado para cada orden de forma coherente
        hist1 = HistorialEstado(
            orden_id=orden.id,
            estado_anterior="Creado",
            estado_nuevo="Pendiente",
            usuario_id=orden.usuario_id,
            observacion_tecnica="Orden ingresada al sistema."
        )
        hist1.fecha_cambio = fecha_recepcion
        db.session.add(hist1)

        # Transición a DIAGNOSTICO
        if estado != EstadoOrden.PENDIENTE:
            fecha_diag = fecha_recepcion + timedelta(hours=random.randint(2, 24))
            hist2 = HistorialEstado(
                orden_id=orden.id,
                estado_anterior="Pendiente",
                estado_nuevo="Diagnostico",
                usuario_id=tecnico_user.id,
                observacion_tecnica="Equipo en laboratorio. Iniciando revisión técnica."
            )
            hist2.fecha_cambio = fecha_diag
            db.session.add(hist2)

            # Transición a PRESUPUESTADO
            if estado != EstadoOrden.DIAGNOSTICO:
                fecha_pres = fecha_diag + timedelta(hours=random.randint(2, 12))
                hist3 = HistorialEstado(
                    orden_id=orden.id,
                    estado_anterior="Diagnostico",
                    estado_nuevo="Presupuestado",
                    usuario_id=tecnico_user.id,
                    observacion_tecnica=f"Diagnóstico finalizado. Presupuesto estimado: ${costo:,.2f}."
                )
                hist3.fecha_cambio = fecha_pres
                db.session.add(hist3)

                # Transición a REPARACION
                if estado != EstadoOrden.PRESUPUESTADO:
                    fecha_rep = fecha_pres + timedelta(days=random.randint(1, 2))
                    hist4 = HistorialEstado(
                        orden_id=orden.id,
                        estado_anterior="Presupuestado",
                        estado_nuevo="Reparacion",
                        usuario_id=secretario_user.id,
                        observacion_tecnica="Cliente aprobó el presupuesto. Iniciando trabajos de reparación."
                    )
                    hist4.fecha_cambio = fecha_rep
                    db.session.add(hist4)

                    # Transición a LISTO
                    if estado != EstadoOrden.REPARACION:
                        fecha_listo = fecha_rep + timedelta(days=random.randint(1, 3))
                        hist5 = HistorialEstado(
                            orden_id=orden.id,
                            estado_anterior="Reparacion",
                            estado_nuevo="Listo",
                            usuario_id=tecnico_user.id,
                            observacion_tecnica="Reparación finalizada con éxito. Control de calidad aprobado."
                        )
                        hist5.fecha_cambio = fecha_listo
                        db.session.add(hist5)

                        # Transición a ENTREGADO
                        if estado == EstadoOrden.ENTREGADO:
                            hist6 = HistorialEstado(
                                orden_id=orden.id,
                                estado_anterior="Listo",
                                estado_nuevo="Entregado",
                                usuario_id=secretario_user.id,
                                observacion_tecnica="Dispositivo entregado al titular. Pago recibido."
                            )
                            hist6.fecha_cambio = fecha_entrega
                            db.session.add(hist6)

    # 6. Generar Notificaciones de prueba
    print("Generando notificaciones de prueba...")
    ordenes_recientes = OrdenServicio.query.order_by(OrdenServicio.fecha_recepcion.desc()).limit(5).all()
    
    # Notificaciones para Técnico
    for i, ord_rec in enumerate(ordenes_recientes[:2]):
        n = Notificacion(
            usuario_id=tecnico_user.id,
            titulo="Nueva Orden Pendiente",
            mensaje=f"Se ha ingresado la orden #{ord_rec.id} para el equipo {ord_rec.equipo.marca} {ord_rec.equipo.modelo}. Falla: {ord_rec.falla_reportada}",
            orden_id=ord_rec.id
        )
        n.fecha_creacion = datetime.now() - timedelta(minutes=(i + 1) * 30)
        db.session.add(n)

    # Notificaciones para Admin
    for i, ord_rec in enumerate(ordenes_recientes[2:4]):
        n = Notificacion(
            usuario_id=admin_user.id,
            titulo="Orden en Diagnóstico",
            mensaje=f"El técnico comenzó a diagnosticar la orden #{ord_rec.id} ({ord_rec.equipo.marca}).",
            orden_id=ord_rec.id
        )
        n.fecha_creacion = datetime.now() - timedelta(hours=(i + 1))
        db.session.add(n)

    # Notificación para Secretario
    if len(ordenes_recientes) > 4:
        ord_rec = ordenes_recientes[4]
        n = Notificacion(
            usuario_id=secretario_user.id,
            titulo="Presupuesto Aprobado",
            mensaje=f"La orden #{ord_rec.id} fue aprobada por el cliente y está lista para reparación.",
            orden_id=ord_rec.id
        )
        n.fecha_creacion = datetime.now() - timedelta(hours=3)
        db.session.add(n)

    db.session.commit()
    print("[OK] ¡Datos de prueba cargados correctamente en la base de datos!")

if __name__ == "__main__":
    with app.app_context():
        limpiar_tablas()
        generar_datos()
