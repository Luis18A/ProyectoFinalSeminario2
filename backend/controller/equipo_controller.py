from database import db
from backend.models.Equipo import Equipo
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.Usuario import Usuario

class EquipoController:
    @staticmethod
    def crear_equipo(datos_formulario):
        num_serie = datos_formulario.get('numero_serie', '').strip().upper()
        # Validaciones de negocio
        if not num_serie:
            return False, "El número de serie no puede estar vacío."
        if not datos_formulario.get('marca'):
            return False, "La marca no puede estar vacía."
        if not datos_formulario.get('modelo'):
            return False, "El modelo no puede estar vacío."
            
        equipo_existente = Equipo.get_por_numero_serie(num_serie)
        # si existe el equipo con el numero de serie, no se puede crear
        if equipo_existente:
            return False, f"El número de serie {num_serie} ya existe."
            
        try:
            cliente_id = int(datos_formulario.get('cliente_id'))
            tipo_id = int(datos_formulario.get('tipo_dispositivo_id'))
        except (TypeError, ValueError):
            return False, "Datos de cliente o tipo de dispositivo inválidos."
            
        # creamos el equipo
        try:
            Equipo.crear(
                cliente_id=cliente_id,
                tipo_id=tipo_id,
                marca=datos_formulario.get('marca'),
                modelo=datos_formulario.get('modelo'),
                numero_serie=num_serie,
                descripcion=datos_formulario.get('descripcion'),
            )
            return True, "Equipo creado exitosamente."
        except Exception as e:
            db.session.rollback()
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
        num_serie = datos_formulario.get('numero_serie', '').strip().upper()
        if not num_serie:
            return False, "El número de serie no puede estar vacío."
        if not datos_formulario.get('marca'):
            return False, "La marca no puede estar vacía."
        if not datos_formulario.get('modelo'):
            return False, "El modelo no puede estar vacío."

        try:
            tipo_id = int(datos_formulario.get('tipo_dispositivo_id'))
        except (TypeError, ValueError):
            return False, "Datos de tipo de dispositivo inválidos."

        try:
            equipo = Equipo.get_by_id(equipo_id)
            if not equipo:
                return False, "Equipo no encontrado."
            
            # Verificar que el número de serie no esté duplicado en otro equipo
            equipo_existente = Equipo.get_por_numero_serie(num_serie)
            if equipo_existente and equipo_existente.id != equipo_id:
                return False, f"El número de serie {num_serie} ya está registrado en otro equipo."
            
            equipo.tipo_dispositivo_id = tipo_id
            equipo.marca = datos_formulario.get('marca')
            equipo.modelo = datos_formulario.get('modelo')
            equipo.numero_serie = num_serie
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
        ).limit(50).all()

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

    @staticmethod
    def obtener_por_numero_serie(numero_serie):
        return Equipo.get_por_numero_serie(numero_serie)