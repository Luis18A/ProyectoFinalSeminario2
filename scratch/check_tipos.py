from app import app
from backend.models.TipoDispositivo import TipoDispositivo

with app.app_context():
    tipos = TipoDispositivo.obtener_todos()
    print(f"Total tipos de dispositivo: {len(tipos)}")
    for t in tipos:
        print(f"ID: {t.id}, Descripcion: {t.descripcion}")
