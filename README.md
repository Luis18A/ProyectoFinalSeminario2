# TechFlow – Sistema de Gestión de Órdenes de Servicio

Sistema web para la gestión de órdenes de servicio técnico de dispositivos electrónicos. Permite registrar clientes, equipos, asignar técnicos y hacer seguimiento del estado de las reparaciones, con control de acceso por roles.

---

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Backend | Python + Flask |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy (Flask-SQLAlchemy) |
| Frontend | HTML + CSS + JS (Jinja2 templates) |
| Arquitectura | Blueprints (MVC) |

---

## Estructura del proyecto

```
ProyectoFinalSeminario2/
│
├── app.py                  # Punto de entrada: inicializa Flask, DB y registra rutas
├── create.py               # Script de inicialización: roles, usuarios y datos por defecto
├── database.py             # Instancia global de SQLAlchemy
├── requirements.txt        # Dependencias del proyecto
│
├── backend/
│   ├── models/             # Modelos de la base de datos (ORM)
│   │   ├── Usuario.py
│   │   ├── Rol.py
│   │   ├── Cliente.py
│   │   ├── Equipo.py
│   │   ├── OrdenServicio.py
│   │   └── TipoDispositivo.py
│   │
│   └── routes/             # Blueprints con las rutas de la aplicación
│       ├── vistas.py               # Rutas de renderizado de páginas
│       ├── usuario_route.py
│       ├── cliente_route.py
│       ├── equipo_route.py
│       ├── ordenServicio_route.py
│       └── tipoDispositivo_route.py
│
├── frontend/
│   ├── templates/          # Plantillas HTML (Jinja2)
│   └── static/             # Archivos estáticos (CSS, JS, imágenes)
│
├── apis/                   # Módulos de APIs externas o internas
├── scrappers/              # Scrapers de precios u otros datos
└── scratch/                # Archivos de prueba / borrador
```

---

## Requisitos previos

- Python 3.10 o superior
- PostgreSQL instalado y corriendo
- pip

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd ProyectoFinalSeminario2
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos en PostgreSQL

Abrir psql o pgAdmin y ejecutar:

```sql
CREATE DATABASE "TechFlowDB";
```

### 5. Configurar la conexión (si es necesario)

En `app.py`, verificar o modificar esta línea con tus credenciales:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/TechFlowDB'
```

### 6. Inicializar tablas y datos por defecto

Este script crea las tablas, los roles, los usuarios iniciales y los tipos de dispositivo:

```bash
python create.py
```

**Usuarios creados por defecto:**

| Usuario | Contraseña | Rol |
|---|---|---|
| admin | 1234 | Administrador |
| tecnico | 1234 | Técnico |
| secretario | 1234 | Secretario |

> ⚠️ Se recomienda cambiar las contraseñas antes de usar el sistema en producción.

---

## Ejecución

```bash
python app.py
```

La aplicación estará disponible en: [http://localhost:5000](http://localhost:5000)

---

## Funcionalidades principales

- **Gestión de clientes**: registro y administración de clientes
- **Gestión de equipos**: registro de dispositivos por tipo (Notebook, PC, Impresora, etc.)
- **Órdenes de servicio**: creación, asignación y seguimiento de reparaciones
- **Control de roles**: acceso diferenciado para Administrador, Técnico y Secretario
- **Manejo de errores**: redirección automática en rutas no encontradas (404) o sin permisos (403)

---

## Roles del sistema

| Rol | Descripción |
|---|---|
| Administrador | Acceso total al sistema |
| Técnico | Gestión de órdenes de servicio asignadas |
| Secretario | Registro de clientes y apertura de órdenes |

---

## Notas de desarrollo

- El archivo `database.py` contiene únicamente la instancia `db = SQLAlchemy()` para evitar imports circulares.
- Las tablas se crean automáticamente al iniciar la app gracias a `db.create_all()` dentro del contexto de aplicación.
- Los Blueprints separan las rutas por entidad para mantener el código organizado.
- La carpeta `scratch/` es de uso interno para pruebas y no forma parte del sistema productivo.
