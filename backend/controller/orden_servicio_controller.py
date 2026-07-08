from backend.models import OrdenServicio, EstadoOrden, HistorialEstado, Cliente, Equipo, TipoDispositivo, Usuario
from backend.controller.tipo_dispositivo_controller import TipoDispositivoController
from database import db
import csv, io
           
class OrdenServicioController:
    
    @staticmethod
    def procesar_datos(datos_formulario, es_creacion=True):
        """Centraliza la sanitización y validación de datos para Ordenes."""
        datos = {
            'equipo_id': datos_formulario.get('equipo_id'),
            'usuario_id': datos_formulario.get('usuario_id'),
            'falla_reportada': (datos_formulario.get('falla_reportada') or '').strip(),
            'accesorios': (datos_formulario.get('accesorios') or '').strip(),
            'costo': datos_formulario.get('costo')
        }

        # Validación de tipos e integridad referencial
        try:
            datos['equipo_id'] = int(datos['equipo_id'])
            datos['usuario_id'] = int(datos['usuario_id'])
            
            if not db.session.get(Equipo, datos['equipo_id']):
                return False, "El equipo asignado no existe."
            
            if not db.session.get(Usuario, datos['usuario_id']):
                return False, "El usuario (operador) asignado no existe."

            datos['costo'] = float(datos['costo']) if datos['costo'] else 0.0
            if datos['costo'] < 0: return False, "El costo no puede ser negativo."
        except (TypeError, ValueError):
            return False, "Datos numéricos inválidos (equipo, usuario o costo)."

        if not datos['falla_reportada']: return False, "La falla reportada es obligatoria."
        if len(datos['falla_reportada']) > 500:
            return False, "La descripción de la falla reportada no puede superar los 500 caracteres."
        if datos['accesorios'] and len(datos['accesorios']) > 500:
            return False, "La descripción de accesorios no puede superar los 500 caracteres."
        
        return True, datos

    @staticmethod
    def crear_ordenServicio(datos_formulario):
        try:
            success, result = OrdenServicioController.procesar_datos(datos_formulario)
            if not success: return False, result

            # Validar equipo disponible
            if OrdenServicio.query.filter(OrdenServicio.equipo_id == result['equipo_id'], 
                                         OrdenServicio.estado != EstadoOrden.ENTREGADO).first():
                return False, "El equipo ya tiene una orden activa."

            nueva_orden = OrdenServicio(**result)
            db.session.add(nueva_orden)
            db.session.flush() # Para obtener el ID

            # Registro histórico profesional
            historial = HistorialEstado(
                orden_id=nueva_orden.id,
                estado_anterior="Ingreso",
                estado_nuevo=EstadoOrden.PENDIENTE.value,
                usuario_id=nueva_orden.usuario_id,
                observacion_tecnica="Ingreso del equipo al taller."
            )
            db.session.add(historial)
            db.session.commit()
            return True, "Orden creada exitosamente."
        except Exception:
            db.session.rollback()
            return False, "Error al crear la orden. Intentá de nuevo."

    @staticmethod
    def _crear_query_filtrado(ticket_id=None, cliente_query=None, equipo_query=None):
        """Construye la consulta base con los filtros aplicados (DNI/CUIL, DNI, marca, etc.)."""
        query = OrdenServicio.query.join(Equipo).join(Cliente)
        
        if ticket_id and ticket_id.strip():
            # Limpiamos prefijos comunes como #, TK- o TK para robustez
            clean_id = ticket_id.upper().replace("TK-", "").replace("TK", "").replace("#", "").strip()
            try:
                numeric_id = int(clean_id)
                query = query.filter(OrdenServicio.id == numeric_id)
            except ValueError:
                query = query.filter(OrdenServicio.id == -1)
                
        if cliente_query:
            query = query.filter(
                (Cliente.nombre.ilike(f"%{cliente_query}%")) |
                (Cliente.apellido.ilike(f"%{cliente_query}%")) |
                (Cliente.telefono.ilike(f"%{cliente_query}%"))
            )
            
        if equipo_query:
            query = query.join(TipoDispositivo, Equipo.tipo_id == TipoDispositivo.id).filter(
                (Equipo.marca.ilike(f"%{equipo_query}%")) |
                (Equipo.modelo.ilike(f"%{equipo_query}%")) |
                (TipoDispositivo.descripcion.ilike(f"%{equipo_query}%"))
            )
            
        return query

    @staticmethod
    def obtener_historial_filtrado(ticket_id=None, cliente_query=None, equipo_query=None):
        """Obtiene las órdenes de servicio filtradas según criterios de búsqueda."""
        query = OrdenServicioController._crear_query_filtrado(ticket_id, cliente_query, equipo_query)
        return query.order_by(OrdenServicio.fecha_recepcion.desc()).all()

    @staticmethod
    def obtener_por_id(orden_id):
        return OrdenServicio.get_by_id(orden_id)

    @staticmethod
    def obtener_datos_lista_activas(ticket_id=None, cliente_query=None, equipo_query=None):
        query = OrdenServicioController._crear_query_filtrado(ticket_id, cliente_query, equipo_query)
        
        # Filtrar solo las activas
        query = query.filter(OrdenServicio.estado != EstadoOrden.ENTREGADO)
        
        ordenes = query.order_by(OrdenServicio.id.desc()).all()
        return {
            'ordenes':           ordenes,
            'clientes':          Cliente.query.all(),
            'tipo_dispositivos': TipoDispositivoController.obtener_todos(),
        }
    
    @staticmethod
    def obtener_tablero_tecnico(usuario_id):
        """Ahora recibe el usuario_id, desacoplado de flask.session"""
        ordenes = OrdenServicio.query.order_by(OrdenServicio.fecha_recepcion.desc()).all()
        
        return {
            'pendiente':      [o for o in ordenes if o.estado == EstadoOrden.PENDIENTE],
            'diagnostico':    [o for o in ordenes if o.estado == EstadoOrden.DIAGNOSTICO],
            'presupuestado':  [o for o in ordenes if o.estado == EstadoOrden.PRESUPUESTADO],
            'reparacion':     [o for o in ordenes if o.estado == EstadoOrden.REPARACION],
            'listo':          [o for o in ordenes if o.estado == EstadoOrden.LISTO],
            'entregado':      [o for o in ordenes if o.estado == EstadoOrden.ENTREGADO],
            'usuario_id':     usuario_id,
        }
    
    @staticmethod
    def generar_csv_historial(args):
        if args.get('activos_only') == 'true':
            datos = OrdenServicioController.obtener_datos_lista_activas(
                ticket_id=args.get('ticket_id', '').strip(),
                cliente_query=args.get('cliente', '').strip(),
                equipo_query=args.get('equipo', '').strip(),
            )
            ordenes = datos['ordenes']
        else:
            ordenes = OrdenServicioController.obtener_historial_filtrado(
                ticket_id=args.get('ticket_id', '').strip(),
                cliente_query=args.get('cliente', '').strip(),
                equipo_query=args.get('equipo', '').strip(),
            )
        output = io.StringIO()
        output.write('\ufeff')  # BOM para Excel
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['Ticket ID', 'Cliente', 'DNI/CUIL', 'Teléfono', 'Email',
                        'Tipo', 'Marca', 'Modelo', 'S/N', 'Estado',
                        'Fecha Recepción', 'Fecha Entrega', 'Costo ($)', 'Observaciones'])
        for o in ordenes:
            writer.writerow([
                f"TK-{o.id:04d}",
                f"{o.equipo.cliente.apellido}, {o.equipo.cliente.nombre}" if o.equipo and o.equipo.cliente else '—',
                o.equipo.cliente.dni_cuil if o.equipo and o.equipo.cliente else '—',
                o.equipo.cliente.telefono if o.equipo and o.equipo.cliente else '—',
                o.equipo.cliente.email if o.equipo and o.equipo.cliente else '—',
                o.equipo.tipo.descripcion if o.equipo and o.equipo.tipo else '—',
                o.equipo.marca if o.equipo else '—',
                o.equipo.modelo if o.equipo else '—',
                o.equipo.numero_serie if o.equipo else '—',
                o.estado.value if o.estado else '—',
                o.fecha_recepcion.strftime('%d/%m/%Y %H:%M') if o.fecha_recepcion else '—',
                o.fecha_entrega.strftime('%d/%m/%Y %H:%M') if o.fecha_entrega else '—',
                f"{o.costo:.2f}" if o.costo is not None else '0.00',
                o.observaciones or '—',
            ])
        return output.getvalue()    