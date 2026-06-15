from database import db
from backend.models.TipoDispositivo import TipoDispositivo

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
            
        return True, {'descripcion': descripcion}

    @staticmethod
    def crear_tipoDispositivo(datos_formulario):
        success, result = TipoDispositivoController.procesar_datos(datos_formulario)
        if not success:
            return False, result

        if TipoDispositivo.obtener_por_descripcion(result['descripcion']):
            return False, f"El tipo '{result['descripcion']}' ya está registrado."

        try:
            nuevo = TipoDispositivo(**result)
            db.session.add(nuevo)
            db.session.commit()
            return True, "Tipo de dispositivo creado exitosamente."
        except Exception:
            db.session.rollback()
            return False, "Error al guardar el tipo de dispositivo."

    @staticmethod
    def crear_tipo_rapido(datos_formulario):
        """Intenta crear y devuelve el objeto serializado en un solo viaje."""
        success, result = TipoDispositivoController.procesar_datos(datos_formulario)
        if not success:
            return False, result, None

        if TipoDispositivo.obtener_por_descripcion(result['descripcion']):
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
    def actualizar_tipoDispositivo(tipo_id, datos_formulario):
        tipo = TipoDispositivo.obtener_por_id(tipo_id)
        if not tipo:
            return False, "Tipo no encontrado."
            
        success, result = TipoDispositivoController.procesar_datos(datos_formulario)
        if not success:
            return False, result

        try:
            tipo.descripcion = result['descripcion']
            db.session.commit()
            return True, "Tipo actualizado exitosamente."
        except Exception:
            db.session.rollback()
            return False, "Error al actualizar el tipo."

    @staticmethod
    def obtener_todos():
        return TipoDispositivo.obtener_todos()

    @staticmethod
    def buscar(termino):
        return TipoDispositivo.get_por_descripcion(termino)
    
    @staticmethod
    def obtener_por_descripcion(descripcion):
        return TipoDispositivo.obtener_por_descripcion(descripcion)

    @staticmethod
    def eliminar_tipo_dispositivo(tipo_id):
        tipo = TipoDispositivo.obtener_por_id(tipo_id)
        if not tipo:
            return False
        try:
            db.session.delete(tipo)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False