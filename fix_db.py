from app import app
from database import db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # 1. Cambiamos el tipo de dato de telefono a VARCHAR
            try:
                db.session.execute(text('ALTER TABLE cliente ALTER COLUMN telefono TYPE VARCHAR(20) USING telefono::varchar;'))
                db.session.commit()
                print("Columna 'telefono' ok.")
            except:
                db.session.rollback()

            # 2. Cambiamos el tipo de dato de dni_cuil a VARCHAR (por si era INTEGER)
            try:
                db.session.execute(text('ALTER TABLE cliente ALTER COLUMN dni_cuil TYPE VARCHAR(80) USING dni_cuil::varchar;'))
                db.session.commit()
                print("Columna 'dni_cuil' ok.")
            except:
                db.session.rollback()
                
            print("Migración completada.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    migrate()
