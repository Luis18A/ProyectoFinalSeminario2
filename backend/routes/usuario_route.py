from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.controller.usuario_controller import UsuarioController
from backend.utils.decorators import login_required, role_required
from backend.controller.ordenServicio_controller import OrdenServicioController


# Creamos el Blueprint para los usuarios
usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.get('/usuarios')
@role_required('Administrador', 'Administrdor')
def listar_usuarios():
    usuarios_lista = UsuarioController.obtener_todos()
    return render_template('gestion_usuarios.html', usuarios=usuarios_lista)

@usuarios_bp.post('/usuarios')
@role_required('Administrador', 'Administrdor')
def crear_usuario():
    # Le delegamos la lógica de negocio al controlador
    success, message = UsuarioController.crear_usuario(request.form)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    # El router redirige de vuelta a la función listar_usuarios
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/eliminar/<int:id>')
@role_required('Administrador', 'Administrdor')
def eliminar_usuario(id):
    if UsuarioController.eliminar_usuario(id):
        flash("Usuario eliminado correctamente.", "success")
    else:
        flash("Error al eliminar el usuario.", "error")
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/actualizar/<int:id>')
@role_required('Administrador', 'Administrdor')
def actualizar_usuario(id):
    if UsuarioController.actualizar_usuario(id, request.form):
        flash("Usuario actualizado correctamente.", "success")
    else:
        flash("Error al actualizar el usuario.", "error")
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.route('/admin/backup/download')
@role_required('Administrador', 'Administrdor')
def download_backup():
    from flask import Response, session, redirect, url_for
    import json
    
    try:
        backup_dict = UsuarioController.generar_backup(session.get('usuario_id', 1))
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
@role_required('Secretario', 'Secretaria', 'Administrador', 'Administrdor')
def secretary():
    clientes, usuarios, ordenes = UsuarioController.obtener_datos_secretaria()
    return render_template('secretary_view.html',
                           clientes=clientes,
                           usuarios=usuarios,
                           ordenes=ordenes)

@usuarios_bp.route('/technician')
@role_required('Técnico', 'Administrador', 'Administrdor')
def technician():
    pendientes, en_trabajo, listos = OrdenServicioController.obtener_tickets_tablero()
    return render_template('technician_board.html',
                           pendientes=pendientes,
                           en_trabajo=en_trabajo,
                           listos=listos)

@usuarios_bp.route('/admin/cambiar-rol')
@login_required
def cambiar_rol():
    from flask import session, request, redirect, url_for, flash
    real_rol = session.get('real_rol_descripcion', '')
    if real_rol not in ('Administrador', 'Administrdor'):
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