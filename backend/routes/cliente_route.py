from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from backend.controller import cliente_controller
from backend.utils.decorators import login_required, role_required

cliente_bp = Blueprint('clientes', __name__)

@cliente_bp.post('/clientes/editar/<int:id>')
@login_required
@role_required('Administrador', 'Secretario')
def editar_cliente(id):
    success, message = cliente_controller.editar_cliente(id, request.form)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('clientes.gestion_cliente'))

@cliente_bp.get('/clientes/buscar')
@login_required
@role_required('Administrador', 'Secretario')
def buscar_clientes():
    # La limpieza (.strip) y búsqueda suceden en el controller
    return jsonify(cliente_controller.buscar_clientes_json(request.args.get('q')))

@cliente_bp.get('/clientes/verificar-dni/<dni>')
@login_required
@role_required('Administrador', 'Secretario')
def verificar_dni(dni):
    # Delegación de serialización (DTO) al controlador
    exists, cliente_data = cliente_controller.verificar_dni(dni)
    return jsonify({'exists': exists, 'cliente': cliente_data} if exists else {'exists': False})

@cliente_bp.route('/clientes', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Secretario')
def gestion_cliente():
    form_data = {}
    if request.method == 'POST':
        success, result = cliente_controller.crear_cliente(request.form)
        if success:
            flash("Cliente creado exitosamente.", "success")
            return redirect(url_for('clientes.gestion_cliente'))
        
        flash(result, 'error')
        form_data = request.form

    clientes = cliente_controller.obtener_datos_gestion(request.args.get('q'))
    return render_template(
        'gestion_cliente.html',
        clientes=clientes,
        search_query=request.args.get('q', ''),
        form_data=form_data
    )