import json
from datetime import datetime
from backend.models.Usuario import Usuario
from backend.models.Cliente import Cliente
from backend.models.Equipo import Equipo
from backend.models.OrdenServicio import OrdenServicio
from backend.models.HistorialEstado import HistorialEstado
from database import db

class BackupService:
    @staticmethod
    def generate_backup_dict():
        """
        Serializa todas las tablas del sistema en un diccionario para backup.
        Excluye hashes de contraseñas por motivos de seguridad y usa yield_per para optimizar memoria.
        """
        backup_data = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "system": "TechFlow ITSM",
                "version": "1.0"
            },
            "usuarios": [],
            "clientes": [],
            "equipos": [],
            "ordenes_servicio": [],
            "historial_estados": []
        }
        
        # 1. Usuarios (Excluyendo contraseña)
        for u in Usuario.query.yield_per(100):
            backup_data["usuarios"].append({
                "id": u.id,
                "username": u.username,
                "nombre": u.nombre,
                "apellido": u.apellido,
                "rol_id": u.rol_id,
                "activo": u.activo,
                "intentos_fallidos": u.intentos_fallidos
            })
            
        # 2. Clientes
        for c in Cliente.query.yield_per(100):
            backup_data["clientes"].append({
                "id": c.id,
                "dni_cuil": c.dni_cuil,
                "nombre": c.nombre,
                "apellido": c.apellido,
                "telefono": c.telefono,
                "email": c.email,
                "domicilio": c.domicilio,
                "localidad": c.localidad
            })
            
        # 3. Equipos
        for e in Equipo.query.yield_per(100):
            backup_data["equipos"].append({
                "id": e.id,
                "cliente_id": e.cliente_id,
                "marca": e.marca,
                "modelo": e.modelo,
                "numero_serie": e.numero_serie,
                "tipo_id": e.tipo_id,
                "descripcion": e.descripcion
            })
            
        # 4. Ordenes de Servicio
        for o in OrdenServicio.query.yield_per(100):
            backup_data["ordenes_servicio"].append({
                "id": o.id,
                "usuario_id": o.usuario_id,
                "equipo_id": o.equipo_id,
                "falla_reportada": o.falla_reportada,
                "accesorios": o.accesorios,
                "estado": o.estado.name if o.estado else None,
                "estado_diagnostico": o.estado_diagnostico,
                "fecha_recepcion": o.fecha_recepcion.isoformat() if o.fecha_recepcion else None,
                "fecha_entrega": o.fecha_entrega.isoformat() if o.fecha_entrega else None,
                "costo": o.costo,
                "observaciones": o.observaciones
            })
            
        # 5. Historial de Estados
        for h in HistorialEstado.query.yield_per(100):
            backup_data["historial_estados"].append({
                "id": h.id,
                "orden_id": h.orden_id,
                "estado_anterior": h.estado_anterior,
                "estado_nuevo": h.estado_nuevo,
                "fecha_cambio": h.fecha_cambio.isoformat() if h.fecha_cambio else None,
                "usuario_id": h.usuario_id,
                "observacion_tecnica": h.observacion_tecnica
            })
            
        return backup_data

    @staticmethod
    def restore_backup(json_data):
        """
        Restaura de forma atómica y transaccional los datos desde un respaldo.
        Asigna una contraseña por defecto ('1234') a los usuarios al no exportarse sus hashes.
        Sincroniza todas las secuencias de PostgreSQL post-importación.
        """
        try:
            # 1. Limpieza en orden inverso de dependencias de llaves foráneas
            db.session.query(HistorialEstado).delete()
            db.session.query(OrdenServicio).delete()
            db.session.query(Equipo).delete()
            db.session.query(Cliente).delete()
            db.session.query(Usuario).delete()
            db.session.flush()
            
            # 2. Restaurar Usuarios (contraseña por defecto '1234')
            from werkzeug.security import generate_password_hash
            default_pass_hash = generate_password_hash('1234')
            
            for u in json_data.get("usuarios", []):
                nuevo_u = Usuario(
                    username=u["username"],
                    password='1234',  # se hashea automáticamente en el __init__
                    nombre=u["nombre"],
                    apellido=u["apellido"],
                    rol_id=u["rol_id"],
                    activo=u["activo"],
                    intentos_fallidos=u.get("intentos_fallidos", 0)
                )
                nuevo_u.id = u["id"]  # forzar ID original
                db.session.add(nuevo_u)
                
            # 3. Restaurar Clientes
            for c in json_data.get("clientes", []):
                nuevo_c = Cliente(
                    dni_cuil=c["dni_cuil"],
                    nombre=c["nombre"],
                    apellido=c["apellido"],
                    telefono=c["telefono"],
                    email=c["email"],
                    domicilio=c["domicilio"],
                    localidad=c["localidad"]
                )
                nuevo_c.id = c["id"]
                db.session.add(nuevo_c)
                
            # 4. Restaurar Equipos
            for e in json_data.get("equipos", []):
                nuevo_e = Equipo(
                    cliente_id=e["cliente_id"],
                    marca=e["marca"],
                    modelo=e["modelo"],
                    numero_serie=e["numero_serie"],
                    tipo_id=e["tipo_id"],
                    descripcion=e["descripcion"]
                )
                nuevo_e.id = e["id"]
                db.session.add(nuevo_e)
                
            # 5. Restaurar Ordenes de Servicio
            from backend.models.EstadoOrden import EstadoOrden
            for o in json_data.get("ordenes_servicio", []):
                estado_enum = EstadoOrden[o["estado"]] if o["estado"] else None
                fecha_rec = datetime.fromisoformat(o["fecha_recepcion"]) if o["fecha_recepcion"] else None
                fecha_ent = datetime.fromisoformat(o["fecha_entrega"]) if o["fecha_entrega"] else None
                
                nuevo_o = OrdenServicio(
                    equipo_id=o["equipo_id"],
                    usuario_id=o["usuario_id"],
                    falla_reportada=o["falla_reportada"],
                    accesorios=o["accesorios"],
                    costo=o["costo"]
                )
                nuevo_o.id = o["id"]
                nuevo_o.estado = estado_enum
                nuevo_o.estado_diagnostico = o["estado_diagnostico"]
                nuevo_o.fecha_recepcion = fecha_rec
                nuevo_o.fecha_entrega = fecha_ent
                nuevo_o.observaciones = o["observaciones"]
                db.session.add(nuevo_o)
                
            # 6. Restaurar Historial de Estados
            for h in json_data.get("historial_estados", []):
                fecha_ch = datetime.fromisoformat(h["fecha_cambio"]) if h["fecha_cambio"] else None
                nuevo_h = HistorialEstado(
                    orden_id=h["orden_id"],
                    estado_anterior=h["estado_anterior"],
                    estado_nuevo=h["estado_nuevo"],
                    usuario_id=h["usuario_id"],
                    observacion_tecnica=h["observacion_tecnica"]
                )
                nuevo_h.id = h["id"]
                nuevo_h.fecha_cambio = fecha_ch
                db.session.add(nuevo_h)
                
            db.session.flush()
            
            # 7. Sincronizar todas las secuencias en PostgreSQL
            from sqlalchemy import text
            seq_query = """
            SELECT 
                t.relname AS table_name,
                a.attname AS column_name,
                s.relname AS sequence_name
            FROM pg_class s
            JOIN pg_depend d ON d.objid = s.oid
            JOIN pg_class t ON d.refobjid = t.oid
            JOIN pg_attribute a ON (d.refobjid = a.attrelid AND d.refobjsubid = a.attnum)
            WHERE s.relkind = 'S'
            """
            sequences = db.session.execute(text(seq_query)).fetchall()
            for row in sequences:
                max_val = db.session.execute(text(f"SELECT COALESCE(MAX({row.column_name}), 0) FROM {row.table_name}")).scalar()
                if max_val > 0:
                    db.session.execute(text(f"SELECT setval('{row.sequence_name}', {max_val}, true)"))
                    
            db.session.commit()
            return True, "Base de datos restaurada correctamente y secuencias sincronizadas."
        except Exception as e:
            db.session.rollback()
            return False, f"Error al restaurar base de datos: {str(e)}"
