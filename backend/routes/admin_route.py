import json
from datetime import datetime
from flask import Blueprint, Response, request, redirect, url_for, flash, session
from backend.controller import admin_controller
from backend.utils.decorators import login_required, role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/backup/download')
@login_required
@role_required('Administrador')
def download_backup():
    usuario_id = session.get('usuario_id')
    success, result = admin_controller.generar_backup(usuario_id)
    
    if not success:
        flash(result, "error")
        return redirect(url_for('vistas.dashboard'))

    try:
        json_str = json.dumps(result, indent=4, ensure_ascii=False)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"techflow_backup_{timestamp}.json"

        return Response(
            json_str,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception:
        flash("Error al procesar el archivo de backup.", "error")
        return redirect(url_for('vistas.dashboard'))

@admin_bp.get('/admin/cambiar-rol')
@login_required
def cambiar_rol():
    # Delegamos toda la validación al AdminController.
    success, rol_normalizado = admin_controller.validar_simulacion_rol(
        usuario_id=session.get('usuario_id'), 
        nuevo_rol_descripcion=request.args.get('rol', '')
    )
    
    if success:
        # Enrutamiento y nombres de sesión son responsabilidad del Blueprint
        role_to_route = {
            'administrador': 'vistas.dashboard',
            'tecnico': 'vistas.technician',
            'secretario': 'vistas.secretary'
        }
        
        role_to_session_name = {
            'administrador': 'Administrador',
            'tecnico': 'Técnico',
            'secretario': 'Secretario'
        }
        
        route = role_to_route.get(rol_normalizado)
        session_name = role_to_session_name.get(rol_normalizado, rol_normalizado)
        
        if route:
            session['rol_descripcion'] = session_name
            flash(f"Simulando entorno como {session_name}.", "success")
            return redirect(url_for(route))
    
    flash(rol_normalizado if not success and isinstance(rol_normalizado, str) else "No tienes permisos o el rol es inválido.", "error")
    return redirect(url_for('vistas.dashboard'))
