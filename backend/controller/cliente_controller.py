from backend.models.Cliente import Cliente
from database import db
from backend.models.Equipo import Equipo

class ClienteController:
    @staticmethod
    def crear_cliente(datos_formulario):
        try:
            dni = datos_formulario.get('dni')
            if not dni:
                return False, "El DNI es requerido."
                
            cliente_existente = Cliente.get_por_dni(dni)
            if cliente_existente:
                return False, f"El DNI/CUIL {dni} ya existe."
                
            Cliente.create(
                dni_cuil=dni,
                nombre=datos_formulario.get('nombre'),
                apellido=datos_formulario.get('apellido'),
                telefono=datos_formulario.get('telefono'),
                email=datos_formulario.get('email'),
                domicilio=datos_formulario.get('domicilio'),
                localidad=datos_formulario.get('localidad')
            )
            return True, "Cliente creado exitosamente."
        except Exception as e:
            return False, f"Error al crear el cliente: {str(e)}"

    @staticmethod
    def obtener_todos():
        return Cliente.get_all()

    @staticmethod
    def obtener_por_id(cliente_id):
        if cliente_id <=0:
            return False, "El ID del cliente es requerido."
        return Cliente.get_by_id(cliente_id)

    @staticmethod
    def obtener_por_dni(dni):
        return Cliente.get_por_dni(dni)

    @staticmethod
    def buscar_clientes(termino):
        """Busca clientes por nombre, apellido o DNI/CUIL."""
        return Cliente.query.filter(
            (Cliente.nombre.ilike(f"%{termino}%")) | 
            (Cliente.apellido.ilike(f"%{termino}%")) | 
            (Cliente.dni_cuil.ilike(f"%{termino}%"))
        ).all()

    @staticmethod
    def buscar_clientes_json(termino):
        """Busca clientes y retorna una lista de diccionarios JSON listos para responder en la ruta."""
        if not termino:
            return []
        clientes = ClienteController.buscar_clientes(termino)
        resultados = []
        for c in clientes:
            resultados.append({
                'id': c.id,
                'nombre': c.nombre,
                'apellido': c.apellido,
                'dni_cuil': c.dni_cuil,
                'telefono': c.telefono,
                'email': c.email,
                'domicilio': c.domicilio,
                'localidad': c.localidad
            })
        return resultados

    @staticmethod
    def editar_cliente(cliente_id, datos_formulario):
        try:
            cliente = Cliente.get_by_id(cliente_id)
            if not cliente:
                return False, "Cliente no encontrado."
                
            cliente.nombre = datos_formulario.get('nombre')
            cliente.apellido = datos_formulario.get('apellido')
            cliente.telefono = datos_formulario.get('telefono')
            cliente.email = datos_formulario.get('email')
            cliente.domicilio = datos_formulario.get('domicilio')
            cliente.localidad = datos_formulario.get('localidad')
            
            db.session.commit()
            return True, "Cliente actualizado exitosamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar el cliente: {str(e)}"

    def eliminar_cliente(cliente_id):
        cliente = Cliente.get_by_id(cliente_id)
        if cliente:
            cliente.delete()
            return True
        return False

    def obtener_equipos_cliente(cliente_id):
        return Equipo.obtener_por_cliente(cliente_id)