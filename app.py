from flask import Flask, render_template, request, redirect, url_for
from database import db

# Importar los modelos
from models.Usuario import Usuario
from models.Rol import Rol
from models.Cliente import Cliente
from models.Equipo import Equipo
from models.OrdenServicio import OrdenServicio
from models.TipoDispositivo import TipoDispositivo

app = Flask(__name__)

# CONEXIÓN A LA BASE DE DATOS
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:3536@localhost:5432/TechFlowDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# RUTAS
@app.route('/')
def login():
    return render_template('login_screen.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard_index.html')

@app.route('/technician')
def technician():
    return render_template('technician_board.html')

@app.route('/admin')
def admin():
    return render_template('admin_analytics.html')

@app.route('/secretary')
def secretary():
    return render_template('secretary_view.html')

@app.route('/usuarios', methods=['GET', 'POST'])
def gestion_usuarios():
    # 1. Método CREAR (Cuando el formulario hace un POST)
    if request.method == 'POST':
        Usuario.crear(
            username=request.form.get('username'),
            password=request.form.get('password'),
            nombre=request.form.get('nombre'),
            apellido=request.form.get('apellido'),
            rol_id=request.form.get('rol_id'),
            activo=True if request.form.get('activo') else False
        )
        return redirect(url_for('gestion_usuarios'))
        
    # 2. Método LISTAR (Cuando se carga la página por GET)
    usuarios_lista = Usuario.obtener_todos()
    return render_template('gestion_usuarios.html', usuarios=usuarios_lista)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
