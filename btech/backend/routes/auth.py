from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
# Importamos el cerebro de la autenticación
from backend.controllers import auth_controller

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya tiene la sesión abierta, lo mandamos al tablero de trabajo
    if current_user.is_authenticated:
        return redirect(url_for('taller.tickets'))
        
    if request.method == 'POST':
        # 1. Atajamos los datos del formulario web
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 2. Le preguntamos al controlador si son válidos
        usuario, mensaje_error = auth_controller.validar_login(username, password)
        
        # 3. Tomamos una decisión basada en la respuesta
        if usuario:
            login_user(usuario)
            return redirect(url_for('taller.tickets'))
        else:
            flash(mensaje_error, 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))