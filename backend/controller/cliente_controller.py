import re
from backend.models.Cliente import Cliente
from database import db
from backend.models.Equipo import Equipo

class ClienteController:
    @staticmethod
    def validar_cuit_cuil(cuit):
        """
        Valida el dígito verificador del algoritmo oficial de CUIT/CUIL para Argentina (11 dígitos).
        """
        # Limpiamos el string de cualquier guion o espacio
        cuit = re.sub(r'\D', '', str(cuit))
        
        if len(cuit) != 11 or not cuit.isdigit():
            return False
        
        multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        total = sum(int(cuit[i]) * multipliers[i] for i in range(10))
        remainder = total % 11
        
        check_digit = 11 - remainder
        if check_digit == 11:
            calculated = 0
        elif check_digit == 10:
            # En casos especiales de recalculo de CUIT en Argentina para evitar colisiones
            calculated = 9
        else:
            calculated = check_digit
            
        provided = int(cuit[10])
        # Se admite recalculo excepcional oficial que asigna 9 o 4 en residuo 10
        if check_digit == 10:
            return provided in (9, 4)
            
        return provided == calculated

    @staticmethod
    def validar_datos_cliente(datos_formulario, is_edit=False, cliente_id=None):
        nombre = datos_formulario.get('nombre', '').strip()
        apellido = datos_formulario.get('apellido', '').strip()
        telefono = datos_formulario.get('telefono', '').strip()
        email = datos_formulario.get('email', '').strip()
        domicilio = datos_formulario.get('domicilio', '').strip()
        localidad = datos_formulario.get('localidad', '').strip()

        # 1. Validación de Nombre y Apellido (Compuestos con guion y límites de longitud)
        if not nombre or len(nombre) < 2:
            return False, "El nombre debe tener al menos 2 caracteres."
        if len(nombre) > 50:
            return False, "El nombre es demasiado largo (máximo 50 caracteres)."
            
        if not apellido or len(apellido) < 2:
            return False, "El apellido debe tener al menos 2 caracteres."
        if len(apellido) > 50:
            return False, "El apellido es demasiado largo (máximo 50 caracteres)."
            
        # Permitir letras, espacios, apóstrofes y guiones (para compuestos)
        nombre_pattern = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$"
        if not re.match(nombre_pattern, nombre):
            return False, "El nombre solo debe contener letras, espacios o guiones."
        if not re.match(nombre_pattern, apellido):
            return False, "El apellido solo debe contener letras, espacios o guiones."

        # 2. Validación de DNI / CUIL (Longitudes fijas y Dígito Verificador oficial)
        if not is_edit:
            dni = datos_formulario.get('dni', '').strip()
            if not dni:
                return False, "El DNI/CUIL es requerido."
            clean_dni = re.sub(r'[- ]', '', dni)
            if not clean_dni.isdigit() or len(clean_dni) not in [7, 8, 11]:
                return False, "El DNI/CUIL debe contener exactamente 7, 8 u 11 números, sin letras."
            
            # Si es un CUIL/CUIT de 11 dígitos, se valida el dígito verificador matemático
            if len(clean_dni) == 11:
                if not ClienteController.validar_cuit_cuil(clean_dni):
                    return False, "El número de CUIL/CUIT no es válido. El dígito verificador es incorrecto."

        # 3. Validación de Teléfono (Rango neto entre 8 y 15 dígitos)
        if not telefono:
            return False, "El teléfono es requerido."
        if len(telefono) > 20:
            return False, "El teléfono es demasiado largo."
        clean_tel = re.sub(r'[-+ ]', '', telefono)
        if not clean_tel.isdigit() or not (8 <= len(clean_tel) <= 15):
            return False, "El teléfono debe contener entre 8 y 15 números netos."

        # 4. Validación de Correo Electrónico (Longitud máxima y unicidad real)
        if email:
            if len(email) > 254:
                return False, "El correo electrónico es demasiado largo (máximo 254 caracteres)."
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, email):
                return False, "El formato del correo electrónico no es válido (ej. correo@ejemplo.com)."
            
            # Validar Unicidad de Email
            existente = Cliente.query.filter_by(email=email).first()
            if not is_edit:
                if existente:
                    return False, "El correo electrónico ya está registrado por otro cliente."
            else:
                if existente and existente.id != cliente_id:
                    return False, "El correo electrónico ya está registrado por otro cliente."

        # 5. Validación de Domicilio (Al menos un carácter alfanumérico y límite)
        if not domicilio or len(domicilio) < 3:
            return False, "El domicilio debe tener al menos 3 caracteres."
        if len(domicilio) > 150:
            return False, "El domicilio es demasiado largo (máximo 150 caracteres)."
        if not re.search(r"[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ]", domicilio):
            return False, "El domicilio es inválido (debe contener letras o números)."

        # 6. Validación de Localidad (Patrón restrictivo y límites)
        if not localidad or len(localidad) < 2:
            return False, "La localidad debe tener al menos 2 caracteres."
        if len(localidad) > 100:
            return False, "La localidad es demasiado larga (máximo 100 caracteres)."
        localidad_pattern = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$"
        if not re.match(localidad_pattern, localidad):
            return False, "La localidad solo debe contener letras, espacios, guiones o apóstrofes."

        return True, ""

    @staticmethod
    def crear_cliente(datos_formulario):
        try:
            success, message = ClienteController.validar_datos_cliente(datos_formulario, is_edit=False)
            if not success:
                return False, message
                
            dni = re.sub(r'[- ]', '', datos_formulario.get('dni', '').strip())
            
            cliente_existente = Cliente.get_por_dni(dni)
            if cliente_existente:
                return False, f"El DNI/CUIL {dni} ya existe."
                
            Cliente.create(
                dni_cuil=dni,
                nombre=datos_formulario.get('nombre').strip().title(),
                apellido=datos_formulario.get('apellido').strip().title(),
                telefono=datos_formulario.get('telefono').strip(),
                email=datos_formulario.get('email').strip().lower(),
                domicilio=datos_formulario.get('domicilio').strip(),
                localidad=datos_formulario.get('localidad').strip()
            )
            return True, "Cliente creado exitosamente."
        except Exception as e:
            return False, f"Error al crear el cliente: {str(e)}"

    @staticmethod
    def obtener_todos():
        return Cliente.get_all()

    @staticmethod
    def obtener_por_id(cliente_id):
        if cliente_id <= 0:
            return False, "El ID del cliente es requerido."
        return Cliente.get_by_id(cliente_id)

    @staticmethod
    def obtener_por_dni(dni):
        return Cliente.get_por_dni(dni)

    @staticmethod
    def buscar_clientes(termino):
        """Busca clientes por nombre, apellido o DNI/CUIL con sanitización y límites."""
        termino = termino.strip()
        if not termino or len(termino) > 100:
            return []
        return Cliente.query.filter(
            (Cliente.nombre.ilike(f"%{termino}%")) | 
            (Cliente.apellido.ilike(f"%{termino}%")) | 
            (Cliente.dni_cuil.ilike(f"%{termino}%"))
        ).limit(20).all()

    @staticmethod
    def buscar_clientes_json(termino):
        """Busca clientes y retorna una lista de diccionarios JSON listos para responder en la ruta."""
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
                
            success, message = ClienteController.validar_datos_cliente(datos_formulario, is_edit=True, cliente_id=cliente_id)
            if not success:
                return False, message
                
            cliente.nombre = datos_formulario.get('nombre').strip().title()
            cliente.apellido = datos_formulario.get('apellido').strip().title()
            cliente.telefono = datos_formulario.get('telefono').strip()
            cliente.email = datos_formulario.get('email').strip().lower()
            cliente.domicilio = datos_formulario.get('domicilio').strip()
            cliente.localidad = datos_formulario.get('localidad').strip()
            
            db.session.commit()
            return True, "Cliente actualizado exitosamente."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al actualizar el cliente: {str(e)}"

    @staticmethod
    def eliminar_cliente(cliente_id):
        cliente = Cliente.get_by_id(cliente_id)
        if cliente:
            cliente.delete()
            return True
        return False

    @staticmethod
    def obtener_equipos_cliente(cliente_id):
        return Equipo.obtener_por_cliente(cliente_id)