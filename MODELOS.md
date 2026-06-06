# Documentación de Modelos – TechFlow

Este archivo describe todos los modelos de la base de datos del sistema, sus atributos, relaciones y métodos disponibles. Todos los modelos usan **Flask-SQLAlchemy** con el patrón **Active Record**.

---

## Índice

1. [Rol](#1-rol)
2. [Usuario](#2-usuario)
3. [Cliente](#3-cliente)
4. [TipoDispositivo](#4-tipodispositivo)
5. [Equipo](#5-equipo)
6. [EstadoOrden](#6-estadoorden)
7. [OrdenServicio](#7-ordenservicio)
8. [HistorialEstado](#8-historialestado)
9. [Diagrama de relaciones](#9-diagrama-de-relaciones)

---

## 1. Rol

**Archivo:** `backend/models/Rol.py`  
**Tabla:** `rol`

Define los roles de acceso del sistema. Cada usuario tiene exactamente un rol asignado.

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | Integer | PK, autoincremental | Identificador único |
| `descripcion` | String(80) | UNIQUE, NOT NULL | Nombre del rol (ej: "Administrador") |

### Relaciones

| Relación | Modelo | Tipo | Descripción |
|---|---|---|---|
| `usuarios` | Usuario | One-to-Many | Lista de usuarios con este rol |

### Roles disponibles en el sistema

- Administrador
- Técnico
- Secretario

---

## 2. Usuario

**Archivo:** `backend/models/Usuario.py`  
**Tabla:** `usuario`

Representa a los empleados del sistema. Las contraseñas se almacenan **siempre hasheadas** con `werkzeug.security`.

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | Integer | PK | Identificador único |
| `username` | String(80) | UNIQUE, NOT NULL | Nombre de usuario para login |
| `password` | String(255) | NOT NULL | Contraseña hasheada (nunca en texto plano) |
| `nombre` | String(80) | NOT NULL | Nombre del empleado |
| `apellido` | String(80) | NOT NULL | Apellido del empleado |
| `rol_id` | Integer | FK → rol.id | Rol asignado |
| `activo` | Boolean | NOT NULL, default=True | Si el usuario puede ingresar al sistema |
| `intentos_fallidos` | Integer | NOT NULL, default=0 | Contador de intentos de login fallidos |

### Métodos

| Método | Tipo | Descripción |
|---|---|---|
| `crear(...)` | classmethod | Crea y persiste un nuevo usuario (el hash se aplica automáticamente en `__init__`) |
| `obtener_todos()` | classmethod | Retorna todos los usuarios |
| `obtener_por_id(id)` | classmethod | Busca por ID |
| `actualizar(**kwargs)` | instancia | Actualiza campos; si se pasa `password`, la hashea antes de guardar |
| `verificar_password(password)` | instancia | Compara texto plano con el hash guardado. Retorna `True/False` |
| `eliminar()` | instancia | Elimina el usuario de la base de datos |
| `obtener_por_username(username)` | static | Busca por nombre de usuario (usado en login) |
| `obtener_por_nombre(nombre)` | static | Búsqueda parcial por nombre (LIKE) |
| `obtener_por_apellido(apellido)` | static | Búsqueda parcial por apellido (LIKE) |
| `obtener_por_rol(rol_id)` | static | Filtra usuarios por rol |
| `obtener_por_activo(activo)` | static | Filtra usuarios activos o inactivos |

> ⚠️ **Importante:** El `__init__` aplica `generate_password_hash()` automáticamente. Nunca llamar a `generate_password_hash()` manualmente antes de pasar la contraseña al constructor.

---

## 3. Cliente

**Archivo:** `backend/models/Cliente.py`  
**Tabla:** `cliente`

Representa a los clientes que traen equipos para reparar.

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | Integer | PK | Identificador único |
| `dni_cuil` | String(20) | UNIQUE, NOT NULL | DNI o CUIL del cliente |
| `nombre` | String(50) | NOT NULL | Nombre del cliente |
| `apellido` | String(50) | NOT NULL | Apellido del cliente |
| `telefono` | String(20) | NOT NULL | Número de contacto |
| `email` | String(254) | UNIQUE, NOT NULL | Correo electrónico |
| `domicilio` | String(150) | NOT NULL | Dirección |
| `localidad` | String(100) | NOT NULL | Ciudad o localidad |
| `fecha_registro` | DateTime | default=utcnow | Fecha de alta en el sistema |

### Relaciones

| Relación | Modelo | Tipo | Descripción |
|---|---|---|---|
| `equipos` | Equipo | One-to-Many | Equipos registrados a nombre de este cliente |

### Métodos

| Método | Tipo | Descripción |
|---|---|---|
| `get_all()` | static | Retorna todos los clientes |
| `get_by_id(id)` | static | Busca por ID |
| `create(**data)` | classmethod | Crea y persiste un nuevo cliente |
| `update_data(**data)` | instancia | Actualiza campos dinámicamente |
| `delete()` | instancia | Elimina el cliente |
| `get_por_dni(dni)` | static | Busca por DNI/CUIL exacto |
| `get_por_nombre_apellido(termino)` | static | Búsqueda parcial por nombre o apellido (LIKE) |
| `get_por_email(email)` | static | Busca por email exacto |

---

## 4. TipoDispositivo

**Archivo:** `backend/models/TipoDispositivo.py`  
**Tabla:** `tipo_dispositivo`

Catálogo de tipos de dispositivos que puede recibir el taller.

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | Integer | PK | Identificador único |
| `descripcion` | String(80) | UNIQUE, NOT NULL | Nombre del tipo (ej: "Notebook") |

### Tipos cargados por defecto

- Notebook
- PC Escritorio
- Impresora
- Servidor
- Consola

### Métodos

| Método | Tipo | Descripción |
|---|---|---|
| `obtener_todos()` | classmethod | Retorna todos los tipos |
| `crear(descripcion)` | classmethod | Crea y persiste un nuevo tipo |
| `obtener_por_id(id)` | classmethod | Busca por ID |
| `get_por_descripcion(termino)` | classmethod | Búsqueda parcial (LIKE) |
| `actualizar(id, descripcion)` | classmethod | Actualiza la descripción de un tipo existente |
| `eliminar(id)` | classmethod | Elimina un tipo. Retorna `True` si tuvo éxito |

---

## 5. Equipo

**Archivo:** `backend/models/Equipo.py`  
**Tabla:** `equipo`

Representa el dispositivo físico que ingresa al taller para ser reparado. Siempre pertenece a un cliente.

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | Integer | PK | Identificador único |
| `cliente_id` | Integer | FK → cliente.id, NOT NULL | Propietario del equipo |
| `marca` | String(80) | NOT NULL | Marca del dispositivo |
| `modelo` | String(80) | NOT NULL | Modelo del dispositivo |
| `numero_serie` | String(80) | UNIQUE, NOT NULL | Número de serie del equipo |
| `tipo_id` | Integer | FK → tipo_dispositivo.id | Tipo de dispositivo |
| `descripcion` | String(500) | nullable | Descripción adicional del equipo |

### Relaciones

| Relación | Modelo | Tipo | Descripción |
|---|---|---|---|
| `cliente` | Cliente | Many-to-One | Propietario del equipo |
| `tipo` | TipoDispositivo | Many-to-One | Categoría del dispositivo |

### Métodos

| Método | Tipo | Descripción |
|---|---|---|
| `get_all()` | static | Retorna todos los equipos |
| `get_by_id(id)` | static | Busca por ID |
| `crear(**data)` | classmethod | Crea y persiste un nuevo equipo |
| `update_data(**data)` | instancia | Actualiza campos dinámicamente |
| `delete()` | instancia | Elimina el equipo |
| `get_por_cliente(cliente_id)` | static | Lista equipos de un cliente |
| `get_por_numero_serie(numero_serie)` | static | Busca por número de serie exacto |

---

## 6. EstadoOrden

**Archivo:** `backend/models/EstadoOrden.py`  
**Tipo:** Enum (no es tabla de base de datos)

Define los estados posibles de una orden de servicio y las transiciones válidas entre ellos. Implementa una **máquina de estados**.

### Estados

| Estado | Valor | Descripción |
|---|---|---|
| `PENDIENTE` | "Pendiente" | Orden recién creada, sin iniciar |
| `DIAGNOSTICO` | "Diagnostico" | El técnico está evaluando el equipo |
| `PRESUPUESTADO` | "Presupuestado" | Se generó un presupuesto para el cliente |
| `REPARACION` | "Reparacion" | El equipo está siendo reparado |
| `LISTO` | "Listo" | Reparación terminada, esperando retiro |
| `ENTREGADO` | "Entregado" | El equipo fue devuelto al cliente |

### Transiciones permitidas

```
PENDIENTE → DIAGNOSTICO
DIAGNOSTICO → PRESUPUESTADO
PRESUPUESTADO → REPARACION | DIAGNOSTICO (puede volver si se rechaza el presupuesto)
REPARACION → LISTO | PRESUPUESTADO (puede volver si se necesita nuevo presupuesto)
LISTO → ENTREGADO
ENTREGADO → (ninguna, estado final)
```

### Métodos

| Método | Tipo | Descripción |
|---|---|---|
| `list()` | classmethod | Retorna lista de valores string de todos los estados |
| `transiciones_permitidas(estado_actual)` | classmethod | Retorna lista de estados a los que se puede avanzar desde el estado actual, incluyendo el estado actual al inicio |

---

## 7. OrdenServicio

**Archivo:** `backend/models/OrdenServicio.py`  
**Tabla:** `orden_servicio`

Modelo central del sistema. Registra cada trabajo de reparación, su estado, historial y costos. Contiene tanto lógica de negocio como métodos CRUD.

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | Integer | PK | Identificador único / número de orden |
| `usuario_id` | Integer | FK → usuario.id, NOT NULL | Técnico o empleado responsable |
| `equipo_id` | Integer | FK → equipo.id, NOT NULL | Equipo ingresado |
| `falla_reportada` | String(100) | NOT NULL | Descripción del problema según el cliente |
| `accesorios` | String(100) | NOT NULL | Accesorios entregados junto al equipo |
| `estado` | Enum(EstadoOrden) | NOT NULL, default=PENDIENTE | Estado actual de la orden |
| `estado_diagnostico` | String(255) | nullable | Diagnóstico técnico detallado |
| `fecha_recepcion` | DateTime | default=utcnow | Fecha de ingreso del equipo |
| `fecha_entrega` | DateTime | nullable | Fecha de entrega al cliente |
| `costo` | Float | nullable | Costo final de la reparación |
| `observaciones` | String(500) | nullable | Notas adicionales |
| `repuestos` | JSON | nullable, default=[] | Lista de repuestos utilizados |

### Relaciones

| Relación | Modelo | Tipo | Descripción |
|---|---|---|---|
| `usuario` | Usuario | Many-to-One | Empleado que gestiona la orden |
| `equipo` | Equipo | Many-to-One | Equipo en reparación |
| `historial` | HistorialEstado | One-to-Many | Registro de todos los cambios de estado |

### Métodos de negocio

| Método | Descripción |
|---|---|
| `actualizar_estado(nuevo_estado, usuario_id, observacion)` | Cambia el estado de la orden y registra automáticamente el movimiento en `HistorialEstado` |
| `finalizar_orden(costo_final, observaciones, usuario_id)` | Cierra la orden: registra el costo, la fecha de entrega y cambia el estado a `ENTREGADO` |
| `actualizar_diagnostico(diagnostico, usuario_id)` | Guarda el diagnóstico técnico detallado |

### Métodos CRUD

| Método | Tipo | Descripción |
|---|---|---|
| `get_all()` | static | Retorna todas las órdenes |
| `get_by_id(id)` | static | Busca por ID |
| `create(**data)` | classmethod | Crea y persiste una nueva orden |
| `update_data(**data)` | instancia | Actualiza campos dinámicamente |
| `delete()` | instancia | Elimina la orden |
| `get_por_usuario(usuario_id)` | static | Filtra órdenes por técnico asignado |
| `get_por_estado(estado)` | static | Filtra órdenes por estado |

---

## 8. HistorialEstado

**Archivo:** `backend/models/HistorialEstado.py`  
**Tabla:** `historial_estados`

Registra cada cambio de estado de una orden de servicio. Funciona como una **bitácora de auditoría**: nunca se modifica, solo se agrega.

### Atributos

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | Integer | PK | Identificador único del registro |
| `orden_id` | Integer | FK → orden_servicio.id, NOT NULL | Orden a la que pertenece |
| `estado_anterior` | String(50) | NOT NULL | Estado antes del cambio |
| `estado_nuevo` | String(50) | NOT NULL | Estado después del cambio |
| `fecha_cambio` | DateTime | default=utcnow | Fecha y hora exacta del cambio |
| `usuario_id` | Integer | FK → usuario.id, NOT NULL | Usuario que realizó el cambio |
| `observacion_tecnica` | Text | nullable | Nota técnica asociada al cambio |

### Relaciones

| Relación | Modelo | Tipo | Descripción |
|---|---|---|---|
| `usuario` | Usuario | Many-to-One | Quién realizó el cambio de estado |
| `orden` | OrdenServicio | Many-to-One | Backref definido en OrdenServicio |

### Métodos

| Método | Tipo | Descripción |
|---|---|---|
| `add_registro(orden_id, estado_anterior, estado_nuevo, usuario_id, observacion_tecnica)` | classmethod | Crea y persiste un nuevo registro en el historial |
| `get_historial_orden(orden_id)` | classmethod | Retorna todos los cambios de una orden |
| `get_historial_usuario(usuario_id)` | classmethod | Retorna todos los cambios realizados por un usuario |
| `get_historial_fecha(fecha_cambio)` | classmethod | Filtra registros por fecha exacta |
| `get_historial_tickets(orden_id)` | classmethod | Retorna el historial de una orden ordenado por fecha descendente (más reciente primero) |

> 📝 Este modelo es invocado automáticamente por `OrdenServicio.actualizar_estado()`. No es necesario llamarlo directamente en las rutas.

---

## 9. Diagrama de relaciones

```
Rol (1) ──────────────── (N) Usuario
                                │
                                │ usuario_id
                                ▼
Cliente (1) ──── (N) Equipo (1) ──── (N) OrdenServicio
                        │                      │
               tipo_id  │              historial│
                        ▼                      ▼
                TipoDispositivo        HistorialEstado
                                               │
                                       usuario_id
                                               ▼
                                           Usuario

EstadoOrden ──── (usado por) ──── OrdenServicio.estado
```

### Flujo principal de datos

```
1. Se registra un Cliente
2. Se registra un Equipo asociado al Cliente
3. Se crea una OrdenServicio para ese Equipo, asignada a un Usuario
4. La orden avanza por los estados definidos en EstadoOrden
5. Cada cambio de estado queda registrado en HistorialEstado
6. Al finalizar, se registra el costo y la fecha de entrega
```
