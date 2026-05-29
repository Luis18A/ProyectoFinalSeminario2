from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask import flash
from backend.models.Cliente import Cliente
from backend.controller.cliente_controller import ClienteController
from backend.utils.decorators import login_required, role_required

cliente_bp = Blueprint('clientes', __name__)

@cliente_bp.post('/clientes')
@login_required
def crear_cliente():
    success, message = ClienteController.crear_cliente(request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('clientes.gestion_cliente'))

@cliente_bp.post('/clientes/editar/<int:id>')
@login_required
def editar_cliente(id):
    success, message = ClienteController.editar_cliente(id, request.form)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('clientes.gestion_cliente'))

@cliente_bp.get('/listar_clientes')
@login_required
def listar_clientes():
    return render_template('clientes.html')

@cliente_bp.get('/clientes/buscar')
@login_required
def buscar_clientes():
    termino = request.args.get('q', '')
    resultados = ClienteController.buscar_clientes_json(termino)
    return jsonify(resultados)

@cliente_bp.route('/clientes')
@login_required
@role_required('Administrador', 'Administrdor', 'Secretario', 'Secretaria')
def gestion_cliente():
    clientes = ClienteController.obtener_todos()
    return render_template('gestion_cliente.html', clientes=clientes)

@cliente_bp.post('/clientes/rapido')
@login_required
def crear_cliente_rapido():
    success, message = ClienteController.crear_cliente(request.form)
    if success:
        dni = request.form.get('dni')
        cliente = Cliente.get_por_dni(dni)
        return jsonify({
            'success': True,
            'message': message,
            'cliente': {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'dni_cuil': cliente.dni_cuil
            }
        })
    else:
        return jsonify({'success': False, 'message': message}), 400