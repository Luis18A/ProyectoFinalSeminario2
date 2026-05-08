from flask import Flask, redirect, url_for
from flask_login import LoginManager
from backend.models import db, Usuario, RolUsuario, EstadoOrden

# 1. Configuración de la App
app = Flask(__name__, 
            template_folder='frontend/templates', 
            static_folder='frontend/static')
app.config['SECRET_KEY'] = 'una_clave_super_secreta_para_btech' # Cambiá esto en producción
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/btech_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Inicializar la Base de Datos
db.init_app(app)

# 3. Configuración del Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Si alguien sin sesión entra a una ruta protegida, lo manda acá
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

# 4. Registrar los Blueprints (Nuestras Rutas)
from backend.routes.auth import auth_bp
from backend.routes.crm import crm_bp
from backend.routes.taller import taller_bp

# Le decimos a Flask que use estas rutas
app.register_blueprint(auth_bp)
app.register_blueprint(crm_bp)
app.register_blueprint(taller_bp)

# 5. Ruta Principal (Dashboard / Redirección)
@app.route('/')
def index():
    # Cuando entran a btech.com, los mandamos directo a loguearse
    return redirect(url_for('auth.login'))

# 6. Crear las tablas al arrancar (Solo para desarrollo)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)