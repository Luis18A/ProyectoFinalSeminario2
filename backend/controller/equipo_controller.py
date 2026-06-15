from database import db
from backend.models.Equipo import Equipo
from backend.models.TipoDispositivo import TipoDispositivo

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

        # ── 2. VALIDACIÓN DE CAMPOS OBLIGATORIOS ──
        if not datos['numero_serie']:
            return False, "El número de serie no puede estar vacío."
        if not datos['marca']:
            return False, "La marca no puede estar vacía."
        if not datos['modelo']:
            return False, "El modelo no puede estar vacío."

        # ── 3. VALIDACIÓN DE CLAVES FORÁNEAS (IDs) ──
        try:
            datos['tipo_id'] = int(datos_formulario.get('tipo_dispositivo_id'))
            # El cliente solo es necesario al crearlo, no al editarlo
            if not is_edit:
                datos['cliente_id'] = int(datos_formulario.get('cliente_id'))
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
            return True, "Equipo creado exitosamente."

        except Exception:
            db.session.rollback()
            return False, "Error al crear el equipo. Intentá de nuevo."

    @staticmethod
    def crear_equipo_rapido(datos_formulario):
        """Intenta crear el equipo y devuelve el DTO formateado en un solo viaje."""
        success, result = EquipoController.crear_equipo(datos_formulario)
        if not success:
            return False, result, None

        equipo = Equipo.get_por_numero_serie(datos_formulario.get('numero_serie'))
        if not equipo:
            return False, "Error al recuperar el equipo tras la creación.", None

        return True, result, {
            'id': equipo.id,
            'label': f"{equipo.marca} {equipo.modelo} (S/N: {equipo.numero_serie})"
        }

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
        if not equipo:
            return False
        try:
            db.session.delete(equipo)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def obtener_por_id(equipo_id):
        return Equipo.get_by_id(equipo_id)

    @staticmethod
    def obtener_por_usuario(usuario_id):
        return Equipo.obtener_por_usuario(usuario_id)

    @staticmethod
    def buscar_equipos(termino):
        return Equipo.query.filter(
            (Equipo.marca.ilike(f"%{termino}%")) | 
            (Equipo.modelo.ilike(f"%{termino}%")) | 
            (Equipo.numero_serie.ilike(f"%{termino}%"))
        ).limit(50).all()

    @staticmethod
    def obtener_por_numero_serie(numero_serie):
        return Equipo.get_por_numero_serie(numero_serie)

    @staticmethod
    def obtener_equipos_cliente_json(cliente_id):
        """Obtiene equipos de un cliente en formato JSON (para AJAX)."""
        from backend.models.Cliente import Cliente
        cliente = Cliente.get_by_id(cliente_id)
        if not cliente:
            return None
        equipos = Equipo.get_por_cliente(cliente_id)
        return [{
            'id': e.id,
            'label': f"{e.marca} {e.modelo} (S/N: {e.numero_serie})"
        } for e in equipos]
