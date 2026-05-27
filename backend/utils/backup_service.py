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
        
        # 1. Usuarios
        for u in Usuario.query.all():
            backup_data["usuarios"].append({
                "id": u.id,
                "username": u.username,
                "password": u.password,
                "nombre": u.nombre,
                "apellido": u.apellido,
                "rol_id": u.rol_id,
                "activo": u.activo,
                "intentos_fallidos": u.intentos_fallidos
            })
            
        # 2. Clientes
        for c in Cliente.query.all():
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
        for e in Equipo.query.all():
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
        for o in OrdenServicio.query.all():
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
        for h in HistorialEstado.query.all():
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
