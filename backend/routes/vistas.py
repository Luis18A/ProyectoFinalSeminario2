from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.controller.auth_controller import AuthController
from backend.utils.decorators import login_required, role_required

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
def dashboard():
    from backend.controller.ordenServicio_controller import OrdenServicioController
    active_tickets, pending_repairs, revenue = OrdenServicioController.obtener_datos_dashboard()
    return render_template('dashboard_index.html', 
                           active_tickets=active_tickets,
                           pending_repairs=pending_repairs,
                           revenue=revenue)
