import re
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

from backend.models.Usuario import Usuario
from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from backend.models.HistorialEstado import HistorialEstado
from backend.models.EstadoOrden import EstadoOrden
from backend.models.Repuesto import Repuesto
from backend.models.OrdenRepuesto import OrdenRepuesto
from database import db
from sqlalchemy import text

# Claves requeridas en el JSON para validar antes de restaurar
_CLAVES_REQUERIDAS = {"usuarios", "clientes", "equipos", "ordenes_servicio", "historial_estados"}

class BackupService:

    @staticmethod
    def generate_backup_dict():
        """
        Serializa todas las tablas en un dict para exportar como JSON.
        Excluye hashes de contraseñas por seguridad.
        Usa yield_per(100) para no cargar toda la BD en memoria.
        """
        backup_data = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "system":        "TechFlow ITSM",
                "version":       "1.0",
            },
            "usuarios":          [],
            "clientes":          [],
            "equipos":           [],
            "ordenes_servicio":  [],
            "historial_estados": [],
        }

        for u in Usuario.query.yield_per(100):
            backup_data["usuarios"].append({
                "id":                u.id,
                "username":          u.username,
                "nombre":            u.nombre,
                "apellido":          u.apellido,
                "rol_id":            u.rol_id,
                "activo":            u.activo,
                "intentos_fallidos": u.intentos_fallidos,
            })

        for c in Cliente.query.yield_per(100):
            backup_data["clientes"].append({
                "id":        c.id,
                "dni_cuil":  c.dni_cuil,
                "nombre":    c.nombre,
                "apellido":  c.apellido,
                "telefono":  c.telefono,
                "email":     c.email,
                "domicilio": c.domicilio,
                "localidad": c.localidad,
            })

        for e in Equipo.query.yield_per(100):
            backup_data["equipos"].append({
                "id":           e.id,
                "cliente_id":   e.cliente_id,
                "marca":        e.marca,
                "modelo":       e.modelo,
                "numero_serie": e.numero_serie,
                "tipo_id":      e.tipo_id,
                "descripcion":  e.descripcion,
            })

        for o in OrdenServicio.query.yield_per(100):
            backup_data["ordenes_servicio"].append({
                "id":                 o.id,
                "usuario_id":         o.usuario_id,
                "equipo_id":          o.equipo_id,
                "falla_reportada":    o.falla_reportada,
                "accesorios":         o.accesorios,
                "estado":             o.estado.name if o.estado else None,
                "estado_diagnostico": o.estado_diagnostico,
                "fecha_recepcion":    o.fecha_recepcion.isoformat() if o.fecha_recepcion else None,
                "fecha_entrega":      o.fecha_entrega.isoformat() if o.fecha_entrega else None,
                "costo":              float(o.costo) if o.costo is not None else None,
                "repuestos":          o.repuestos or [],
                "observaciones":      o.observaciones,
            })

        for h in HistorialEstado.query.yield_per(100):
            backup_data["historial_estados"].append({
                "id":                  h.id,
                "orden_id":            h.orden_id,
                "estado_anterior":     h.estado_anterior,
                "estado_nuevo":        h.estado_nuevo,
                "fecha_cambio":        h.fecha_cambio.isoformat() if h.fecha_cambio else None,
                "usuario_id":          h.usuario_id,
                "observacion_tecnica": h.observacion_tecnica,
            })

        return backup_data

    @staticmethod
    def _validar_estructura_json(json_data):
        """
        Valida que el JSON de restore tenga las claves necesarias.
        Retorna (True, '') o (False, mensaje_error).
        """
        if not isinstance(json_data, dict):
            return False, "El archivo de backup no es un objeto JSON válido."
        faltantes = _CLAVES_REQUERIDAS - json_data.keys()
        if faltantes:
            return False, f"El backup está incompleto. Faltan secciones: {', '.join(faltantes)}."
        return True, ""

    @staticmethod
    def restore_backup(json_data):
        """
        Restaura la BD de forma atómica desde un dict de backup.
        Los usuarios recuperan contraseña por defecto 'TechFlow2024!' que deben cambiar.
        Sincroniza las secuencias de PostgreSQL al finalizar.
        """
        # CORRECCIÓN: validar estructura antes de tocar la BD
        valido, mensaje = BackupService._validar_estructura_json(json_data)
        if not valido:
            return False, mensaje

        try:
            # ── 1. Limpieza en orden inverso de FK ────────────────────────────
            db.session.query(HistorialEstado).delete()
            db.session.query(OrdenServicio).delete()
            db.session.query(Equipo).delete()
            db.session.query(Cliente).delete()
            db.session.query(Usuario).delete()
            db.session.flush()

            # ── 2. Usuarios con contraseña por defecto ─────────────────────────
            # CORRECCIÓN: hashear UNA sola vez y pasar el hash al constructor
            # (que ya no hashea internamente según la corrección de Usuario.py)
            password_defecto = Usuario.hashear_password('TechFlow2024!')

            for u in json_data.get("usuarios", []):
                nuevo_u = Usuario(
                    username=u["username"],
                    password=password_defecto,
                    nombre=u["nombre"],
                    apellido=u["apellido"],
                    rol_id=u["rol_id"],
                    activo=u["activo"],
                    intentos_fallidos=u.get("intentos_fallidos", 0),
                )
                nuevo_u.id = u["id"]
                db.session.add(nuevo_u)

            # ── 3. Clientes ───────────────────────────────────────────────────
            for c in json_data.get("clientes", []):
                nuevo_c = Cliente(
                    dni_cuil=c["dni_cuil"],
                    nombre=c["nombre"],
                    apellido=c["apellido"],
                    telefono=c["telefono"],
                    email=c.get("email"),
                    domicilio=c["domicilio"],
                    localidad=c["localidad"],
                )
                nuevo_c.id = c["id"]
                db.session.add(nuevo_c)

            # ── 4. Equipos ────────────────────────────────────────────────────
            for e in json_data.get("equipos", []):
                nuevo_e = Equipo(
                    cliente_id=e["cliente_id"],
                    marca=e["marca"],
                    modelo=e["modelo"],
                    numero_serie=e["numero_serie"],
                    tipo_id=e["tipo_id"],
                    descripcion=e.get("descripcion"),
                )
                nuevo_e.id = e["id"]
                db.session.add(nuevo_e)

            # ── 5. Órdenes de Servicio ────────────────────────────────────────
            for o in json_data.get("ordenes_servicio", []):
                estado_enum  = EstadoOrden[o["estado"]] if o.get("estado") else None
                fecha_rec    = datetime.fromisoformat(o["fecha_recepcion"]) if o.get("fecha_recepcion") else None
                fecha_ent    = datetime.fromisoformat(o["fecha_entrega"])   if o.get("fecha_entrega")   else None

                nuevo_o = OrdenServicio(
                    equipo_id=o["equipo_id"],
                    usuario_id=o["usuario_id"],
                    falla_reportada=o["falla_reportada"],
                    accesorios=o["accesorios"],
                    costo=o.get("costo")
                )
                nuevo_o.id               = o["id"]
                nuevo_o.estado           = estado_enum
                nuevo_o.estado_diagnostico = o.get("estado_diagnostico")
                nuevo_o.fecha_recepcion  = fecha_rec
                nuevo_o.fecha_entrega    = fecha_ent
                nuevo_o.observaciones    = o.get("observaciones")
                db.session.add(nuevo_o)
                db.session.flush()

                # Restaurar repuestos en la base de datos relacional
                repuestos_json = o.get("repuestos", [])
                for rep in repuestos_json:
                    titulo = rep.get('titulo') or rep.get('nombre')
                    if not titulo:
                        continue
                    precio = float(rep.get('precio') or 0.0)
                    tienda = rep.get('tienda') or 'Manual'

                    # Buscar o registrar repuesto en catálogo
                    rep_db = Repuesto.query.filter_by(descripcion=titulo).first()
                    if not rep_db:
                        codigo = f"REP-{uuid.uuid4().hex[:12].upper()}"
                        rep_db = Repuesto(
                            codigo=codigo,
                            descripcion=titulo,
                            categoria="Hardware",
                            precio_promedio=precio,
                            proveedor=tienda
                        )
                        db.session.add(rep_db)
                        db.session.flush()

                    # Asociar a la orden si no está ya asociado
                    existe_rel = OrdenRepuesto.query.filter_by(orden_id=nuevo_o.id, repuesto_id=rep_db.id).first()
                    if not existe_rel:
                        orden_rep = OrdenRepuesto(
                            orden_id=nuevo_o.id,
                            repuesto_id=rep_db.id,
                            cantidad=1,
                            precio_unitario=precio
                        )
                        db.session.add(orden_rep)

            # ── 6. Historial de Estados ───────────────────────────────────────
            for h in json_data.get("historial_estados", []):
                fecha_ch = datetime.fromisoformat(h["fecha_cambio"]) if h.get("fecha_cambio") else None
                nuevo_h  = HistorialEstado(
                    orden_id=h.get("orden_id"),
                    estado_anterior=h["estado_anterior"],
                    estado_nuevo=h["estado_nuevo"],
                    usuario_id=h["usuario_id"],
                    observacion_tecnica=h.get("observacion_tecnica"),
                )
                nuevo_h.id          = h["id"]
                nuevo_h.fecha_cambio = fecha_ch
                db.session.add(nuevo_h)

            db.session.flush()

            # ── 7. Sincronizar secuencias PostgreSQL ──────────────────────────
            # CORRECCIÓN: validar nombres con regex antes de usarlos en SQL dinámico
            # para eliminar el riesgo de SQL injection por nombres de secuencia maliciosos
            seq_query = text("""
                SELECT
                    t.relname  AS table_name,
                    a.attname  AS column_name,
                    s.relname  AS sequence_name
                FROM pg_class s
                JOIN pg_depend   d ON d.objid      = s.oid
                JOIN pg_class    t ON d.refobjid   = t.oid
                JOIN pg_attribute a ON (d.refobjid = a.attrelid AND d.refobjsubid = a.attnum)
                WHERE s.relkind = 'S'
            """)
            sequences = db.session.execute(seq_query).fetchall()

            nombre_seguro = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

            for row in sequences:
                # Solo procesar nombres que sean identificadores SQL válidos
                if not (nombre_seguro.match(row.table_name) and
                        nombre_seguro.match(row.column_name) and
                        nombre_seguro.match(row.sequence_name)):
                    continue

                max_val = db.session.execute(
                    text(f"SELECT COALESCE(MAX({row.column_name}), 0) FROM {row.table_name}")
                ).scalar()
                if max_val and max_val > 0:
                    db.session.execute(
                        text(f"SELECT setval('{row.sequence_name}', :val, true)"),
                        {"val": max_val}
                    )

            db.session.commit()
            return True, "Base de datos restaurada correctamente. Los usuarios deben cambiar su contraseña."

        except Exception:
            db.session.rollback()
            return False, "Error al restaurar la base de datos. Verificá que el archivo sea válido."