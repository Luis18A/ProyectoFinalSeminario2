from database import db
from backend.models import TipoDispositivo
import re

class TipoDispositivoController:

    @staticmethod
    def procesar_datos(datos_formulario):
        """Centraliza la extracción y validación de tipos de dispositivo."""
        descripcion = (datos_formulario.get('descripcion') or '').strip()
        
        if not descripcion:
            return False, "La descripción es obligatoria."
        
        # Validar longitud mínima/máxima para mayor robustez
        if len(descripcion) < 3 or len(descripcion) > 50:
            return False, "La descripción debe tener entre 3 y 50 caracteres."
            
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s0-9]+$", descripcion):
            return False, "La descripción solo debe contener letras, números y espacios."
            
        return True, {'descripcion': descripcion}

    @staticmethod
    def crear_tipo_rapido(datos_formulario):
        """Crea un tipo de dispositivo y lo devuelve formateado para AJAX."""
        success, result = TipoDispositivoController.procesar_datos(datos_formulario)
        if not success:
            return False, result, None

        if TipoDispositivo.get_por_descripcion_exacta(result['descripcion']):
            return False, f"El tipo '{result['descripcion']}' ya está registrado.", None

        try:
            nuevo = TipoDispositivo(**result)
            db.session.add(nuevo)
            db.session.commit()
            return True, "Tipo de dispositivo creado exitosamente.", {'id': nuevo.id, 'descripcion': nuevo.descripcion}
        except Exception:
            db.session.rollback()
            return False, "Error al guardar el tipo de dispositivo.", None

    @staticmethod
    def obtener_todos():
        return TipoDispositivo.get_all()