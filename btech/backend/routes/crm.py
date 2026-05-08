from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
# Importamos el cerebro del CRM
from backend.controllers import crm_controller
from backend.utils.decorators import role_required

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/clientes', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Secretaria')
def clientes():
    if request.method == 'POST':
        # 1. La ruta ataja los datos del formulario web
        dni_cuil = request.form.get('dni_cuil')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        direccion = request.form.get('direccion')

        # 2. Le pasa la pelota al controlador
        exito, mensaje = crm_controller.registrar_cliente(
            dni_cuil, nombre, apellido, telefono, email, direccion
        )

        # 3. Muestra el mensaje en pantalla según lo que dijo el controlador
        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('crm.clientes'))
        else:
            flash(mensaje, 'danger')

    # Si es GET, le pide la lista al controlador y dibuja el HTML
    lista_clientes = crm_controller.obtener_todos_los_clientes()
    return render_template('crm/clientes.html', clientes=lista_clientes)

@crm_bp.route('/cliente/<int:cliente_id>/equipos', methods=['GET', 'POST'])
@login_required
@role_required('Administrador','Secretaria','Tecnico')
def equipos_cliente(cliente_id):
    cliente_actual = crm_controller.obtener_cliente_por_id(cliente_id)

    if request.method == 'POST':
        exito, mensaje = crm_controller.registrar_equipo(
            cliente_id=cliente_actual.id,
            tipo=request.form.get('tipo'), # ¡Corregido! Ya no es tipo_id
            marca=request.form.get('marca'),
            modelo=request.form.get('modelo'),
            nro_serie=request.form.get('numero_serie'),
            descripcion=request.form.get('descripcion_general')
        )
        
        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('crm.equipos_cliente', cliente_id=cliente_actual.id))
        else:
            flash(mensaje, 'danger')

    lista_equipos = crm_controller.obtener_equipos_de_cliente(cliente_actual.id)
    tipos_disponibles = crm_controller.obtener_tipos_dispositivo()
    return render_template('crm/equipos.html', cliente=cliente_actual, equipos=lista_equipos, tipos=tipos_disponibles)