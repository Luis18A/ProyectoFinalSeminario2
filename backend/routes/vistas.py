from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.controller.auth_controller import AuthController
from backend.utils.decorators import login_required, role_required
from backend.controller.usuario_controller import UsuarioController

# Creamos el Blueprint para las vistas estáticas
vistas_bp = Blueprint('vistas', __name__)

# ─── Auth ────────────────────────────────────────────────────────────────────

@vistas_bp.route('/')
def login():
    return render_template('login.html')

@vistas_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    usuario_valido, mensaje = AuthController.validar_login(username, password)

    if usuario_valido:
        session['usuario_id'] = usuario_valido.id
        session['username']   = usuario_valido.username
        try:
            session['rol_descripcion'] = usuario_valido.rol.descripcion
        except Exception:
            session['rol_descripcion'] = ''
        session['real_rol_descripcion'] = session.get('rol_descripcion', '')
        return redirect(url_for('vistas.dashboard'))
    else:
        return render_template('login.html', error=mensaje)

@vistas_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('vistas.login'))

# ─── Vistas generales ────────────────────────────────────────────────────────

@vistas_bp.route('/dashboard')
@login_required
@role_required('Administrador', 'Administrdor')
def dashboard():
    datos = UsuarioController.obtener_datos_analytics()
    return render_template('admin_analytics.html', **datos)
