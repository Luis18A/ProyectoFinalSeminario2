from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from backend.controller.cliente_controller import ClienteController
from backend.utils.decorators import login_required, role_required

cliente_bp = Blueprint('clientes', __name__)

@cliente_bp.post('/clientes/editar/<int:id>')
@login_required
@role_required('Administrador', 'Secretario')
def editar_cliente(id):
    success, message = ClienteController.editar_cliente(id, request.form)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('clientes.gestion_cliente'))

@cliente_bp.get('/listar_clientes')
@login_required
@role_required('Administrador', 'Secretario')
def listar_clientes():
    return render_template('clientes.html')

@cliente_bp.get('/clientes/buscar')
@login_required
@role_required('Administrador', 'Secretario')
def buscar_clientes():
    # La limpieza (.strip) y búsqueda suceden en el controller
    return jsonify(ClienteController.buscar_clientes_json(request.args.get('q')))

@cliente_bp.get('/clientes/verificar-dni/<dni>')
@login_required
@role_required('Administrador', 'Secretario')
def verificar_dni(dni):
    # Delegación de serialización (DTO) al controlador
    exists, cliente_data = ClienteController.verificar_dni(dni)
    return jsonify({'exists': exists, 'cliente': cliente_data} if exists else {'exists': False})

@cliente_bp.route('/clientes', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Secretario')
def gestion_cliente():
    if request.method == 'POST':
        success, message = ClienteController.crear_cliente(request.form)
        flash(message, 'success' if success else 'error')
        if success:
            return redirect(url_for('clientes.gestion_cliente'))
        clientes = ClienteController.obtener_datos_gestion(request.args.get('q'))
        return render_template('gestion_cliente.html', clientes=clientes, search_query=request.args.get('q', ''), form_data=request.form)

    # El controlador decide si busca filtrado o trae todos internamente
    clientes = ClienteController.obtener_datos_gestion(request.args.get('q'))
    return render_template('gestion_cliente.html', clientes=clientes, search_query=request.args.get('q', ''), form_data={})

@cliente_bp.post('/clientes/rapido')
@login_required
@role_required('Administrador', 'Secretario')
def crear_cliente_rapido():
    # Eliminación del antipatrón "Doble Viaje"
    success, message, cliente_data = ClienteController.crear_cliente_rapido(request.form)
    
    if not success:
        return jsonify({'success': False, 'message': message}), 400

    return jsonify({
        'success': True,
        'message': message,
        'cliente': cliente_data
    })