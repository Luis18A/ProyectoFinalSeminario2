from flask import Blueprint, render_template, request, redirect, url_for
from backend.controller.usuario_controller import UsuarioController

# Creamos el Blueprint para los usuarios
usuarios_bp = Blueprint('usuarios', __name__)

'''@usuarios_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    # Le pedimos al controlador los datos puros
    usuarios_lista = UsuarioController.obtener_todos()
    
    # La ruta renderiza la vista (presentación) inyectando los datos
    return render_template('gestion_usuarios.html', usuarios=usuarios_lista)
'''
@usuarios_bp.get('/usuarios')
def listar_usuarios():
    usuarios_lista = UsuarioController.obtener_todos()
    return render_template('gestion_usuarios.html', usuarios=usuarios_lista)

@usuarios_bp.post('/usuarios')
def crear_usuario():
    # Le delegamos la lógica de negocio al controlador, enviando el request.form
    UsuarioController.crear_usuario(request.form)
    
    # El router redirige de vuelta a la función listar_usuarios
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/eliminar/<int:id>')
def eliminar_usuario(id):
    UsuarioController.eliminar_usuario(id)
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.post('/usuarios/actualizar/<int:id>')
def actualizar_usuario(id):
    UsuarioController.actualizar_usuario(id, request.form)
    return redirect(url_for('usuarios.listar_usuarios'))