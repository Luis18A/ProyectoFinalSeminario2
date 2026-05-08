#solo para inicializar la app y conectar la base de datos

from flask import Flask
from database import db

# Importar los modelos (ahora dentro de backend)
from backend.models.Usuario import Usuario
from backend.models.Rol import Rol
from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from backend.models.TipoDispositivo import TipoDispositivo

# Importar los Blueprints de las rutas (ahora dentro de backend)
from backend.routes.vistas import vistas_bp
from backend.routes.usuario_route import usuarios_bp

# Configurar Flask para que busque en la carpeta frontend
app = Flask(__name__, 
            template_folder='frontend/templates', 
            static_folder='frontend/static')


# CONEXIÓN A LA BASE DE DATOS
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:3536@localhost:5432/TechFlowDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# REGISTRO DE RUTAS (Blueprints)
app.register_blueprint(vistas_bp)
app.register_blueprint(usuarios_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
