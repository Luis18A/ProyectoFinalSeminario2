from datetime import datetime
from database import db
from backend.models.Usuario import Usuario
import re
from backend.models.Rol import Rol
from backend.models.HistorialEstado import HistorialEstado

class UsuarioController:

    @staticmethod
    def procesar_datos(datos_formulario, is_edit=False, usuario_id=None):
        """
        Extrae, sanitiza y valida las reglas de negocio del usuario.
        Retorna: (True, dict_con_datos_limpios) o (False, mensaje_de_error)
        """
        # ── 1. EXTRACCIÓN BLINDADA ──
        datos = {
            'username': (datos_formulario.get('username') or '').strip().lower(),
            'nombre': (datos_formulario.get('nombre') or '').strip(),
            'apellido': (datos_formulario.get('apellido') or '').strip(),
            'rol_id': datos_formulario.get('rol_id'),
            'activo': datos_formulario.get('activo') in [True, 'True', 'on', '1']
        }
        password_crudo = (datos_formulario.get('password') or '').strip()

        # ── 2. VALIDACIÓN DE CAMPOS OBLIGATORIOS, LONGITUD Y FORMATO ──
        if not datos['username']: return False, "El nombre de usuario es requerido."
        if len(datos['username']) > 80: return False, "El nombre de usuario no puede tener más de 80 caracteres."
        
        if not re.match(r"^[a-zA-Z0-9._\-]+$", datos['username']):
            return False, "El nombre de usuario solo debe contener letras, números, puntos, guiones y guiones bajos."

        if not datos['nombre']: return False, "El nombre es requerido."
        if len(datos['nombre']) > 80: return False, "El nombre no puede tener más de 80 caracteres."
        
        patron_texto = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'\-]+$"
        if not re.match(patron_texto, datos['nombre']):
            return False, "El nombre solo debe contener letras, espacios, guiones o apóstrofes."

        if not datos['apellido']: return False, "El apellido es requerido."
        if len(datos['apellido']) > 80: return False, "El apellido no puede tener más de 80 caracteres."
        if not re.match(patron_texto, datos['apellido']):
            return False, "El apellido solo debe contener letras, espacios, guiones o apóstrofes."

        if not datos['rol_id']: return False, "El rol es requerido."
        try:
            datos['rol_id'] = int(datos['rol_id'])
            if not db.session.get(Rol, datos['rol_id']):
                return False, "El rol asignado no existe."
        except (ValueError, TypeError):
            return False, "El rol provisto no es válido."

        # ── 3. UNICIDAD DE USERNAME ──
        existente = Usuario.get_por_username(datos['username'])
        if existente and (not is_edit or existente.id != usuario_id):
            return False, "El nombre de usuario ya está en uso."

        # ── 4. MANEJO DE CONTRASEÑA Y HASHING ──
        try:
            if not is_edit:
                if not password_crudo:
                    return False, "La contraseña es requerida para un nuevo usuario."
                datos['password'] = Usuario.hashear_password(password_crudo)
            else:
                if password_crudo:  # Solo se actualiza si se envió una nueva
                    datos['password'] = Usuario.hashear_password(password_crudo)
        except ValueError as e:
            # Captura validaciones de longitud desde el modelo (ej. pass muy corto)
            return False, str(e)

        return True, datos

    @staticmethod
    def crear_usuario(datos_formulario):
        try:
            success, result = UsuarioController.procesar_datos(datos_formulario, is_edit=False)
            if not success:
                return False, result # result es el mensaje de error

            # Desempaquetado limpio directamente al modelo
            nuevo_usuario = Usuario(**result)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return True, "Usuario creado correctamente."
        except Exception:
            db.session.rollback()
            return False, "Error al crear el usuario. Intentá de nuevo."


    @staticmethod
    def actualizar_usuario(usuario_id, datos_formulario):
        try:
            usuario = Usuario.get_by_id(usuario_id)
            if not usuario:
                return False, "Usuario no encontrado."

            success, result = UsuarioController.procesar_datos(
                datos_formulario, is_edit=True, usuario_id=usuario_id
            )
            if not success:
                return False, result

            # Actualizamos los campos desde el diccionario sanitizado
            usuario.username = result['username']
            usuario.nombre   = result['nombre']
            usuario.apellido = result['apellido']
            usuario.rol_id   = result['rol_id']
            usuario.activo   = result['activo']

            if 'password' in result:
                usuario.password = result['password']

            db.session.commit()
            return True, "Usuario actualizado correctamente."
        
        except Exception:
            db.session.rollback()
            return False, "Error al actualizar el usuario. Intentá de nuevo."

    @staticmethod
    def obtener_todos():
        return Usuario.get_all()

    @staticmethod
    def toggle_estado(usuario_id):
        usuario = Usuario.get_by_id(usuario_id)
        if not usuario:
            return False
        usuario.activo = not usuario.activo
        db.session.commit()
        return True

    @staticmethod
    def eliminar_usuario(usuario_id, usuario_actual_id):
        if usuario_id == usuario_actual_id:
            return False, "No puedes eliminar tu propia cuenta."
        usuario = Usuario.get_by_id(usuario_id)
        if not usuario:
            return False, "Usuario no encontrado."
        try:
            db.session.delete(usuario)
            db.session.commit()
            return True, "Usuario eliminado correctamente."
        except Exception:
            db.session.rollback()
            return False, "Error al eliminar el usuario."

    @staticmethod
    def obtener_datos_gestion_usuarios():
        usuarios_lista = Usuario.get_all()
        roles_lista = Rol.get_all()
        
        # Lógica de auditoría movida desde la ruta
        last_audit = HistorialEstado.query.order_by(HistorialEstado.fecha_cambio.desc()).first()
        tiempo_auditoria = "Sin registros"
        
        if last_audit:
            diff = datetime.now() - last_audit.fecha_cambio
            if diff.days > 0: tiempo_auditoria = f"Hace {diff.days}d"
            elif diff.seconds // 3600 > 0: tiempo_auditoria = f"Hace {diff.seconds // 3600}h"
            else: tiempo_auditoria = "Hace instantes"

        return {
            'usuarios': usuarios_lista,
            'roles': roles_lista,
            'cant_activos': sum(1 for u in usuarios_lista if u.activo),
            'cant_roles': len(roles_lista),
            'tiempo_auditoria': tiempo_auditoria,
            'cant_usuarios': Usuario.query.count()
        }