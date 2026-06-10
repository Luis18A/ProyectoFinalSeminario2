from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask import flash
from backend.models.Cliente import Cliente
from backend.controller.cliente_controller import ClienteController
from backend.utils.decorators import login_required, role_required

cliente_bp = Blueprint('clientes', __name__)

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
    termino = request.args.get('q', '').strip()
    if len(termino) < 2:
        return jsonify([])
    resultados = ClienteController.buscar_clientes_json(termino)
    return jsonify(resultados)

@cliente_bp.get('/clientes/verificar-dni/<dni>')
@login_required
def verificar_dni(dni):
    import re
    clean_dni = re.sub(r'[- ]', '', dni.strip())
    cliente = Cliente.get_por_dni(clean_dni)
    if cliente:
        return jsonify({
            'exists': True,
            'cliente': {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'telefono': cliente.telefono,
                'email': cliente.email or '',
                'domicilio': cliente.domicilio,
                'localidad': cliente.localidad,
                'dni_cuil': cliente.dni_cuil
            }
        })
    return jsonify({'exists': False})

@cliente_bp.route('/clientes', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Secretario')
def gestion_cliente():
    if request.method == 'POST':
        success, message = ClienteController.crear_cliente(request.form)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('clientes.gestion_cliente'))

    q = request.args.get('q', '').strip()
    if q:
        clientes = ClienteController.buscar_clientes(q)
    else:
        clientes = ClienteController.obtener_todos()
    return render_template('gestion_cliente.html', clientes=clientes, search_query=q)

@cliente_bp.post('/clientes/rapido')
@login_required
def crear_cliente_rapido():
    success, message = ClienteController.crear_cliente(request.form)
    if success:
        import re
        dni = re.sub(r'[- ]', '', request.form.get('dni', '').strip())
        cliente = Cliente.get_por_dni(dni)
        if not cliente:
            return jsonify({'success': False, 'message': 'Error al recuperar el cliente creado.'}), 500
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