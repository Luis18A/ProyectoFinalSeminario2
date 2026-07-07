from database import db
from backend.models.Equipo import Equipo
from backend.models.TipoDispositivo import TipoDispositivo
from backend.models.Cliente import Cliente

class EquipoController:
    @staticmethod
    def procesar_datos(datos_formulario, is_edit=False, equipo_id=None):
        # ── 1. EXTRACCIÓN BLINDADA ──
        datos = {
            'numero_serie': (datos_formulario.get('numero_serie') or '').strip().upper(),
            'marca': (datos_formulario.get('marca') or '').strip(),
            'modelo': (datos_formulario.get('modelo') or '').strip(),
            'descripcion': (datos_formulario.get('descripcion') or '').strip() or None,
        }

        # ── 2. VALIDACIÓN DE CAMPOS OBLIGATORIOS Y LONGITUD ──
        import re

        if not datos['numero_serie']:
            return False, "El número de serie no puede estar vacío."
        if len(datos['numero_serie']) > 80:
            return False, "El número de serie no puede tener más de 80 caracteres."
        patron_serial = r"^[a-zA-Z0-9][a-zA-Z0-9\s\-\.\/_]*$"
        if not re.match(patron_serial, datos['numero_serie']):
            return False, "El número de serie contiene caracteres no permitidos o no comienza con una letra/número."
        if not re.search(r"[a-zA-Z0-9]", datos['numero_serie']):
            return False, "El número de serie debe contener al menos una letra o número."

        if not datos['marca']:
            return False, "La marca no puede estar vacía."
        if len(datos['marca']) > 80:
            return False, "La marca no puede tener más de 80 caracteres."
        patron_marca_modelo = r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ][a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\-\.\+\/()\"]*$"
        if not re.match(patron_marca_modelo, datos['marca']):
            return False, "La marca contiene caracteres no permitidos o no comienza con una letra/número."
        if not re.search(r"[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ]", datos['marca']):
            return False, "La marca debe contener al menos una letra o número."

        if not datos['modelo']:
            return False, "El modelo no puede estar vacío."
        if len(datos['modelo']) > 80:
            return False, "El modelo no puede tener más de 80 caracteres."
        if not re.match(patron_marca_modelo, datos['modelo']):
            return False, "El modelo contiene caracteres no permitidos o no comienza con una letra/número."
        if not re.search(r"[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ]", datos['modelo']):
            return False, "El modelo debe contener al menos una letra o número."

        if datos['descripcion']:
            if len(datos['descripcion']) > 500:
                return False, "La descripción no puede tener más de 500 caracteres."
            patron_desc = r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s'\",\.\-\+\/()#\?!:;*%=\$@&º°_]+$"
            if not re.match(patron_desc, datos['descripcion']):
                return False, "La descripción contiene caracteres no permitidos."

        # ── 3. VALIDACIÓN DE CLAVES FORÁNEAS (IDs) ──
        try:
            datos['tipo_id'] = int(datos_formulario.get('tipo_dispositivo_id'))
            if not db.session.get(TipoDispositivo, datos['tipo_id']):
                return False, "El tipo de dispositivo asignado no existe."

            # El cliente solo es necesario al crearlo, no al editarlo
            if not is_edit:
                datos['cliente_id'] = int(datos_formulario.get('cliente_id'))
                if not db.session.get(Cliente, datos['cliente_id']):
                    return False, "El cliente asignado no existe."
        except (TypeError, ValueError):
            return False, "Datos de cliente o tipo de dispositivo inválidos."

        # ── 4. VALIDACIÓN DE UNICIDAD (NÚMERO DE SERIE) ──
        existente = Equipo.get_por_numero_serie(datos['numero_serie'])
        if existente and (not is_edit or existente.id != equipo_id):
            return False, f"El número de serie {datos['numero_serie']} ya se encuentra registrado."

        return True, datos

    @staticmethod
    def crear_equipo(datos_formulario):
        try:
            success, result = EquipoController.procesar_datos(datos_formulario, is_edit=False)
            if not success:
                return False, result # result contiene el mensaje de error

            # Código limpio: Desempaquetado del diccionario validado
            nuevo = Equipo(**result)
            
            db.session.add(nuevo)
            db.session.commit()
            return True, nuevo

        except Exception:
            db.session.rollback()
            return False, "Error al crear el equipo. Intentá de nuevo."

    @staticmethod
    def editar_equipo(equipo_id, datos_formulario):
        try:
            equipo = Equipo.get_by_id(equipo_id)
            if not equipo:
                return False, "Equipo no encontrado."

            success, result = EquipoController.procesar_datos(
                datos_formulario, is_edit=True, equipo_id=equipo_id
            )
            if not success:
                return False, result

            # Actualizamos mapeando los campos desde el diccionario sanitizado
            equipo.tipo_id      = result['tipo_id']
            equipo.marca        = result['marca']
            equipo.modelo       = result['modelo']
            equipo.numero_serie = result['numero_serie']
            equipo.descripcion  = result['descripcion']

            db.session.commit()
            return True, "Equipo actualizado exitosamente."

        except Exception:
            db.session.rollback()
            return False, "Error al actualizar el equipo. Intentá de nuevo."

    @staticmethod
    def obtener_equipos_cliente_json(cliente_id):
        """Obtiene equipos de un cliente en formato JSON (para AJAX)."""
        cliente = Cliente.get_by_id(cliente_id)
        if not cliente:
            return None
        equipos = Equipo.get_por_cliente(cliente_id)
        return [{
            'id': e.id,
            'label': f"{e.marca} {e.modelo} (S/N: {e.numero_serie})"
        } for e in equipos]

    @staticmethod
    def obtener_datos_gestion_cliente(cliente_id):
        """Unifica las consultas para el panel de gestión mediante delegación."""
        tipo_dispositivos = TipoDispositivo.get_all()
        cliente = db.session.get(Cliente, cliente_id) if cliente_id else None
        equipos = Equipo.get_por_cliente(cliente_id) if cliente else []
        return tipo_dispositivos, cliente, equipos
