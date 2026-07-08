from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from backend.controller import auth_controller, analytics_controller, orden_servicio_controller, search_controller
from backend.utils.decorators import login_required, role_required, _redirect_por_rol

vistas_bp = Blueprint('vistas', __name__)

# ─── Autenticación ───────────────────────────────────────────────────────────

@vistas_bp.get('/')
def login():
    if 'usuario_id' in session:
        return _redirect_por_rol(session.get('rol_descripcion', ''))
    return render_template('auth/login.html')

@vistas_bp.post('/login')
def login_post():
    session.clear()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    success, data_or_error = auth_controller.validar_login_completo(username, password)

    if not success:
        return render_template('auth/login.html', error=data_or_error)

    session['usuario_id']           = data_or_error['id']
    session['username']             = data_or_error['username']
    session['rol_descripcion']      = data_or_error['rol']
    session['real_rol_descripcion'] = data_or_error['rol']

    return _redirect_por_rol(data_or_error['rol'])

@vistas_bp.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('vistas.login'))

# ─── Dashboard ───────────────────────────────────────────────────────────────

@vistas_bp.get('/dashboard')
@login_required
@role_required('Administrador')
def dashboard():
    return render_template('admin_analytics.html', **analytics_controller.obtener_datos_analytics())

@vistas_bp.get('/secretary')
@login_required
@role_required('Secretario', 'Administrador')
def secretary():
    return redirect(url_for('orden_servicio.listar_ordenes_view'))

@vistas_bp.get('/technician')
@login_required
@role_required('Técnico', 'Administrador')
def technician():
    return render_template('technician_board.html', **orden_servicio_controller.obtener_tablero_tecnico(session.get('usuario_id')))

@vistas_bp.get('/api/global-search')
@login_required
def global_search():
    rol = session.get('rol_descripcion')
    resultados = search_controller.buscar_global(request.args.get('q', '').strip())
    if rol == 'Técnico':
        resultados['clientes'] = []
        resultados['equipos'] = []
    return jsonify(resultados)
