from app import app
from database import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Intentamos agregar la columna direccion a la tabla cliente
            db.session.execute(text('ALTER TABLE cliente ADD COLUMN direccion VARCHAR(80);'))
            db.session.commit()
            print("Columna 'direccion' agregada exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error o la columna ya existe: {e}")

if __name__ == '__main__':
    migrate()
