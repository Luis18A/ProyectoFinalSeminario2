
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
    try:
        usuario_id = session.get('usuario_id')
        backup_dict = admin_controller.generar_backup(usuario_id)
        json_str = json.dumps(backup_dict, indent=4, ensure_ascii=False)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"techflow_backup_{timestamp}.json"

        return Response(
            json_str,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception:
        flash("Error al generar el backup. Contactá al administrador del sistema.", "error")
        return redirect(url_for('vistas.dashboard'))

@admin_bp.get('/admin/cambiar-rol')
@login_required
def cambiar_rol():
    # Delegamos toda la validación al AdminController.
    success, destination = admin_controller.simular_rol(
        usuario_id=session.get('usuario_id'), 
        nuevo_rol=request.args.get('rol')
    )
    
    if success and destination:
        session['rol_descripcion'] = request.args.get('rol')
        flash(f"Simulando entorno como {request.args.get('rol')}.", "success")
        return redirect(url_for(destination))
    
    flash("No tienes permisos o el rol es inválido.", "error")
    return redirect(url_for('vistas.dashboard'))
