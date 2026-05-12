from database import db
from backend.models.TipoDispositivo import TipoDispositivo

class TipoDispositivoController:
    @staticmethod
    def crear_tipoDispositivo(datos_formulario):
        # 1. Extraer y limpiar datos
        descripcion = datos_formulario.get('descripcion', '').strip()
        
        # 2. Validaciones de lógica de negocio
        if not descripcion:
            return False, "La descripción es obligatoria."
        
        # 3. Control de duplicados
        # Usamos una búsqueda exacta para validar si ya existe
        existente = TipoDispositivo.obtener_todos()
        for dispositivo in existente:
            if dispositivo.descripcion.lower() == descripcion.lower():
                return False, f"El tipo '{descripcion}' ya está registrado."
        
        # 4. Intentar la creación
        try:
            TipoDispositivo.crear(descripcion=descripcion)
            return True, "Tipo de dispositivo creado exitosamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error técnico al guardar: {str(e)}"

    @staticmethod
    def obtener_todos():
        return TipoDispositivo.obtener_todos()

    @staticmethod
    def buscar(termino):
        return TipoDispositivo.buscar_por_descripcion(termino)

    @staticmethod
    def eliminar_tipo_dispositivo(tipo_dispositivo_id):
        tipo_dispositivo = TipoDispositivo.obtener_por_id(tipo_dispositivo_id)
        if tipo_dispositivo:
            tipo_dispositivo.eliminar()
            return True
        return False

    @staticmethod
    def actualizar_tipoDispositivo(tipoDispositivo_id, datos_formulario):
        tipoDispositivo = TipoDispositivo.obtener_por_id(tipoDispositivo_id)
        if tipoDispositivo:
            tipoDispositivo.descripcion = datos_formulario.get('descripcion')
            #tipoDispositivo.activo = True if datos_formulario.get('activo') else False
            db.session.commit()
            return True
        return False
