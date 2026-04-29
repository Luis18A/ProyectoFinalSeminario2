from flask import Blueprint, render_template, request, redirect, url_for
from backend.controller.auth_controller import AuthController

# Creamos el Blueprint para las vistas estáticas
vistas_bp = Blueprint('vistas', __name__)

@vistas_bp.route('/')
def login():
    return render_template('login_screen.html')

@vistas_bp.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('operator-id')
    password = request.form.get('passcode')
    
    # Delegamos al controlador para ver si es válido
    usuario_valido = AuthController.validar_login(username, password)
    
    if usuario_valido:
        # Si está bien, lo mandamos al dashboard
        return redirect(url_for('vistas.dashboard'))
    else:
        # Si falló, mostramos el login de nuevo con un mensaje de error
        return render_template('login_screen.html', error="Credenciales inválidas")

@vistas_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard_index.html')

@vistas_bp.route('/technician')
def technician():
    return render_template('technician_board.html')

@vistas_bp.route('/admin')
def admin():
    return render_template('admin_analytics.html')

@vistas_bp.route('/secretary')
def secretary():
    return render_template('secretary_view.html')
