from database import db
from backend.models.Equipo import Equipo
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.Usuario import Usuario

class EquipoController:
    @staticmethod
    def crear_equipo(datos_formulario):
        try:
            equipo_existente = Equipo.obtener_por_numero_serie(datos_formulario.get('numero_serie'))
            if equipo_existente:
                return False, f"El número de serie {datos_formulario.get('numero_serie')} ya existe."
            Equipo.crear(
                cliente_id=int(datos_formulario.get('cliente_id')),
                tipo_dispositivo_id=int(datos_formulario.get('tipo_dispositivo_id')),
                marca=datos_formulario.get('marca'),
                modelo=datos_formulario.get('modelo'),
                numero_serie=datos_formulario.get('numero_serie'),
                descripcion=datos_formulario.get('descripcion'),
            )
        except Exception as e:
            return False, f"Error al crear el equipo: {str(e)}"

    @staticmethod
    def obtener_todos():
        return Equipo.obtener_todos()

    @staticmethod
    def toggle_estado(equipo_id):
        equipo = Equipo.obtener_por_id(equipo_id)
        if equipo:
            equipo.activo = not equipo.activo # Cambia de True a False y viceversa
            db.session.commit()
            return True
        return False

    @staticmethod
    def eliminar_equipo(equipo_id):
        equipo = Equipo.obtener_por_id(equipo_id)
        if equipo:
            equipo.eliminar()
            return True
        return False

    @staticmethod
    def actualizar_equipo(equipo_id, datos_formulario):
        equipo = Equipo.obtener_por_id(equipo_id)
        if equipo:
            equipo.nombre = datos_formulario.get('nombre')
            equipo.tipo_dispositivo_id = int(datos_formulario.get('tipo_dispositivo_id'))
            equipo.usuario_id = int(datos_formulario.get('usuario_id'))
            equipo.activo = True if datos_formulario.get('activo') else False
            db.session.commit()
            return True
        return False

    @staticmethod
    def obtener_por_id(equipo_id):
        return Equipo.obtener_por_id(equipo_id)

    @staticmethod
    def obtener_por_usuario(usuario_id):
        return Equipo.obtener_por_usuario(usuario_id)

    @staticmethod
    def buscar_equipos(termino):
        """Busca equipos por marca, modelo o número de serie."""
        return Equipo.query.filter(
            (Equipo.marca.ilike(f"%{termino}%")) | 
            (Equipo.modelo.ilike(f"%{termino}%")) | 
            (Equipo.numero_serie.ilike(f"%{termino}%"))
        ).all()
    
    #def obtener_equipos_cliente(cliente_id):
    #   return Equipo.query.filter_by(cliente_id=cliente_id).all()