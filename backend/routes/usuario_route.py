import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response, jsonify
from backend.controller.usuario_controller import UsuarioController
from backend.utils.decorators import login_required, role_required
from backend.controller.ordenServicio_controller import OrdenServicioController
from backend.controller.tipoDispositivo_controller import TipoDispositivoController
from backend.controller.admin_controller import AdminController


# Creamos el Blueprint para los usuarios
usuarios_bp = Blueprint('usuarios', __name__)

from backend.models.Rol import Rol

@usuarios_bp.get('/usuarios')
@login_required
@role_required('Administrador')
def listar_usuarios():
    usuarios_lista = UsuarioController.obtener_todos()
    roles_lista = Rol.query.all()
    
    cant_activos = sum(1 for u in usuarios_lista if u.activo)
    cant_roles = len(roles_lista)
    
    from datetime import datetime
    from backend.models.HistorialEstado import HistorialEstado
    last_audit = HistorialEstado.query.order_by(HistorialEstado.fecha_cambio.desc()).first()
    if last_audit:
        diff = datetime.now() - last_audit.fecha_cambio
        if diff.days > 0:
            tiempo_auditoria = f"Hace {diff.days}d"
        elif diff.seconds // 3600 > 0:
            tiempo_auditoria = f"Hace {diff.seconds // 3600}h"
        elif diff.seconds // 60 > 0:
            tiempo_auditoria = f"Hace {diff.seconds // 60}m"
        else:
            tiempo_auditoria = "Hace instantes"
    else:
        tiempo_auditoria = "Sin registros"
        
    return render_template(
        'gestion_usuarios.html', 
        usuarios=usuarios_lista, 
        roles=roles_lista,
        cant_activos=cant_activos,
        cant_roles=cant_roles,
        tiempo_auditoria=tiempo_auditoria
    )

@usuarios_bp.post('/usuarios')
@login_required
@role_required('Administrador')
def crear_usuario():
    # Validación simple: verificar que el form no esté vacío
    if not request.form:
        flash('Datos de formulario inválidos', 'error')
        return redirect(url_for('usuarios.listar_usuarios'))
    
    # Le delegamos la lógica de negocio al controlador
    success, message = UsuarioController.crear_usuario(request.form)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    # El router redirige de vuelta a la función listar_usuarios
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/eliminar/<int:id>')
@login_required
@role_required('Administrador')
def eliminar_usuario(id):
    if session.get('usuario_id') == id:
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for('usuarios.listar_usuarios'))
        
    if UsuarioController.eliminar_usuario(id):
        flash("Usuario eliminado correctamente.", "success")
    else:
        flash("Error al eliminar el usuario.", "error")
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/actualizar/<int:id>')
@login_required
@role_required('Administrador')
def actualizar_usuario(id):
    
    if not request.form:
        flash('Datos de formulario inválidos', 'error')
        return redirect(url_for('usuarios.listar_usuarios'))

    success, message = UsuarioController.actualizar_usuario(id, request.form)
    if success:
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.route('/admin/backup/download')
@login_required
@role_required('Administrador')
def download_backup():
    try:
        backup_dict = AdminController.generar_backup(session.get('usuario_id', 1))
        json_str = json.dumps(backup_dict, indent=4, ensure_ascii=False)
        return Response(
            json_str,
            mimetype="application/json",
            headers={"Content-disposition": "attachment; filename=techflow_backup.json"}
        )
    except Exception as e:
        flash(f"Error al generar backup: {str(e)}", "error")
        return redirect(url_for('vistas.dashboard'))

@usuarios_bp.route('/secretary')
@login_required
@role_required('Secretario', 'Administrador')
def secretary():
    return redirect(url_for('ordenServicio.listar_ordenes_view'))

@usuarios_bp.route('/technician')
@login_required
@role_required('Técnico', 'Administrador')
def technician():
    from backend.models.OrdenServicio import OrdenServicio
    from backend.models.EstadoOrden import EstadoOrden
    
    ordenes = OrdenServicio.get_all()
    
    pendiente     = [o for o in ordenes if o.estado == EstadoOrden.PENDIENTE]
    diagnostico   = [o for o in ordenes if o.estado == EstadoOrden.DIAGNOSTICO]
    presupuestado = [o for o in ordenes if o.estado == EstadoOrden.PRESUPUESTADO]
    reparacion    = [o for o in ordenes if o.estado == EstadoOrden.REPARACION]
    listo         = [o for o in ordenes if o.estado == EstadoOrden.LISTO]
    entregado     = [o for o in ordenes if o.estado == EstadoOrden.ENTREGADO]
    
    return render_template('technician_board.html',
                           pendiente=pendiente,
                           diagnostico=diagnostico,
                           presupuestado=presupuestado,
                           reparacion=reparacion,
                           listo=listo,
                           entregado=entregado)

@usuarios_bp.route('/admin/cambiar-rol')
@login_required
def cambiar_rol():
    real_rol = session.get('real_rol_descripcion', '')
    if real_rol != 'Administrador':
        flash("No tienes permisos para cambiar de rol.", "error")
        return redirect(url_for('vistas.login'))
    
    nuevo_rol = request.args.get('rol')
    if nuevo_rol not in ('Administrador', 'Técnico', 'Secretario'):
        flash("Rol de simulación no válido.", "error")
        return redirect(url_for('vistas.dashboard'))
    
    session['rol_descripcion'] = nuevo_rol
    flash(f"Simulando entorno como {nuevo_rol}.", "success")
    
    if nuevo_rol == 'Administrador':
        return redirect(url_for('vistas.dashboard'))
    elif nuevo_rol == 'Técnico':
        return redirect(url_for('usuarios.technician'))
    elif nuevo_rol == 'Secretario':
        return redirect(url_for('usuarios.secretary'))
        
    return redirect(url_for('vistas.dashboard'))

@usuarios_bp.post('/notificaciones/<int:id>/leer')
@login_required
def leer_notificacion(id):
    from backend.models.Notificacion import Notificacion
    from database import db
    notif = Notificacion.query.filter_by(id=id, usuario_id=session.get('usuario_id')).first()
    if notif:
        notif.leido = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Notificación no encontrada.'}), 404

@usuarios_bp.post('/notificaciones/leer-todas')
@login_required
def leer_todas_notificaciones():
    from backend.models.Notificacion import Notificacion
    from database import db
    usuario_id = session.get('usuario_id')
    Notificacion.query.filter_by(usuario_id=usuario_id, leido=False).update({Notificacion.leido: True}, synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True})