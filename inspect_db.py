from app import app
from database import db
from sqlalchemy import text

def inspect_columns():
    with app.app_context():
        try:
            # Consultamos los nombres de las columnas de la tabla cliente
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'cliente';
            """))
            print("Columnas encontradas en la tabla 'cliente':")
            for row in result:
                print(f"- {row[0]} ({row[1]}), Nullable: {row[2]}")
        except Exception as e:
            print(f"Error al inspeccionar: {e}")

if __name__ == '__main__':
    inspect_columns()
