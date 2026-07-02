import re
from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from database import db

class ClienteController:
    @staticmethod
    def validar_cuit_cuil(cuit):
        """Valida el dígito verificador del algoritmo oficial de CUIT/CUIL para Argentina."""
        cuit = re.sub(r'\D', '', str(cuit))
        if len(cuit) != 11 or not cuit.isdigit():
            return False
        
        multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        total = sum(int(cuit[i]) * multipliers[i] for i in range(10))
        remainder = total % 11
        
        check_digit = 11 - remainder
        if check_digit == 11: calculated = 0
        elif check_digit == 10: calculated = 9
        else: calculated = check_digit
            
        provided = int(cuit[10])
        if check_digit == 10: return provided in (9, 4)
        return provided == calculated

    @staticmethod
    def procesar_datos(datos_formulario, is_edit=False, cliente_id=None):
        """
        Extrae, sanitiza y valida todas las reglas de negocio.
        Retorna: (True, dict_con_datos_limpios) o (False, mensaje_de_error)
        """
        # ── 1. EXTRACCIÓN Y SANITIZACIÓN ÚNICA (DRY) ──
        datos = {
            'nombre': (datos_formulario.get('nombre') or '').strip().title(),
            'apellido': (datos_formulario.get('apellido') or '').strip().title(),
            'telefono': (datos_formulario.get('telefono') or '').strip(),
            'email': (datos_formulario.get('email') or '').strip().lower() or None,
            'domicilio': (datos_formulario.get('domicilio') or '').strip(),
            'localidad': (datos_formulario.get('localidad') or '').strip(),
        }

        # ── 2. VALIDACIÓN DE NOMBRE Y APELLIDO ──
        if not datos['nombre'] or len(datos['nombre']) < 2: return False, "El nombre debe tener al menos 2 caracteres."
        if len(datos['nombre']) > 50: return False, "El nombre es demasiado largo."
        if not datos['apellido'] or len(datos['apellido']) < 2: return False, "El apellido debe tener al menos 2 caracteres."
        if len(datos['apellido']) > 50: return False, "El apellido es demasiado largo."
        
        patron_texto = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$"
        if not re.match(patron_texto, datos['nombre']): return False, "El nombre solo debe contener letras, espacios o guiones."
        if not re.match(patron_texto, datos['apellido']): return False, "El apellido solo debe contener letras, espacios o guiones."

        # ── 3. VALIDACIÓN DE DNI / CUIL Y SU UNICIDAD ──
        if not is_edit:
            dni_crudo = (datos_formulario.get('dni') or '').strip()
            if not dni_crudo: return False, "El DNI/CUIL es requerido."
            
            clean_dni = re.sub(r'[\.\- ]', '', dni_crudo)
            if not clean_dni.isdigit(): return False, "El documento solo debe contener números."
            
            longitud = len(clean_dni)
            if not (6 <= longitud <= 8) and longitud != 11:
                return False, "El DNI debe tener entre 6 y 8 números, o exactamente 11 para CUIL/CUIT."
            
            if longitud == 11:
                prefijo = clean_dni[:2]
                if prefijo not in ['20', '23', '24', '27', '30', '33', '34']:
                    return False, f"El prefijo '{prefijo}' no es válido para un CUIL/CUIT argentino."
                if not ClienteController.validar_cuit_cuil(clean_dni):
                    return False, "El número de CUIL/CUIT no es válido (Dígito verificador incorrecto)."
            
            # Cohesión: La unicidad del DNI se evalúa aquí mismo
            if Cliente.get_por_dni(clean_dni):
                return False, f"El DNI/CUIL {clean_dni} ya se encuentra registrado en el sistema."
            
            datos['dni_cuil'] = clean_dni

        # ── 4. VALIDACIÓN DE TELÉFONO ──
        if not datos['telefono']: return False, "El teléfono es requerido."
        if len(datos['telefono']) > 20: return False, "El teléfono es demasiado largo."
        clean_tel = re.sub(r'[-+ ]', '', datos['telefono'])
        if not clean_tel.isdigit() or not (8 <= len(clean_tel) <= 15):
            return False, "El teléfono debe contener entre 8 y 15 números netos."

        # ── 5. VALIDACIÓN Y UNICIDAD DE EMAIL ──
        if datos['email']:
            if len(datos['email']) > 254: return False, "El correo electrónico es demasiado largo."
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", datos['email']):
                return False, "El formato del correo electrónico no es válido."
            
            existente = Cliente.query.filter_by(email=datos['email']).first()
            if existente and (not is_edit or existente.id != cliente_id):
                return False, "El correo electrónico ya está registrado por otro cliente."

        # ── 6. VALIDACIÓN DE DOMICILIO Y LOCALIDAD ──
        if not datos['domicilio'] or len(datos['domicilio']) < 3: return False, "El domicilio debe tener al menos 3 caracteres."
        if len(datos['domicilio']) > 150: return False, "El domicilio es demasiado largo."
        if not re.search(r"[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ]", datos['domicilio']): return False, "El domicilio es inválido."
        
        if not datos['localidad'] or len(datos['localidad']) < 2: return False, "La localidad debe tener al menos 2 caracteres."
        if len(datos['localidad']) > 100: return False, "La localidad es demasiado larga."
        if not re.match(patron_texto, datos['localidad']): return False, "La localidad contiene caracteres inválidos."

        # Retornamos True y el diccionario listo para usar
        return True, datos

    @staticmethod
    def crear_cliente(datos_formulario):
        try:
            success, result = ClienteController.procesar_datos(datos_formulario, is_edit=False)
            if not success:
                return False, result # result contiene el mensaje de error

            # Código ultra limpio: desempaquetamos el diccionario validado directamente en el modelo
            nuevo = Cliente(**result)
            
            db.session.add(nuevo)
            db.session.commit()
            return True, "Cliente creado exitosamente."

        except Exception:
            db.session.rollback()
            return False, "Error al crear el cliente. Intentá de nuevo."

    @staticmethod
    def editar_cliente(cliente_id, datos_formulario):
        try:
            cliente = Cliente.get_by_id(cliente_id)
            if not cliente:
                return False, "Cliente no encontrado."

            success, result = ClienteController.procesar_datos(
                datos_formulario, is_edit=True, cliente_id=cliente_id
            )
            if not success:
                return False, result

            # Actualizamos usando el diccionario sanitizado (no pisamos el DNI porque no se edita)
            cliente.nombre    = result['nombre']
            cliente.apellido  = result['apellido']
            cliente.telefono  = result['telefono']
            cliente.email     = result['email']
            cliente.domicilio = result['domicilio']
            cliente.localidad = result['localidad']

            db.session.commit()
            return True, "Cliente actualizado exitosamente."

        except Exception:
            db.session.rollback()
            return False, "Error al actualizar el cliente. Intentá de nuevo."

    @staticmethod
    def obtener_todos():
        return Cliente.get_all()

    @staticmethod
    def obtener_por_id(cliente_id):
        if not cliente_id or cliente_id <= 0:
            return None
        return Cliente.get_by_id(cliente_id)

    @staticmethod
    def obtener_por_dni(dni):
        return Cliente.get_por_dni(dni)

    @staticmethod
    def buscar_clientes(termino):
        termino = (termino or '').strip()
        if not termino or len(termino) > 100:
            return []
        return Cliente.query.filter(
            (Cliente.nombre.ilike(f"%{termino}%")) | 
            (Cliente.apellido.ilike(f"%{termino}%")) | 
            (Cliente.dni_cuil.ilike(f"%{termino}%"))
        ).order_by(Cliente.fecha_registro.desc()).limit(20).all()

    @staticmethod
    def buscar_clientes_json(termino):
        return [
            {
                'id':        c.id,
                'nombre':    c.nombre,
                'apellido':  c.apellido,
                'dni_cuil':  c.dni_cuil,
                'telefono':  c.telefono,
                'email':     c.email,
                'domicilio': c.domicilio,
                'localidad': c.localidad,
            }
            for c in ClienteController.buscar_clientes(termino)
        ]

    @staticmethod
    def verificar_dni(dni):
        """Verifica si un cliente existe por DNI y devuelve el DTO correspondiente."""
        cliente = Cliente.get_por_dni(dni)
        if not cliente:
            return False, None
        return True, {
            'id': cliente.id, 'nombre': cliente.nombre, 'apellido': cliente.apellido,
            'telefono': cliente.telefono, 'email': cliente.email or '',
            'domicilio': cliente.domicilio, 'localidad': cliente.localidad,
            'dni_cuil': cliente.dni_cuil
        }

    @staticmethod
    def obtener_datos_gestion(q):
        """Busca clientes si q existe, de lo contrario obtiene todos."""
        q = (q or '').strip()
        if q:
            return ClienteController.buscar_clientes(q)
        return ClienteController.obtener_todos()

    @staticmethod
    def crear_cliente_rapido(datos_formulario):
        """Intenta crear un cliente y devuelve el DTO en un único viaje."""
        success, result = ClienteController.crear_cliente(datos_formulario)
        if not success:
            return False, result, None
            
        dni = (datos_formulario.get('dni') or '').strip()
        clean_dni = re.sub(r'[\.\- ]', '', dni)
        cliente = Cliente.get_por_dni(clean_dni)
        if not cliente:
            return False, "Error al recuperar el cliente tras la creación.", None
            
        return True, result, {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'apellido': cliente.apellido,
            'dni_cuil': cliente.dni_cuil
        }

    @staticmethod
    def eliminar_cliente(cliente_id):
        cliente = Cliente.get_by_id(cliente_id)
        if not cliente:
            return False
        try:
            db.session.delete(cliente)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def obtener_equipos_cliente(cliente_id):
        return Equipo.obtener_por_cliente(cliente_id)