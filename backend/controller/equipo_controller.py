from database import db
from backend.models.Equipo import Equipo
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.Usuario import Usuario

class EquipoController:
    @staticmethod
    def crear_equipo(datos_formulario):
        equipo_existente = Equipo.get_por_numero_serie(datos_formulario.get('numero_serie'))
        # Validaciones de negocio
        if not datos_formulario.get('numero_serie'):
            return False, "El número de serie no puede estar vacío."
        if not datos_formulario.get('marca'):
            return False, "La marca no puede estar vacía."
        if not datos_formulario.get('modelo'):
            return False, "El modelo no puede estar vacío."
        #si existe el equipo con el numero de serie, no se puede crear
        if equipo_existente:
            return False, f"El número de serie {datos_formulario.get('numero_serie')} ya existe."
       #creamos el equipo
        try:
            Equipo.crear(
                cliente_id=int(datos_formulario.get('cliente_id')),
                tipo_id=int(datos_formulario.get('tipo_dispositivo_id')),
                marca=datos_formulario.get('marca'),
                modelo=datos_formulario.get('modelo'),
                numero_serie=datos_formulario.get('numero_serie'),
                descripcion=datos_formulario.get('descripcion'),
            )
            return True, "Equipo creado exitosamente."
        except Exception as e:
            return False, f"Error al crear el equipo: {str(e)}"

    @staticmethod
    def obtener_todos():
        return Equipo.get_all()

    @staticmethod
    def toggle_estado(equipo_id):
        equipo = Equipo.get_by_id(equipo_id)
        if equipo:
            equipo.activo = not equipo.activo # Cambia de True a False y viceversa
            db.session.commit()
            return True
        return False

    @staticmethod
    def eliminar_equipo(equipo_id):
        equipo = Equipo.get_by_id(equipo_id)
        if equipo:
            equipo.eliminar()
            return True
        return False

    @staticmethod
    def editar_equipo(equipo_id, datos_formulario):
        try:
            equipo = Equipo.get_by_id(equipo_id)
            if not equipo:
                return False, "Equipo no encontrado."
            
            equipo.tipo_dispositivo_id = int(datos_formulario.get('tipo_dispositivo_id'))
            equipo.marca = datos_formulario.get('marca')
            equipo.modelo = datos_formulario.get('modelo')
            equipo.numero_serie = datos_formulario.get('numero_serie')
            equipo.descripcion = datos_formulario.get('descripcion')
            
            db.session.commit()
            return True, "Equipo actualizado exitosamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar el equipo: {str(e)}"

    @staticmethod
    def obtener_por_id(equipo_id):
        return Equipo.get_by_id(equipo_id)

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

    @staticmethod
    def obtener_datos_gestion(cliente_id):
        """Unifica las consultas de equipos y clientes para el panel de gestión de equipos."""
        from backend.controller.tipoDispositivo_controller import TipoDispositivoController
        from backend.models.Cliente import Cliente
        
        tipo_dispositivos = TipoDispositivoController.obtener_todos()
        cliente = None
        equipos = []

        if cliente_id:
            cliente = Cliente.query.get(cliente_id)
            if cliente:
                equipos = Equipo.get_por_cliente(cliente_id)
                
        return tipo_dispositivos, cliente, equipos