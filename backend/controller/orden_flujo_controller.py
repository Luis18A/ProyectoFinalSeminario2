from backend.utils.predictor_service import PredictorService
from backend.models.OrdenServicio import OrdenServicio
from database import db
from datetime import datetime
import json
from flask import url_for
from backend.utils.sse_service import sse_service
from backend.models.EstadoOrden import EstadoOrden
from backend.models.HistorialEstado import HistorialEstado
from backend.models.Notificacion import Notificacion
from backend.models.Usuario import Usuario
from backend.models.Rol import Rol

class OrdenFlujoController:
    @staticmethod
    def actualizar_ordenServicio(orden_id, datos_formulario, rol_actual=''):
        """Actualiza la orden y maneja el cambio de estado con historial."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden no encontrada."

            # REGLA: Secretario solo puede modificar la orden en estado PENDIENTE
            if rol_actual == 'Secretario' and orden.estado != EstadoOrden.PENDIENTE:
                return False, "La secretaría no tiene permitido modificar campos de la orden una vez que ha salido del estado Pendiente."

            estado_anterior_enum = orden.estado

            # Capturamos datos del formulario
            nuevo_estado_id = datos_formulario.get('estado')
            try:
                usuario_id = int(datos_formulario.get('usuario_id'))
            except (TypeError, ValueError):
                return False, "ID de usuario inválido."
            observacion = datos_formulario.get('observaciones')
            costo = datos_formulario.get('costo')
            estado_anterior_nombre = orden.estado.value
            estado_nuevo_nombre = orden.estado.value
            hubo_cambios = False
            es_estado_cerrado = orden.estado in (EstadoOrden.LISTO, EstadoOrden.ENTREGADO)

            # Validar modificaciones de montos en estados cerrados (LISTO / ENTREGADO)
            if es_estado_cerrado:
                costo_nuevo_val = None
                if costo and str(costo).strip():
                    try:
                        costo_nuevo_val = float(costo)
                    except ValueError:
                        pass
                
                if costo_nuevo_val is not None and costo_nuevo_val != (orden.costo or 0.0):
                    if rol_actual != 'Administrador':
                        return False, "No tienes permisos para modificar montos en una orden cerrada."
                    else:
                        if not observacion or not str(observacion).strip():
                            return False, "La justificación técnica es obligatoria para modificar el monto de una orden cerrada."
                        costo_anterior = orden.costo or 0.0
                        observacion = f"Modificación de costo en estado cerrado por el Administrador. Monto anterior: ${costo_anterior:.2f} -> Monto nuevo: ${costo_nuevo_val:.2f}. Motivo: {observacion.strip()}"
                        orden.costo = costo_nuevo_val
                        hubo_cambios = True

            # 1. Si el estado cambió
            if nuevo_estado_id and nuevo_estado_id != orden.estado.name:
                try:
                    nuevo_enum = EstadoOrden[nuevo_estado_id]
                except KeyError:
                    return False, f"Estado '{nuevo_estado_id}' no es válido."
                
                # REGLA: Si la orden está PRESUPUESTADO, el Técnico no puede cambiar el estado manually.
                # Solo Administrador y Secretario pueden confirmar o rechazar presupuestos.
                if orden.estado == EstadoOrden.PRESUPUESTADO and rol_actual == 'Técnico':
                    return False, "No tienes permisos para aprobar o rechazar presupuestos. Esto debe ser realizado por la secretaría o administración."
                
                if nuevo_enum == EstadoOrden.ENTREGADO and rol_actual == 'Técnico':
                    return False, "El técnico no tiene permitido entregar equipos. Esto debe ser realizado por la secretaría o administración."
                
                # Validar la transición usando la máquina de estados
                permitidos = EstadoOrden.transiciones_permitidas(orden.estado)
                if nuevo_enum not in permitidos:
                    return False, f"Transición de estado no permitida: {orden.estado.value} -> {nuevo_enum.value}."
                
                # Validar obligatoriedad de observación en retrocesos
                es_retroceso = (
                    (orden.estado == EstadoOrden.PRESUPUESTADO and nuevo_enum == EstadoOrden.DIAGNOSTICO) or
                    (orden.estado == EstadoOrden.REPARACION and nuevo_enum == EstadoOrden.PRESUPUESTADO)
                )
                if es_retroceso:
                    if not observacion or not str(observacion).strip():
                        return False, "La observación técnica es obligatoria al retroceder el estado de la orden."
                
                orden.estado = nuevo_enum
                estado_nuevo_nombre = orden.estado.value
                hubo_cambios = True
                    
            # 2. Si hay un costo nuevo y no es estado cerrado
            if costo and not es_estado_cerrado:
                try:
                    costo_val = float(costo)
                    if costo_val < 0:
                        return False, "El costo total no puede ser negativo."
                    if costo_val != (orden.costo or 0.0):
                        orden.costo = costo_val
                        hubo_cambios = True
                except ValueError:
                    return False, "El costo total debe ser un número válido."
                
            # Validar que si el estado final no es PENDIENTE, el diagnóstico no esté vacío
            estado_final = orden.estado
            if nuevo_estado_id:
                try:
                    estado_final = EstadoOrden[nuevo_estado_id]
                except KeyError:
                    pass

            if estado_final != EstadoOrden.PENDIENTE:
                diag_campo = datos_formulario.get('estado_diagnostico')
                if diag_campo is not None:
                    if not str(diag_campo).strip():
                        return False, "El diagnóstico técnico es obligatorio para el estado seleccionado."
                else:
                    if not (orden.estado_diagnostico or '').strip():
                        return False, "El diagnóstico técnico es obligatorio para el estado seleccionado."

            # Actualizamos otros campos técnicos con validaciones de longitud
            if datos_formulario.get('estado_diagnostico') is not None:
                new_diag = datos_formulario.get('estado_diagnostico').strip()
                if len(new_diag) > 255:
                    return False, "El diagnóstico técnico no puede superar los 255 caracteres."
                if new_diag != (orden.estado_diagnostico or ''):
                    orden.estado_diagnostico = new_diag
                    hubo_cambios = True
            if datos_formulario.get('falla_reportada') is not None:
                new_falla = datos_formulario.get('falla_reportada').strip()
                if len(new_falla) > 500:
                    return False, "La falla reportada no puede superar los 500 caracteres."
                if new_falla != (orden.falla_reportada or ''):
                    orden.falla_reportada = new_falla
                    hubo_cambios = True
            if datos_formulario.get('accesorios') is not None:
                new_acc = datos_formulario.get('accesorios').strip()
                if len(new_acc) > 500:
                    return False, "La descripción de accesorios no puede superar los 500 caracteres."
                if new_acc != (orden.accesorios or ''):
                    orden.accesorios = new_acc
                    hubo_cambios = True

            # Detección y persistencia de Trabajo Realizado (observaciones de la orden)
            nota_modificada = False
            observacion_limpia = ""
            if datos_formulario.get('observaciones') is not None:
                new_obs = datos_formulario.get('observaciones').strip()
                if len(new_obs) > 500:
                    return False, "La descripción de trabajo realizado no puede superar los 500 caracteres."
                if new_obs != (orden.observaciones or ''):
                    orden.observaciones = new_obs
                    hubo_cambios = True
                    nota_modificada = True
                    observacion_limpia = new_obs

            # Validar que efectivamente haya algún cambio antes de guardar
            if not hubo_cambios:
                return False, "No se detectaron cambios en la orden de servicio."

            # 3. Si hubo algún cambio, grabamos el historial.
            # En el historial técnico grabamos la observación/trabajo realizado solo si fue modificado en esta acción,
            # o bien un mensaje estándar si hubo un cambio de estado automático.
            historial_obs = None
            if nuevo_estado_id and nuevo_estado_id != estado_anterior_enum.name:
                try:
                    nuevo_enum = EstadoOrden[nuevo_estado_id]
                except KeyError:
                    nuevo_enum = None
                
                if nuevo_enum == EstadoOrden.PRESUPUESTADO:
                    historial_obs = "Presupuesto de repuestos y mano de obra enviado a secretaría para confirmación del cliente."
                elif nuevo_enum == EstadoOrden.ENTREGADO:
                    historial_obs = "Orden finalizada y entregada al cliente."
                else:
                    historial_obs = observacion_limpia if (nota_modificada and observacion_limpia) else None
            else:
                historial_obs = observacion_limpia if (nota_modificada and observacion_limpia) else None

            historial = HistorialEstado(
                orden_id=orden.id,
                usuario_id=usuario_id,
                estado_anterior=estado_anterior_nombre,
                estado_nuevo=estado_nuevo_nombre,
                observacion_tecnica=historial_obs
            )
            db.session.add(historial)
            db.session.commit()

            # Enviar notificaciones si cambió el estado
            if nuevo_state_changed := (nuevo_estado_id and nuevo_estado_id != estado_anterior_enum.name):
                OrdenFlujoController._enviar_notificaciones_cambio_estado(
                    orden=orden,
                    estado_anterior=estado_anterior_enum,
                    nuevo_estado=nuevo_enum,
                    observacion=observacion_limpia
                )

            return True, 'Ticket actualizado correctamente.'
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar la orden: {str(e)}"
            
    @staticmethod
    def _enviar_notificaciones_cambio_estado(orden, estado_anterior, nuevo_estado, observacion=None):
        """Envía notificaciones a los destinatarios correspondientes al cambiar el estado de la orden."""
        try:
            notificaciones = []

            # 1. Notificaciones al técnico (Aprobación o Rechazo de Presupuesto)
            if estado_anterior == EstadoOrden.PRESUPUESTADO:
                # Encontrar el técnico que envió el presupuesto (el último en cambiar a PRESUPUESTADO)
                registro_presupuesto = HistorialEstado.query.filter_by(
                    orden_id=orden.id, 
                    estado_nuevo=EstadoOrden.PRESUPUESTADO.value
                ).order_by(HistorialEstado.fecha_cambio.desc()).first()
                
                tecnicos_a_notificar = []
                if registro_presupuesto:
                    tecnicos_a_notificar.append(registro_presupuesto.usuario_id)
                else:
                    # Fallback: enviar a todos los técnicos
                    tecnicos = Usuario.query.join(Rol).filter(Rol.descripcion == 'Técnico').all()
                    tecnicos_a_notificar = [t.id for t in tecnicos]
                    
                if nuevo_estado == EstadoOrden.REPARACION:
                    titulo = "Presupuesto Aprobado"
                    mensaje = f"El presupuesto para el Ticket #{orden.id} ({orden.equipo.marca} {orden.equipo.modelo}) ha sido aprobado. Puede comenzar la reparación."
                    for t_id in tecnicos_a_notificar:
                        notificaciones.append(Notificacion(usuario_id=t_id, titulo=titulo, mensaje=mensaje, orden_id=orden.id))
                elif nuevo_estado == EstadoOrden.DIAGNOSTICO:
                    titulo = "Presupuesto Rechazado"
                    motivo_str = f" Motivo: {observacion}" if observacion else ""
                    mensaje = f"El presupuesto para el Ticket #{orden.id} ({orden.equipo.marca} {orden.equipo.modelo}) fue rechazado y volvió a diagnóstico.{motivo_str}"
                    for t_id in tecnicos_a_notificar:
                        notificaciones.append(Notificacion(usuario_id=t_id, titulo=titulo, mensaje=mensaje, orden_id=orden.id))

            # 2. Notificaciones a secretarias y administradores (Presupuesto requerido o Equipo Listo)
            if nuevo_estado in (EstadoOrden.PRESUPUESTADO, EstadoOrden.LISTO):
                if nuevo_estado == EstadoOrden.PRESUPUESTADO:
                    titulo_sec = "Presupuesto Requerido"
                    mensaje_sec = f"El Ticket #{orden.id} ({orden.equipo.marca} {orden.equipo.modelo}) requiere aprobación de presupuesto."
                else: # EstadoOrden.LISTO
                    titulo_sec = "Equipo Listo"
                    mensaje_sec = f"El equipo del Ticket #{orden.id} ({orden.equipo.marca} {orden.equipo.modelo}) ya se encuentra listo para entregar."
                    
                secretarios = Usuario.query.join(Rol).filter(Rol.descripcion.in_(['Secretario', 'Administrador'])).all()
                for sec in secretarios:
                    notificaciones.append(Notificacion(usuario_id=sec.id, titulo=titulo_sec, mensaje=mensaje_sec, orden_id=orden.id))

            # Agregar y commitear todas las notificaciones juntas al final
            for n in notificaciones:
                db.session.add(n)
            db.session.commit()

            # Anunciar notificaciones en tiempo real vía Server-Sent Events (SSE)
            for n in notificaciones:
                try:
                    sse_service.announce(json.dumps({
                        'type': 'notification',
                        'usuario_id': n.usuario_id,
                        'titulo': n.titulo,
                        'mensaje': n.mensaje,
                        'orden_id': n.orden_id
                    }))
                except Exception as sse_err:
                    print(f"[SSE Error] No se pudo anunciar notificación: {sse_err}")
        except Exception as e:
            print(f"Error al enviar notificaciones: {str(e)}")
            db.session.rollback()

    @staticmethod
    def cambiar_estado_flujo(orden_id, nuevo_estado_name, usuario_id, observacion=None, rol_actual=''):
        """Cambia el estado de una orden con validación de rol y máquina de estados."""
        try:
            orden = OrdenServicio.get_by_id(orden_id)
            if not orden:
                return False, "Orden de servicio no encontrada."

            if nuevo_estado_name not in EstadoOrden.__members__:
                return False, f"Estado '{nuevo_estado_name}' no válido."

            nuevo_estado = EstadoOrden[nuevo_estado_name]

            if nuevo_estado == orden.estado:
                return True, f"La orden ya está en estado {nuevo_estado.value}."

            # ── Restricciones por rol ──────────────────────────────────
            if rol_actual == 'Técnico':
                if orden.estado == EstadoOrden.PRESUPUESTADO:
                    return False, "No tenés permisos para aprobar o rechazar presupuestos."
                if nuevo_estado == EstadoOrden.ENTREGADO:
                    return False, "El técnico no puede marcar equipos como entregados."

            # ── Validar transición con la máquina de estados ──────────
            permitidos = EstadoOrden.transiciones_permitidas(orden.estado)
            if nuevo_estado not in permitidos:
                return False, f"Transición no permitida: {orden.estado.value} → {nuevo_estado.value}."

            # ── Diagnóstico obligatorio para estados distintos de PENDIENTE ──
            if nuevo_estado != EstadoOrden.PENDIENTE and not (orden.estado_diagnostico or '').strip():
                return False, "La orden de servicio debe tener un diagnóstico técnico registrado para cambiar al estado seleccionado."

            # ── Observación obligatoria en retrocesos ─────────────────
            es_retroceso = (
                (orden.estado == EstadoOrden.PRESUPUESTADO and nuevo_estado == EstadoOrden.DIAGNOSTICO) or
                (orden.estado == EstadoOrden.REPARACION    and nuevo_estado == EstadoOrden.PRESUPUESTADO)
            )
            if es_retroceso and not (observacion and str(observacion).strip()):
                return False, "La observación técnica es obligatoria al retroceder el estado."

            if nuevo_estado == EstadoOrden.ENTREGADO:
                orden.fecha_entrega = datetime.now()

            estado_anterior = orden.estado

            try:
                # 1. Capturás el objeto devuelto por el modelo
                nuevo_historial = orden.preparar_cambio_estado(nuevo_estado, usuario_id, observacion)
                
                # 2. El controlador asume la responsabilidad de agregarlo a la sesión
                db.session.add(nuevo_historial)
                
                # 3. Y finalmente guardamos todo en una sola transacción atómica
                db.session.commit()
            except ValueError as e:
                db.session.rollback()
                return False, str(e)
            except Exception:
                db.session.rollback()
                return False, "Error al cambiar el estado."

            # Notificaciones fuera de la transacción — fallo no revierte el cambio de estado
            OrdenFlujoController._enviar_notificaciones_cambio_estado(
                orden=orden,
                estado_anterior=estado_anterior,
                nuevo_estado=nuevo_estado,
                observacion=observacion
            )

            return True, f"Estado actualizado a {nuevo_estado.value}."

        except Exception:
            db.session.rollback()
            return False, "Error al cambiar el estado. Intentá de nuevo."

    @staticmethod
    def obtener_datos_gestion_ticket(orden_id, rol_actual):
        """Obtiene el historial de estados, permisos y predicciones de fallas para la gestión de un ticket."""
        orden = OrdenServicio.get_by_id(orden_id)
        if not orden:
            return None
            
        historial = HistorialEstado.query.filter_by(orden_id=orden_id).order_by(HistorialEstado.fecha_cambio.desc()).all()
        estados = EstadoOrden
        opciones_estado = EstadoOrden.transiciones_permitidas(orden.estado)
        if rol_actual == 'Técnico':
            opciones_estado = [e for e in opciones_estado if e != EstadoOrden.ENTREGADO]
        # Construir opciones detalladas indicando dirección (Actual, Avanzar, Retroceder)
        lista_ordenada = [
            EstadoOrden.PENDIENTE,
            EstadoOrden.DIAGNOSTICO,
            EstadoOrden.PRESUPUESTADO,
            EstadoOrden.REPARACION,
            EstadoOrden.LISTO,
            EstadoOrden.ENTREGADO
        ]
        
        try:
            idx_actual = lista_ordenada.index(orden.estado)
        except ValueError:
            idx_actual = -1
            
        opciones_estado_detalladas = []
        for e in opciones_estado:
            try:
                idx_opcion = lista_ordenada.index(e)
            except ValueError:
                idx_opcion = -1
                
            if e == orden.estado:
                label = f"• {e.value} (Actual)"
                direccion = "actual"
            elif idx_opcion > idx_actual:
                label = f"➔ {e.value} (Avanzar)"
                direccion = "avanzar"
            else:
                label = f"↺ {e.value} (Retroceder)"
                direccion = "retroceder"
                
            opciones_estado_detalladas.append({
                'name': e.name,
                'value': e.value,
                'label': label,
                'direccion': direccion,
                'is_actual': e == orden.estado
            })
            
        if rol_actual == 'Secretario':
            puede_editar = (orden.estado == EstadoOrden.PENDIENTE)
        else:
            puede_editar = rol_actual in ('Técnico', 'Administrador')
        puede_editar_costos = orden.estado in (EstadoOrden.DIAGNOSTICO, EstadoOrden.REPARACION)
        predicted_failures = PredictorService.predict_failures(orden.equipo_id)
        
        return {
            'orden': orden,
            'historial': historial,
            'estados': estados,
            'opciones_estado': opciones_estado,
            'opciones_estado_detalladas': opciones_estado_detalladas,
            'puede_editar': puede_editar,
            'puede_editar_costos': puede_editar_costos,
            'rol_actual': rol_actual,
            'predicted_failures': predicted_failures
        }

    @staticmethod
    def obtener_config_json_ticket(orden_id, rol_actual, is_readonly=False):
        """Genera el JSON de configuración para el frontend de gestión de ticket."""
        datos = OrdenFlujoController.obtener_datos_gestion_ticket(orden_id, rol_actual)
        if not datos:
            return None
            
        if is_readonly:
            datos.update({'puede_editar': False, 'puede_editar_costos': False})
            
        orden = datos['orden']
        return {
            'repuestosActivos': orden.repuestos or [],
            'ordenId': orden.id,
            'ordenCostoInicial': orden.costo or 0.0,
            'puedeEditar': datos['puede_editar'],
            'puedeEditarCostos': datos['puede_editar_costos'],
            'rolActual': datos['rol_actual'],
            'estadoActual': orden.estado.name,
            'technicianUrl': url_for('vistas.technician')
        }