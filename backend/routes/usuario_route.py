from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.controller.usuario_controller import UsuarioController
from backend.utils.decorators import login_required, role_required

# Creamos el Blueprint para los usuarios
usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.get('/usuarios')
@login_required
@role_required('Administrador')
def listar_usuarios():
    data = UsuarioController.obtener_datos_gestion_usuarios()
    return render_template('gestion_usuarios.html', **data)

@usuarios_bp.post('/usuarios')
@login_required
@role_required('Administrador')
def crear_usuario():
    success, message = UsuarioController.crear_usuario(request.form)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/eliminar/<int:id>')
@login_required
@role_required('Administrador')
def eliminar_usuario(id):
    success, message = UsuarioController.eliminar_usuario(id, session.get('usuario_id'))
    flash(message, 'success' if success else 'error')
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/actualizar/<int:id>')
@login_required
@role_required('Administrador')
def actualizar_usuario(id):
    success, message = UsuarioController.actualizar_usuario(id, request.form)
    flash(message, 'success' if success else 'error')
    return redirect(url_for('usuarios.listar_usuarios'))