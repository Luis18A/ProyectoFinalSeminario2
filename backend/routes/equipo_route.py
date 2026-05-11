from backend.controller.equipo_controller import EquipoController
from backend.models.Equipo import Equipo
from flask import Blueprint, request, render_template, request, url_for, flash, redirect
equipo_bp = Blueprint('equipo', __name__)

@equipo_bp.route('/equipo', methods=['POST'])
def crear_equipo():
    success, message = EquipoController.crear_equipo(request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    cliente_id = request.form.get('cliente_id')
    return redirect(url_for('vistas.gestion_equipos', cliente_id=cliente_id))
