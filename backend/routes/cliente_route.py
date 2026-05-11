from flask import Blueprint, render_template, request, redirect, url_for
from flask import flash
from backend.models.Cliente import Cliente
from backend.controller.cliente_controller import ClienteController

cliente_bp = Blueprint('clientes', __name__)

@cliente_bp.post('/clientes')
def crear_cliente():
    success, message = ClienteController.crear_cliente(request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('vistas.gestion_cliente'))
