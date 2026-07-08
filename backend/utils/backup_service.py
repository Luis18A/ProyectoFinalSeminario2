import os
import subprocess
import tempfile
import shutil
from urllib.parse import urlparse
import logging
from flask import current_app
from database import FALLBACK_DATABASE_URL

logger = logging.getLogger(__name__)

def find_pg_binary(binary_name):
    """Busca un binario de PostgreSQL en el PATH o en directorios comunes en Windows."""
    # 1. Intentar buscar en el PATH del sistema (funciona en Linux/Render y sistemas configurados)
    path = shutil.which(binary_name)
    if path:
        return path
        
    # 2. Si es Windows y no está en el PATH, buscar en carpetas de instalación estándar
    if os.name == 'nt':
        common_bases = [
            r"C:\Program Files\PostgreSQL",
            r"C:\Program Files (x86)\PostgreSQL"
        ]
        for base in common_bases:
            if os.path.exists(base):
                try:
                    # Listar las carpetas de versiones en orden descendente (ej: 18, 17, 16...)
                    versions = sorted(os.listdir(base), key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else 0, reverse=True)
                    for v in versions:
                        bin_path = os.path.join(base, v, "bin", f"{binary_name}.exe")
                        if os.path.exists(bin_path):
                            logger.info(f"[Backup] Detectado binario local de Postgres: {bin_path}")
                            return bin_path
                except Exception:
                    pass
                    
    # 3. Retornar el nombre plano si falla la autodetectación
    return binary_name

def obtener_datos_conexion():
    db_url = None
    try:
        # Intentar obtener de la configuración activa de Flask
        db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    except RuntimeError:
        # Fuera del contexto de aplicación de Flask (ej. scripts de prueba/CLI)
        pass
        
    if not db_url:
        db_url = os.environ.get('DATABASE_URL', FALLBACK_DATABASE_URL)
        
    parsed = urlparse(db_url)
    return {
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/')
    }

class BackupService:
    @staticmethod
    def generate_backup_dump():
        """Genera un archivo dump físico de la base de datos PostgreSQL usando pg_dump."""
        conn = obtener_datos_conexion()
        
        # Encontrar la ruta de pg_dump
        pg_dump_path = find_pg_binary('pg_dump')
        
        # Crear un archivo temporal para escribir el backup
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".dump")
        temp_file.close()
        
        # Configurar la contraseña de forma segura en las variables del proceso
        env = os.environ.copy()
        env['PGPASSWORD'] = conn['password']
        
        # Comando para pg_dump
        command = [
            pg_dump_path,
            '-h', conn['host'],
            '-p', str(conn['port']),
            '-U', conn['user'],
            '-F', 'c',             # Formato "custom" comprimido de Postgres
            '-b',                 # Incluye grandes objetos (blobs)
            '-f', temp_file.name,  # Archivo de salida
            conn['database']
        ]
        
        try:
            # Ejecutar el comando en el sistema operativo
            subprocess.run(command, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"[Backup] pg_dump completado exitosamente: {temp_file.name}")
            return temp_file.name # Retorna la ruta física del archivo generado
        except subprocess.CalledProcessError as e:
            # Si falla, borrar el temporal y lanzar el error
            if os.path.exists(temp_file.name):
                try:
                    os.remove(temp_file.name)
                except Exception:
                    pass
            err_msg = e.stderr.decode('utf-8', errors='ignore')
            logger.error(f"[Backup] Error en pg_dump: {err_msg}")
            raise RuntimeError(f"Error en pg_dump: {err_msg}")

    @staticmethod
    def restore_backup_dump(filepath):
        """Restaura un archivo dump físico en la base de datos PostgreSQL usando pg_restore."""
        conn = obtener_datos_conexion()
        
        # Encontrar la ruta de pg_restore
        pg_restore_path = find_pg_binary('pg_restore')
        
        env = os.environ.copy()
        env['PGPASSWORD'] = conn['password']
        
        # Comando para pg_restore
        command = [
            pg_restore_path,
            '-h', conn['host'],
            '-p', str(conn['port']),
            '-U', conn['user'],
            '-d', conn['database'],
            '--clean',       # Elimina las tablas existentes antes de recrearlas
            '--if-exists',   # Evita errores si alguna tabla no existía previamente
            filepath         # Ruta del archivo .dump cargado
        ]
        
        try:
            subprocess.run(command, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"[Backup] pg_restore completado exitosamente para {filepath}")
            return True, "Base de datos restaurada correctamente."
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode('utf-8', errors='ignore')
            logger.error(f"[Backup] Error en pg_restore: {err_msg}")
            return False, f"Error en pg_restore: {err_msg}"